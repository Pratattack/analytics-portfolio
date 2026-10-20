"""Exact three-factor accounting attribution with explicit proxy-rate and cohort limits."""
import argparse,csv,gzip,itertools,json,math,sqlite3,statistics,sys
from collections import defaultdict,Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research_support import write_csv,write_json,plot_bars,report,table
from applications import build_application
BASE=Path(__file__).resolve().parent
FIELDS=['ASSET','DEPDOM','DEPNIDOM','EDEPDOM','EDEPDOMQ','NETINCQ','DEPUNINS','DEP']
def previous(date):
    y=int(date[:4]);return {'0331':f'{y-1}1231','0630':f'{y}0331','0930':f'{y}0630','1231':f'{y}0930'}[date[4:]]

def load(cfg):
    rows=[];lookup={};issues=[]
    for file in sorted((BASE/'data/raw').glob('*.json.gz')):
        source=json.loads(gzip.decompress(file.read_bytes()));assert source['meta']['total']==len(source['data'])
        for i,item in enumerate(source['data']):
            r=item['data'];assert str(r['REPDTE'])==file.name[:8]
            assert r['INSAGNT1']=='DIF' and r['BKCLASS']!='OI'
            key=(int(r['CERT']),str(r['REPDTE']));assert key not in lookup
            row=dict(cert=key[0],report_date=key[1],previous_date=previous(key[1]),name=r['NAME'],state=r['STALP'],bank_class=r['BKCLASS'],source_file=file.name,source_pointer=f'/data/{i}/data',accepted=1)
            reasons=[]
            for k in FIELDS:
                value=r.get(k)
                if value is None or not isinstance(value,(int,float)) or not math.isfinite(value):reasons.append('missing_'+k)
                row[k.lower()]=value
            if not reasons:
                if not 0<=row['depnidom']<=row['depdom']<=row['dep']:reasons.append('deposit_stock_contract')
                if row['edepdomq']<0 or row['edepdom']<0:reasons.append('negative_expense')
            row['reasons']=';'.join(reasons);rows.append(row);lookup[key]=row
    for row in rows:
        if row['reasons']:row['accepted']=0;continue
        p=lookup.get((row['cert'],row['previous_date']))
        expected=row['edepdom'] if row['report_date'].endswith('0331') else row['edepdom']-p['edepdom'] if p and p['edepdom'] is not None else None
        if expected is not None and abs(expected-row['edepdomq'])>cfg['quarterly_ytd_tolerance_thousand_usd']:
            row['accepted']=0;row['reasons']='quarterly_YTD_mismatch'
        if row['accepted']==0:issues.append({k:row[k] for k in ['cert','report_date','source_file','source_pointer','reasons']})
    # Append other contract failures too; these are not dropped silently.
    for r in rows:
        if r['accepted']==0 and r['reasons']!='quarterly_YTD_mismatch':issues.append({k:r[k] for k in ['cert','report_date','source_file','source_pointer','reasons']})
    return rows,lookup,issues

def warehouse(rows):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row;keys=list(rows[0])
    types={k:('INTEGER' if k in ['cert','accepted'] else 'REAL' if k in [f.lower() for f in FIELDS] else 'TEXT') for k in keys}
    db.execute('CREATE TABLE bank_quarter ('+','.join(k+' '+types[k] for k in keys)+')')
    db.executemany('INSERT INTO bank_quarter VALUES ('+','.join('?' for _ in keys)+')',[[r[k] for k in keys] for r in rows])
    cfg=json.loads((BASE/'config.json').read_text())
    db.execute('CREATE TABLE thresholds (minimum_ib_balance REAL)')
    db.execute('INSERT INTO thresholds VALUES (?)',(cfg['minimum_average_interest_bearing_deposits_thousand_usd'],))
    db.executescript((BASE/'analysis.sql').read_text());return db

def cost(factors):return factors[0]*factors[1]*factors[2]/4

def shapley(before,after):
    result=[0.,0.,0.]
    for permutation in itertools.permutations(range(3)):
        x=list(before)
        for k in permutation:
            old=cost(x);x[k]=after[k];result[k]+=(cost(x)-old)/6
    return result

def peer_bucket(asset):return 'under_1bn' if asset<1e6 else '1_to_10bn' if asset<1e7 else 'over_10bn'

def retention(balance,proxy_rate,cut,target_share,loss,replacement_rate,fixed_cost):
    assert balance>=0 and 0<=cut<=proxy_rate and 0<=target_share<=1 and 0<=loss<=1 and replacement_rate>=0 and fixed_cost>=0
    targeted=balance*target_share
    savings=targeted*(1-loss)*cut
    extra_funding=targeted*loss*(replacement_rate-proxy_rate)
    net=savings-extra_funding-fixed_cost
    denominator=cut+replacement_rate-proxy_rate
    threshold=(cut-fixed_cost/targeted)/denominator if targeted and denominator>0 else None
    return dict(assumed_rate_cut_bp=cut*10000,assumed_target_share=target_share,assumed_attrition=loss,assumed_replacement_rate=replacement_rate,assumed_annual_fixed_cost_usd=fixed_cost,annual_retained_balance_savings_usd=savings,annual_replacement_increment_usd=extra_funding,modeled_annual_net_usd=net,break_even_attrition=threshold)

def main(out=None):
    out=Path(out or BASE/'outputs');out.mkdir(parents=True,exist_ok=True);cfg=json.loads((BASE/'config.json').read_text())
    source,lookup,issues=load(cfg);db=warehouse(source)
    panel=[dict(r) for r in db.execute('SELECT * FROM quarterly_proxy ORDER BY cert,report_date')]
    bykey={(r['cert'],r['report_date']):r for r in panel};before=cfg['baseline_date'];after=cfg['comparison_date']
    latest=[r for r in source if r['report_date']==after];assert len(latest)==cfg['latest_release_bank_count']
    attr=[];excluded=[];unscreened=[]
    for row in latest:
        c=row['cert'];a=bykey.get((c,before));b=bykey.get((c,after))
        if not a or not b:excluded.append(dict(cert=c,name=row['name'],reason='missing_valid_baseline_or_comparison_proxy'));continue
        f0=[a['average_domestic_deposits'],a['interest_bearing_share'],a['annualized_proxy_rate']];f1=[b['average_domestic_deposits'],b['interest_bearing_share'],b['annualized_proxy_rate']]
        parts=shapley(f0,f1);change=b['edepdomq']-a['edepdomq'];assert abs(sum(parts)-change)<.0001
        growth=b['average_domestic_deposits']/a['average_domestic_deposits']-1
        qgrowth=b['depdom']/lookup[(c,b['previous_date'])]['depdom']-1 if lookup[(c,b['previous_date'])]['depdom'] else float('inf')
        r=dict(cert=c,name=b['name'],state=b['state'],asset_bucket=peer_bucket(b['asset']),baseline_expense_thousand_usd=a['edepdomq'],comparison_expense_thousand_usd=b['edepdomq'],change_thousand_usd=change,volume_contribution_thousand_usd=parts[0],mix_contribution_thousand_usd=parts[1],proxy_rate_contribution_thousand_usd=parts[2],residual_thousand_usd=change-sum(parts),deposit_growth=growth,quarter_deposit_growth=qgrowth,average_domestic_deposits_thousand_usd=b['average_domestic_deposits'],interest_bearing_share=b['interest_bearing_share'],baseline_proxy_rate=a['annualized_proxy_rate'],comparison_proxy_rate=b['annualized_proxy_rate'],source_file=b['source_file'],source_pointer=b['source_pointer'])
        r['constant_mix_rate_baseline_expense_thousand_usd']=cost([f1[0],f0[1],f0[2]])
        r['baseline_gap_thousand_usd']=b['edepdomq']-r['constant_mix_rate_baseline_expense_thousand_usd']
        unscreened.append(r)
        if abs(growth)>cfg['maximum_absolute_deposit_growth'] or abs(qgrowth)>cfg['maximum_absolute_deposit_growth']:
            excluded.append(dict(cert=c,name=row['name'],reason='large_balance_change_structural_break_screen'));continue
        attr.append(r)
    assert len(attr)>3000
    peers=defaultdict(list)
    for r in attr:peers[r['asset_bucket']].append(r['comparison_proxy_rate'])
    for r in attr:
        other=[x['comparison_proxy_rate'] for x in attr if x['asset_bucket']==r['asset_bucket'] and x['cert']!=r['cert']]
        r['peer_median_proxy_rate']=statistics.median(other);r['peer_rate_gap_bp']=(r['comparison_proxy_rate']-r['peer_median_proxy_rate'])*10000
    totals=[]
    for r in db.execute('SELECT * FROM industry_totals ORDER BY report_date'):totals.append(dict(r))
    summary={'source_rows':len(source),'quarterly_proxies':len(panel),'quarterly_YTD_or_contract_flags':len(issues),'latest_universe_institutions':len(latest),'latest_total_deposits_trillion_usd':sum(r['dep'] for r in latest)/1e9,'matched_screened_banks':len(attr),'matched_before_growth_screen':len(unscreened),'latest_banks_excluded':len(excluded),'baseline_date':before,'comparison_date':after,'scope':'DIF insured institutions excluding foreign branches; domestic deposit expense; nominal USD','method':'exact six-order Shapley accounting decomposition; endpoint-average proxy rate; not causal'}
    for field in ['baseline_expense_thousand_usd','comparison_expense_thousand_usd','change_thousand_usd','volume_contribution_thousand_usd','mix_contribution_thousand_usd','proxy_rate_contribution_thousand_usd','residual_thousand_usd']:
        summary[field]=sum(r[field] for r in attr)
    summary['constant_mix_rate_baseline_expense_thousand_usd']=sum(r['constant_mix_rate_baseline_expense_thousand_usd'] for r in attr)
    summary['baseline_gap_thousand_usd']=sum(r['baseline_gap_thousand_usd'] for r in attr)
    summary['unscreened_change_thousand_usd']=sum(r['change_thousand_usd'] for r in unscreened)
    summary['screened_latest_domestic_deposit_coverage_pct']=100*sum(lookup[(r['cert'],after)]['depdom'] for r in attr)/sum(r['depdom'] for r in latest)
    median=statistics.median(r['comparison_proxy_rate'] for r in attr);summary['median_proxy_rate']=median
    # Scenarios use a generic $1bn domestic bank's modeled balances; never imply a named bank will adopt a rate cut.
    modeled=[]
    for cut in [.001,.0025]:
        for share in [.25,1]:
            for loss in [0,.05,.15,.3]:modeled.append(retention(1e9,0.025,cut,share,loss,.045,100000))
    # Signed driver ranking; review pressure, not automatic recommendations or bank safety ranking.
    priority=sorted(attr,key=lambda r:(-r['proxy_rate_contribution_thousand_usd'],r['cert']))[:20]
    history=[]
    for date in sorted({r['report_date'] for r in panel}):
        g=[r for r in panel if r['report_date']==date]
        history.append(dict(date=date,accepted_banks=len(g),average_domestic_deposits_thousand_usd=sum(r['average_domestic_deposits'] for r in g),domestic_expense_thousand_usd=sum(r['edepdomq'] for r in g),weighted_annual_proxy_rate=4*sum(r['edepdomq'] for r in g)/sum(r['average_domestic_deposits'] for r in g)))
    sensitivity=[]
    for cutoff in [.2,.3,.5,1e99]:
        cohort=[r for r in unscreened if abs(r['deposit_growth'])<=cutoff and abs(r['quarter_deposit_growth'])<=cutoff]
        sensitivity.append(dict(maximum_absolute_growth=str(cutoff) if cutoff<1e90 else 'none',banks=len(cohort),expense_change_thousand_usd=sum(r['change_thousand_usd'] for r in cohort),proxy_rate_contribution_thousand_usd=sum(r['proxy_rate_contribution_thousand_usd'] for r in cohort)))
    write_csv(out/'structural_break_sensitivity.csv',sensitivity)
    write_csv(out/'source_audited_quarterly_panel.csv.gz',panel);write_csv(out/'quarterly_flags.csv',issues);write_csv(out/'cohort_exclusions.csv',excluded);write_csv(out/'bank_cost_bridge.csv',attr);write_csv(out/'unscreened_bridge.csv',unscreened);write_csv(out/'review_queue.csv',priority);write_csv(out/'industry_totals.csv',totals);write_csv(out/'quarterly_history.csv',history);write_csv(out/'retention_scenarios.csv',modeled);write_json(out/'metrics.json',summary)
    drivers=[summary[k]/1e6 for k in ['volume_contribution_thousand_usd','mix_contribution_thousand_usd','proxy_rate_contribution_thousand_usd','change_thousand_usd']]
    plot_bars(out/'cost_bridge',['Balance volume','Interest-bearing mix','Residual proxy rate','Observed total change'],drivers,'Why did quarterly domestic deposit expense change?','Q2 2026 minus Q2 2025 · USD billions · fixed screened bank cohort',colors=['#137f8c','#7999ab','#c58b49','#183d51'])
    lead=f"Across {len(attr):,} comparable insured banks, quarterly domestic deposit interest expense changed by ${summary['change_thousand_usd']/1e6:,.2f}bn from Q2 2025 to Q2 2026. The proxy-rate component contributes ${summary['proxy_rate_contribution_thousand_usd']/1e6:,.2f}bn."
    memo=f'''# Bank deposit cost attribution\n\n{lead}\n\n## Decision\n\nSeparate balance growth, interest-bearing mix migration and the residual proxy-rate effect before recommending blanket repricing. This is an accounting bridge for a bank-treasury workstream, not a forecast of depositor behavior or an assessment of bank safety. The review queue is ranked by positive proxy-rate expense contribution, with asset-size peer medians for context. No savings are booked.\n\n## Evidence\n\nThe pinned FDIC panel contains {len(source):,} bank-quarters across 11 dates. The latest insured domestic-bank universe has {len(latest):,} institutions and ${summary['latest_total_deposits_trillion_usd']:.3f}tn total deposits, consistent with the Q2 2026 QBP rounded industry scale. {len(issues)} bank-quarters have expense/contract flags. The screen keeps {len(attr):,} matched banks, representing {summary['screened_latest_domestic_deposit_coverage_pct']:.1f}% of latest domestic deposits. It excludes {len(excluded)} latest institutions because of missing accepted pairs or a greater-than-30% balance change; the latter is a structural-break heuristic, not proof of a merger. Before that growth screen, the matched expense change is ${summary['unscreened_change_thousand_usd']/1e6:.2f}bn.\n\nThe screened change decomposes into balance volume ${drivers[0]:.3f}bn, mix ${drivers[1]:.3f}bn, and proxy rate ${drivers[2]:.3f}bn. Six possible replacement orders allocate interactions symmetrically. The aggregate arithmetic residual is {summary['residual_thousand_usd']:.8f} thousand dollars. Exact reconciliation does not validate an economic causal interpretation.\n\n## Business tradeoff\n\nThe scenario grid models a generic $1bn interest-bearing balance, a 2.5% starting proxy rate, a 4.5% replacement funding rate, 10–25bp cuts, 25–100% targeted shares, 0–30% attrition and $100,000 annual fixed cost. These inputs are invented, separate from the empirical bank bridge. A larger cut saves more on retained balances but can increase replacement funding costs if customers leave. Real adoption needs account-level rates, contractual renewal dates, customer elasticities, liquidity constraints and treasury approval.\n\n## My understanding and interview defense\n\nA bank's expense can fall while its deposit base grows. The bridge asks how much of the observed change comes from volume, from the share that earns interest and from expense per interest-bearing balance. The rate is derived using two quarter-end balances, not regulatory daily-average deposits, and it absorbs timing, composition and measurement effects. It is neither a quoted product rate nor a causal deposit beta.\n\nI should be able to hand-compute one three-factor bridge, explain why order averaging avoids an arbitrary interaction allocation, trace every input to its FDIC JSON pointer, show which bank-quarters fail YTD reconciliation and demonstrate how attrition erases a seemingly attractive rate-cut saving. I should also explain that size peers omit business-model differences and certificate matching does not completely neutralize acquisitions.\n'''
    (out/'executive_memo.md').write_text(memo)
    report(out/'report.html','Bank deposit cost attribution','US insured domestic banking · Treasury decision support',lead,[('The decision','<p class="flag">Review the source of funding-cost changes before repricing deposits. An exact accounting bridge does not establish pricing power or customer retention.</p>'),('A reconciled three-factor bridge','<img src="cost_bridge.png" alt="Signed volume, interest-bearing mix, proxy-rate and total quarterly expense change in billions of US dollars.">'+f'<p>Fixed cohort: {len(attr):,} banks. Latest domestic-deposit coverage: {summary["screened_latest_domestic_deposit_coverage_pct"]:.1f}%. Endpoint-average balances are proxies.</p>'),('Review queue, not a bank safety ranking',table(priority[:10],['cert','name','asset_bucket','proxy_rate_contribution_thousand_usd','peer_rate_gap_bp'])),('Coverage and exclusions',f'<p>{len(source):,} original bank-quarters; {len(issues)} quarterly flags; {len(excluded)} latest institutions excluded from the bridge. The full latest universe has {len(latest):,} institutions. Source pointer lineage, excluded cohorts and unscreened sensitivities are retained.</p><p>No historical publication-vintage reconstruction, causal pricing elasticity, daily-average balance data or complete merger adjustment. Results support an investigation, not a blanket pricing decision.</p>'),('Run a funding tradeoff','<p>Use the documented scenario CLI to vary targeted share, cut, attrition, replacement rate and fixed cost. The generic scenario grid is explicitly hypothetical.</p><p><a href="executive_memo.md">Executive memo</a> · <a href="bank_cost_bridge.csv">Bank bridges</a> · <a href="cohort_exclusions.csv">Cohort exclusions</a> · <a href="quarterly_flags.csv">Quarterly flags</a> · <a href="retention_scenarios.csv">Retention scenarios</a></p>')])
    build_application(BASE,out,'bank')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output');p.add_argument('--scenario',action='store_true');p.add_argument('--balance',type=float,default=1e9);p.add_argument('--proxy-rate',type=float,default=.025);p.add_argument('--cut-bp',type=float,default=25);p.add_argument('--target-share',type=float,default=.25);p.add_argument('--attrition',type=float,default=.05);p.add_argument('--replacement-rate',type=float,default=.045);p.add_argument('--fixed-cost',type=float,default=100000);a=p.parse_args()
    if a.scenario:print(json.dumps(retention(a.balance,a.proxy_rate,a.cut_bp/10000,a.target_share,a.attrition,a.replacement_rate,a.fixed_cost),indent=2))
    else:print(json.dumps(main(a.output),indent=2))
