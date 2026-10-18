"""Method-consistent utility peer review and strictly report-year-separated audit."""
from pathlib import Path
import csv,json,math,random,statistics,sqlite3,hashlib
from collections import defaultdict
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
MODELS=['last_report','median_3','shrink_25','shrink_50','shrink_75']
def read_panel():
    with (ROOT/'data/panel.csv').open() as f:rows=list(csv.DictReader(f))
    for r in rows:
        for k in ['year','utility_id','source_row']:r[k]=int(r[k])
        for k in ['saidi_all','saidi_normal','saifi_all','saifi_normal','customers']:r[k]=float(r[k]) if r[k]!='' else None
    return rows
def write_csv(path,rows):
    rows=list(rows)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def valid(r):return r['standard']=='IEEE' and r['saidi_normal'] is not None and (r['customers'] or 0)>0
def size_bin(n):return 'under_10k' if n<10000 else '10k_100k' if n<100000 else '100k_1m' if n<1000000 else '1m_plus'
def quantile(values,q):
    if not values or not 0<=q<=1:raise ValueError('Invalid quantile')
    return sorted(values)[min(len(values)-1,max(0,math.ceil(len(values)*q)-1))]
def peer_reference(row,pool):
    others=[p for p in pool if p['utility_id']!=row['utility_id']]
    groups=[('state_ownership',[p for p in others if p['state']==row['state'] and p['ownership']==row['ownership']]),('ownership_size',[p for p in others if p['ownership']==row['ownership'] and size_bin(p['customers'])==size_bin(row['customers'])]),('ownership',[p for p in others if p['ownership']==row['ownership']]),('national',others)]
    name,peers=next(((name,g) for name,g in groups if len(g)>=15),groups[-1])
    if not peers:raise ValueError('Insufficient peer pool')
    return name,peers
def predictions(rows,target_year):
    ieee=[r for r in rows if valid(r)];history=defaultdict(list)
    for r in ieee:
        if r['year']<target_year:history[r['utility_id'],r['state']].append(r)
    pool=[r for r in ieee if r['year']==target_year-1];records=[]
    for target in [r for r in ieee if r['year']==target_year]:
        hist=sorted(history[target['utility_id'],target['state']],key=lambda r:r['year'])
        if not hist or hist[-1]['year']!=target_year-1:continue
        last=hist[-1];recent=[r for r in hist if r['year']>=target_year-3]
        peer_group,peers=peer_reference(last,pool);peer=statistics.median(math.log1p(r['saidi_normal']) for r in peers)
        own=statistics.median(math.log1p(r['saidi_normal']) for r in recent)
        estimates=dict(last_report=last['saidi_normal'],median_3=math.expm1(own))
        for shrink in [25,50,75]:estimates[f'shrink_{shrink}']=math.expm1((1-shrink/100)*own+shrink/100*peer)
        for model,estimate in estimates.items():
            records.append(dict(target_year=target_year,utility_id=target['utility_id'],state=target['state'],utility_name=target['utility_name'],model=model,actual=target['saidi_normal'],prediction=estimate,lag_customers=last['customers'],current_customers=target['customers'],last_input_year=last['year'],peer_group=peer_group,peer_n=len(peers),history_n=len(recent),log_residual=math.log1p(target['saidi_normal'])-math.log1p(estimate)))
    return records
def score(records):
    weights=sum(r['lag_customers'] for r in records)
    return dict(rows=len(records),utilities=len({r['utility_id'] for r in records}),mae_minutes=statistics.mean(abs(r['actual']-r['prediction']) for r in records),lag_customer_weighted_mae=sum(abs(r['actual']-r['prediction'])*r['lag_customers'] for r in records)/weights,rmse_minutes=math.sqrt(statistics.mean((r['actual']-r['prediction'])**2 for r in records)),mean_prediction_minus_actual=statistics.mean(r['prediction']-r['actual'] for r in records))
def cluster_bootstrap_differences(selected,baseline,draws=600):
    lookup={(r['utility_id'],r['state']):r for r in baseline};clusters=defaultdict(list)
    for r in selected:
        b=lookup[r['utility_id'],r['state']]
        # Positive difference means selected model reduces absolute error.
        clusters[r['utility_id']].append((r['lag_customers']*(abs(b['actual']-b['prediction'])-abs(r['actual']-r['prediction'])),r['lag_customers']))
    sufficient={k:(sum(x for x,w in g),sum(w for x,w in g)) for k,g in clusters.items()};ids=sorted(sufficient);rng=random.Random(20261018);values=[]
    for _ in range(draws):
        sampled=[sufficient[rng.choice(ids)] for __ in ids];values.append(sum(x for x,w in sampled)/sum(w for x,w in sampled))
    return dict(draws=draws,clusters=len(ids),mean_weighted_error_reduction=sum(v[0] for v in sufficient.values())/sum(v[1] for v in sufficient.values()),percentile_95=[quantile(values,.025),quantile(values,.975)])
def scenario(saidi,customers,reduction,hour_value,opex,rate,years):
    if not(all(math.isfinite(x) for x in [saidi,customers,reduction,hour_value,opex,rate]) and 0<=reduction<=1 and customers>0 and saidi>=0 and hour_value>=0 and opex>=0 and rate>=0 and isinstance(years,int) and 0<years<=100):raise ValueError('Invalid scenario assumptions')
    annual_hours=saidi*customers*reduction/60
    annual_net=annual_hours*hour_value-opex
    factor=sum(1/(1+rate)**y for y in range(1,years+1))
    return dict(annual_customer_hours_avoided_proxy=annual_hours,annual_net_social_value_usd=annual_net,break_even_upfront_cost_usd=annual_net*factor)
def reconcile(rows):
    with (ROOT/'data/published_state_totals.csv').open() as f:published=list(csv.DictReader(f))
    out=[]
    for p in published:
        y=int(p['year']);s=p['state'];g=[r for r in rows if r['year']==y and r['state']==s and r['standard']=='IEEE' and r['saidi_all'] is not None and (r['customers'] or 0)>0]
        if not g or p['ieee_saidi_all']=='':continue
        calculated=sum(r['saidi_all']*r['customers'] for r in g)/sum(r['customers'] for r in g)
        out.append(dict(year=y,state=s,calculated_all_saidi=calculated,published_all_saidi=float(p['ieee_saidi_all']),difference=calculated-float(p['ieee_saidi_all']),within_rounding_tolerance=abs(calculated-float(p['ieee_saidi_all']))<=.11))
    return out
def main():
    OUT.mkdir(exist_ok=True);rows=read_panel();ieee=[r for r in rows if valid(r)];latest_source=max(r['year'] for r in rows)
    reconciliation=reconcile(rows)
    quarantined=sorted({r['year'] for r in reconciliation if not r['within_rounding_tolerance']})
    reconciled_years={r['year'] for r in reconciliation}-set(quarantined)
    latest=max(reconciled_years)
    all_predictions=[]
    for year in [2023,2024,2025]:all_predictions.extend(predictions(rows,year))
    development=[r for r in all_predictions if r['target_year']==2023];selection=[dict(model=name,**score([r for r in development if r['model']==name])) for name in MODELS]
    winner=min(selection,key=lambda r:(r['lag_customer_weighted_mae'],r['model']))['model'];write_csv(OUT/'model_selection_2023.csv',selection)
    calibration=[r for r in all_predictions if r['target_year']==2024 and r['model']==winner]
    radius=quantile([abs(r['log_residual']) for r in calibration],min(1,math.ceil((len(calibration)+1)*.90)/len(calibration)))
    evaluation=[];test=[r for r in all_predictions if r['target_year']==2025];coverage=0
    for r in test:
        if r['model']==winner:
            r['lower']=max(0.,math.expm1(math.log1p(r['prediction'])-radius));r['upper']=math.expm1(math.log1p(r['prediction'])+radius);coverage+=r['lower']<=r['actual']<=r['upper']
        else:r['lower']=None;r['upper']=None
    for name in MODELS:evaluation.append(dict(model=name,**score([r for r in test if r['model']==name])))
    write_csv(OUT/'heldout_2025_evaluation.csv',evaluation);write_csv(OUT/'report_year_predictions.csv',[dict(r,lower=r.get('lower'),upper=r.get('upper')) for r in all_predictions])
    chosen=[r for r in test if r['model']==winner];baseline=[r for r in test if r['model']=='last_report'];bootstrap=cluster_bootstrap_differences(chosen,baseline)
    pool=[r for r in ieee if r['year']==latest];review=[]
    active_method=defaultdict(set)
    for r in rows:
        if r['saidi_normal'] is not None and (r['customers'] or 0)>0:active_method[r['utility_id'],r['state'],r['year']].add(r['standard'])
    for r in pool:
        group,peers=peer_reference(r,pool);values=[p['saidi_normal'] for p in peers];hist=[x for x in ieee if x['utility_id']==r['utility_id'] and x['state']==r['state'] and x['year']<latest]
        previous=max(hist,key=lambda r:r['year']) if hist else None
        flags=[]
        if previous and abs(r['customers']/previous['customers']-1)>.25:flags.append('customer_count_change_over_25pct')
        if previous and previous['year']!=latest-1:flags.append('gap_in_ieee_history')
        if not previous:flags.append('no_prior_valid_ieee_history')
        if active_method[r['utility_id'],r['state'],latest-1]!=active_method[r['utility_id'],r['state'],latest]:flags.append('reporting_method_change')
        if r['saidi_all'] is not None and r['saidi_normal']>r['saidi_all']:flags.append('normal_exceeds_all_review')
        rank=sum(v<=r['saidi_normal'] for v in values)/len(values)
        review.append(dict(year=latest,utility_id=r['utility_id'],state=r['state'],utility_name=r['utility_name'],ownership=r['ownership'],customers=r['customers'],saidi_normal=r['saidi_normal'],saidi_all=r['saidi_all'],normal_customer_hours=r['saidi_normal']*r['customers']/60,peer_group=group,peer_n=len(peers),peer_median=statistics.median(values),peer_percentile=rank,prior_normal=previous['saidi_normal'] if previous else None,data_flags=';'.join(flags),source_file=r['source_file'],source_row=r['source_row']))
    review.sort(key=lambda r:(-r['peer_percentile'],-r['normal_customer_hours'],r['utility_id'],r['state']));write_csv(OUT/'utility_due_diligence.csv',review)
    quality=[]
    for year in sorted({r['year'] for r in rows}):
        for standard in ['IEEE','Other']:
            g=[r for r in rows if r['year']==year and r['standard']==standard]
            quality.append(dict(year=year,standard=standard,source_rows=len(g),positive_customers=sum((r['customers'] or 0)>0 for r in g),missing_normal=sum(r['saidi_normal'] is None for r in g),complete_normal_positive_customers=sum(r['saidi_normal'] is not None and (r['customers'] or 0)>0 for r in g)))
    write_csv(OUT/'reporting_quality.csv',quality)
    # SQL warehouse is recreated from normalized source, never from an uploaded DB.
    (OUT/'reliability.sqlite').unlink(missing_ok=True)
    db=sqlite3.connect(OUT/'reliability.sqlite')
    fields=list(rows[0]);text={'utility_name','state','ownership','standard','automatic','source_file','source_sheet'}
    db.execute('CREATE TABLE reliability ('+','.join(k+(' TEXT' if k in text else ' REAL') for k in fields)+', PRIMARY KEY(year,utility_id,state,standard))')
    db.executemany('INSERT INTO reliability VALUES ('+','.join(':'+k for k in fields)+')',rows);db.commit()
    sql=(ROOT/'warehouse.sql').read_text();cur=db.execute(sql);state_summary=[dict(zip([x[0] for x in cur.description],r)) for r in cur];write_csv(OUT/'state_weighted_reliability.csv',state_summary);db.close()
    # Compare raw published 2025 state totals, retaining discrepancies for review.
    write_csv(OUT/'published_state_reconciliation.csv',reconciliation)
    # Hypothetical reduction/value grid, tied to observed utility exposure.
    candidates=[r for r in review if r['state']=='TX'][:8];scenarios=[]
    for r in candidates:
        for reduction in [.05,.10,.20]:
            for value in [5,15,30]:scenarios.append(dict(utility_id=r['utility_id'],state=r['state'],utility_name=r['utility_name'],reduction_assumption=reduction,value_assumption_usd_per_customer_hour=value,**scenario(r['saidi_normal'],r['customers'],reduction,value,25000,.07,10)))
    write_csv(OUT/'texas_break_even_scenarios.csv',scenarios)
    matched=set((r['utility_id'],r['state']) for r in chosen);long={}
    for r in ieee:
        key=(r['utility_id'],r['state']);long.setdefault(key,set()).add(r['year'])
    complete_keys={k for k,v in long.items() if len(v)==6}
    balanced=[r for r in chosen if (r['utility_id'],r['state']) in complete_keys];balanced_base=[r for r in baseline if (r['utility_id'],r['state']) in complete_keys]
    summaries=dict(panel_rows=len(rows),utility_state_keys=len({(r['utility_id'],r['state']) for r in rows}),valid_ieee_rows=len(ieee),latest_valid_ieee=len(pool),latest_source_year=latest_source,decision_view_year=latest,quarantined_years=quarantined,selection_year=2023,calibration_year=2024,test_year=2025,selected_model=winner,selected_test=score(chosen),baseline_test=score(baseline),bootstrap=bootstrap,empirical_90_interval_coverage=coverage/len(chosen),calibration_log_radius=radius,calibration_n=len(calibration),balanced_panel_test=score(balanced),balanced_baseline_test=score(balanced_base),review_data_flags=sum(bool(r['data_flags']) for r in review),state_reconciliation_rows=len(reconciliation),state_reconciliation_exceptions=sum(not r['within_rounding_tolerance'] for r in reconciliation),panel_sha256=hashlib.sha256((ROOT/'data/panel.csv').read_bytes()).hexdigest(),predictive_component_promotable=bootstrap['percentile_95'][0]>0 and coverage/len(chosen)>=.90 and 2025 not in quarantined)
    (OUT/'metrics.json').write_text(json.dumps(summaries,indent=2,sort_keys=True));print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
