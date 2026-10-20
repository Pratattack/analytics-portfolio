"""Audited retrospective intervention-screen stability study; no causal savings estimate."""
import argparse, csv, io, zipfile, json, math, random, sqlite3, statistics, sys
from collections import defaultdict, Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research_support import write_csv,write_json,digest,plot_bars,report,table
from applications import build_application
BASE=Path(__file__).resolve().parent
NUM=['arr_flights','arr_del15','carrier_ct','weather_ct','nas_ct','security_ct','late_aircraft_ct','arr_cancelled','arr_diverted','arr_delay','carrier_delay','weather_delay','nas_delay','security_delay','late_aircraft_delay']

def load(config):
    raw=list(csv.DictReader(io.StringIO(zipfile.ZipFile(BASE/'data/raw/bts_export.zip').read('Airline_Delay_Cause.csv').decode('utf-8-sig'))))
    keys=set();valid=[];issues=[]
    for line,r in enumerate(raw,2):
        key=(int(r['year']),int(r['month']),r['carrier'],r['airport'])
        assert key not in keys,('duplicate source key',key)
        keys.add(key);row={'year':key[0],'month':key[1],'carrier':key[2],'airport':key[3],'carrier_name':r['carrier_name'],'airport_name':r['airport_name'],'source_row':line}
        reasons=[]
        for k in NUM:
            try: row[k]=float(r[k]);assert math.isfinite(row[k]) and row[k]>=0
            except (ValueError,AssertionError):reasons.append('missing_or_invalid_'+k)
        if not reasons:
            d=row['arr_delay']-sum(row[k] for k in ['carrier_delay','weather_delay','nas_delay','security_delay','late_aircraft_delay'])
            c=row['arr_del15']-sum(row[k] for k in ['carrier_ct','weather_ct','nas_ct','security_ct','late_aircraft_ct'])
            if abs(d)>config['delay_minutes_reconciliation_tolerance']:reasons.append('delay_minutes_do_not_reconcile')
            if abs(c)>config['cause_count_reconciliation_tolerance']:reasons.append('cause_counts_do_not_reconcile')
            if row['arr_del15']+row['arr_cancelled']+row['arr_diverted']>row['arr_flights']+.01:reasons.append('flight_disposition_exceeds_total')
            if row['arr_flights']==0:reasons.append('zero_exposure')
        if reasons:issues.append({'source_row':line,'year':key[0],'month':key[1],'carrier':key[2],'airport':key[3],'reasons':';'.join(reasons)})
        else:valid.append(row)
    assert {r['year']*12+r['month'] for r in valid}==set(range(2024*12+1,2026*12+9))
    return raw,valid,issues

def warehouse(rows):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    keys=list(rows[0]);db.execute('CREATE TABLE valid ('+','.join(k+(' REAL' if k in NUM else ' INTEGER' if k in ['year','month','source_row'] else ' TEXT') for k in keys)+')')
    db.executemany('INSERT INTO valid VALUES ('+','.join('?' for _ in keys)+')',[[r[k] for k in keys] for r in rows])
    cfg=json.loads((BASE/'config.json').read_text())
    db.execute('CREATE TABLE thresholds (minimum_peer_carriers INTEGER,minimum_peer_flights REAL)')
    db.execute('INSERT INTO thresholds VALUES (?,?)',(cfg['minimum_peer_carriers'],cfg['minimum_peer_flights']))
    db.executescript((BASE/'analysis.sql').read_text())
    return db

def summaries(rows,year,months):
    groups=defaultdict(list)
    for r in rows:
        if r['year']==year and r['month'] in months:groups[(r['carrier'],r['airport'])].append(r)
    return {k:{'carrier':k[0],'airport':k[1],'months':len(g),'flights':sum(r['arr_flights'] for r in g),'carrier_minutes':sum(r['carrier_delay'] for r in g),'excess_minutes':sum(r['excess_minutes'] for r in g)} for k,g in groups.items()}

def select(cohort,metric,slots,cap):
    counts=Counter();picks=[]
    for k,v in sorted(cohort.items(),key=lambda kv:(-kv[1][metric],kv[0])):
        if v[metric]<=0:continue
        if counts[k[1]]<cap and len(picks)<slots:picks.append(k);counts[k[1]]+=1
    return picks

def evaluate(rows,picks,pool,year,months):
    totals=summaries(rows,year,months)
    denominator=sum(max(0,totals[k]['excess_minutes']) for k in pool if k in totals)
    captured=sum(max(0,totals[k]['excess_minutes']) for k in picks if k in totals)
    signed=sum(totals[k]['excess_minutes'] for k in picks if k in totals)
    flights=sum(totals[k]['flights'] for k in picks if k in totals)
    return {'year':year,'slots_observed':sum(k in totals for k in picks),'eligible_pool_observed':sum(k in totals for k in pool),'positive_excess_capture_pct':100*captured/denominator if denominator else 0,'signed_excess_minutes':signed,'flights':flights,'excess_minutes_per_flight':signed/flights if flights else 0}

def bootstrap(rows,picks,baseline,pool,year,config):
    # Circular two-month blocks preserve local dependence; only eight months: exploratory.
    rng=random.Random(config['bootstrap_seed']);values=[];months=config['months']
    cells={(r['carrier'],r['airport'],r['month']):r['excess_minutes'] for r in rows if r['year']==year}
    for _ in range(config['bootstrap_replicates']):
        sampled=[]
        for __ in range(4):
            s=rng.randrange(len(months));sampled.extend([months[s],months[(s+1)%len(months)]])
        excess={k:sum(cells.get((k[0],k[1],m),0) for m in sampled) for k in pool}
        denominator=sum(max(0,x) for x in excess.values())
        delta=sum(max(0,excess[k]) for k in picks)-sum(max(0,excess[k]) for k in baseline)
        values.append(100*delta/denominator if denominator else 0)
    values.sort();return [values[int(.025*len(values))],values[int(.975*len(values))]]

def scenario(excess,cost_per_minute,fraction,pilot_cost,sites):
    assert math.isfinite(excess) and cost_per_minute>0 and 0<=fraction<=1 and pilot_cost>=0 and sites>=0
    opportunity=max(0,excess)*cost_per_minute
    return {'assumed_cost_per_minute_usd':cost_per_minute,'assumed_recoverable_fraction':fraction,'assumed_cost_per_site_usd':pilot_cost,'modeled_net_usd':opportunity*fraction-pilot_cost*sites,'break_even_recoverable_fraction':pilot_cost*sites/opportunity if opportunity else None}

def main(out=None):
    out=Path(out or BASE/'outputs');out.mkdir(parents=True,exist_ok=True)
    cfg=json.loads((BASE/'config.json').read_text());raw,valid,issues=load(cfg);db=warehouse(valid)
    rows=[dict(r) for r in db.execute('SELECT * FROM peer_screen ORDER BY year,month,carrier,airport')]
    discovery=summaries(rows,2024,cfg['months'])
    pool={k:v for k,v in discovery.items() if v['months']>=cfg['minimum_site_months'] and v['flights']>=cfg['minimum_site_flights']}
    assert len(pool)>=10
    picks=select(pool,'excess_minutes',cfg['investigation_slots'],cfg['maximum_per_airport'])
    baseline=select(pool,'carrier_minutes',cfg['investigation_slots'],cfg['maximum_per_airport'])
    evals=[]
    for name,selection in [('peer_adjusted',picks),('raw_burden_baseline',baseline)]:
        for year in [2024,2025,2026]:evals.append({'policy':name,**evaluate(rows,selection,pool,year,cfg['months'])})
    interval=bootstrap(rows,picks,baseline,pool,2026,cfg)
    a=next(r for r in evals if r['policy']=='peer_adjusted' and r['year']==2026);b=next(r for r in evals if r['policy']=='raw_burden_baseline' and r['year']==2026)
    # Neither policy is retuned after the discovery cohort. 2025 is a validation checkpoint.
    passed=interval[0]>0 and a['slots_observed']==len(picks)
    review=[];current=summaries(rows,2026,cfg['months'])
    for rank,k in enumerate(picks,1):
        v=current.get(k,{})
        review.append(dict(rank=rank,carrier=k[0],airport=k[1],discovery_excess_minutes=pool[k]['excess_minutes'],diagnostic_months=v.get('months',0),diagnostic_flights=v.get('flights',0),diagnostic_excess_minutes=v.get('excess_minutes',0),status='needs_operational_review'))
    allsites=[]
    for year in [2024,2025,2026]:
        for k,v in sorted(summaries(rows,year,cfg['months']).items()):allsites.append({'year':year,**v,'discovery_eligible':int(k in pool),'selected':int(k in picks)})
    # Sensitivity: repeat current diagnostics retaining reconciled numeric rows even when cause totals disagree.
    loose=dict(cfg,delay_minutes_reconciliation_tolerance=1e12,cause_count_reconciliation_tolerance=1e12)
    _,lv,_=load(loose);ld=warehouse(lv);lr=[dict(r) for r in ld.execute('SELECT * FROM peer_screen')]
    sens=evaluate(lr,picks,pool,2026,cfg['months'])
    scenarios=[]
    for fraction in [.05,.1,.2]:
        for price in [30,60,120]:scenarios.append(scenario(a['signed_excess_minutes'],price,fraction,100000,len(picks)))
    stats={'source_rows':len(raw),'valid_rows':len(valid),'quarantined_rows':len(issues),'peer_eligible_rows':len(rows),'discovery_sites':len(pool),'investigation_slots_filled':len(picks),'baseline_overlap':len(set(picks)&set(baseline)),'diagnostic_capture_difference_percentage_points':a['positive_excess_capture_pct']-b['positive_excess_capture_pct'],'exploratory_95pct_month_block_interval_pp':interval,'retrospective_stability_gate':passed,'prospective_deployment_gate':False,'classification':'retrospective research screen; no causal or prospective validation','diagnostic_with_reconciliation_flags_retained':sens,'strict_diagnostic':a}
    write_csv(out/'quarantine.csv',issues);write_csv(out/'source_audited_peer_rows.csv.gz',rows);write_csv(out/'site_history.csv',allsites);write_csv(out/'investigation_shortlist.csv',review);write_csv(out/'policy_evaluation.csv',evals);write_csv(out/'scenario_sensitivity.csv',scenarios);write_json(out/'metrics.json',stats)
    totals=[]
    for year,month,airport,n,flights,minutes in db.execute('SELECT * FROM airport_month ORDER BY year,month,airport'):totals.append(dict(year=year,month=month,airport=airport,carriers=n,flights=flights,carrier_minutes=minutes))
    write_csv(out/'sql_airport_totals.csv',totals)
    plot_bars(out/'policy_capture',[f"{r['year']} · "+({"peer_adjusted":"Peer adjusted","raw_burden_baseline":"Raw delay baseline"}[r["policy"]]) for r in evals],[r['positive_excess_capture_pct'] for r in evals],'Do peer-adjusted investigation priorities persist?','Jan–Aug positive peer excess captured (%) · fixed 2024 eligible pool',colors=['#137f8c']*3+['#c58b49']*3)
    lead=f"A fixed ten-slot investigation screen captures {a['positive_excess_capture_pct']:.1f}% of eligible positive peer excess in Jan–Aug 2026; the raw-burden baseline captures {b['positive_excess_capture_pct']:.1f}%. Retrospective stability gate: {'PASS' if passed else 'FAIL'}; prospective deployment gate: NOT MET."
    memo=f'''# Airline delay intervention screen\n\n{lead}\n\n## Decision\n\nUse the shortlist for structured operational investigation only. Do not purchase a delay-reduction program from this evidence. The screen adjusts each carrier-airport-month against other operating carriers at the same airport and month, excluding itself. It freezes the candidate universe and priorities using Jan–Aug 2024; checks Jan–Aug 2025; diagnoses Jan–Aug 2026 without retuning. Both policies share ten slots and a two-per-airport cap.\n\nThe capture difference is {stats['diagnostic_capture_difference_percentage_points']:.2f} percentage points; its exploratory two-month-block interval is [{interval[0]:.2f}, {interval[1]:.2f}]. This is concentration of an accounting benchmark, not intervention lift. The denominator is only the discovery-eligible pool still observed, not the entire US network.\n\n## Evidence quality\n\n{len(raw):,} source rows; {len(issues)} quarantined; {len(rows):,} peer-eligible monthly rows. Row exclusions include missing observations and cause-total mismatches. Retaining reconciliation-flagged rows changes selected-site diagnostic signed excess from {a['signed_excess_minutes']:,.0f} to {sens['signed_excess_minutes']:,.0f} minutes. Source rows remain auditable.\n\n## Action workflow\n\n1. Review the shortlist and complete history; identify carrier and airport operational owners.\n2. Obtain flight rotations, turnaround, crew and maintenance records. Confirm the peer rate is feasible for comparable schedules and aircraft.\n3. Price a pilot using the scenario CLI. Values and recoverable fractions are assumptions; negative net values are retained.\n4. Pre-register a randomized or staggered operational pilot with cancellation, safety and customer-service guardrails before claiming savings.\n\n## My understanding and interview defense\n\nA busy airport can generate many delay minutes without having unusually poor performance. The comparison uses another-carrier benchmark at that airport in that month, so it asks where a carrier departs from a common local environment. Its signed excess can be negative. Late-aircraft, NAS and weather minutes are not relabeled as controllable carrier minutes.\n\nThe comparison still lacks schedule, fleet and route adjustment, and eight diagnostic months do not establish generalizable superiority. Historical data are today's revised snapshot, so the time split is a retrospective stability study, not a point-in-time backtest. I should show a source row, independently compute its excluded-self peer rate, explain the capacity constraint and explain why a pilot is needed.\n'''
    (out/'executive_memo.md').write_text(memo)
    report(out/'report.html','Airline delay intervention screen','US passenger airlines · Operating performance due diligence',lead,[('The decision', '<p class="flag">Investigate before intervening. Peer excess measures an accounting gap, not avoidable minutes or measured savings.</p>'),('Fixed priorities across three years','<img src="policy_capture.png" alt="Positive peer-excess capture of two fixed priority policies across 2024, 2025 and 2026.">'+table(evals,['policy','year','slots_observed','positive_excess_capture_pct','signed_excess_minutes'])),('Investigation queue',table(review,['rank','carrier','airport','diagnostic_months','diagnostic_excess_minutes','status'])),('Evidence and boundaries',f'<p>{len(raw):,} original rows; {len(issues)} quarantined. Source export: Jan 2024–Aug 2026. Leave-one-out peers need three other carriers and 1,000 other-carrier flights. Candidate universe and shortlist fixed from 2024. Exploratory block interval: {interval[0]:.2f} to {interval[1]:.2f} percentage points.</p><p>No flight-level schedule controls, passenger counts, causal intervention data or historical release vintages. Review both strict and permissive reconciliation sensitivities.</p>'),('Review files','<p><a href="executive_memo.md">Executive memo</a> · <a href="investigation_shortlist.csv">Shortlist CSV</a> · <a href="source_audited_peer_rows.csv.gz">Source lineage and peers</a> · <a href="quarantine.csv">Quarantine register</a> · <a href="scenario_sensitivity.csv">Hypothetical pilot economics</a></p>')])
    build_application(BASE,out,'airline')
    return stats

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output');p.add_argument('--scenario',action='store_true');p.add_argument('--excess-minutes',type=float,default=100000);p.add_argument('--cost-per-minute',type=float,default=60);p.add_argument('--recoverable-fraction',type=float,default=.1);p.add_argument('--cost-per-site',type=float,default=100000);p.add_argument('--sites',type=int,default=10);a=p.parse_args()
    if a.scenario:print(json.dumps(scenario(a.excess_minutes,a.cost_per_minute,a.recoverable_fraction,a.cost_per_site,a.sites),indent=2))
    else:print(json.dumps(main(a.output),indent=2))
