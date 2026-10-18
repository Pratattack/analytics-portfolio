from common import *
from model import run_forecasts,quantile,decision_cost
import random,sqlite3

def line_chart(rows):
    high=max(max(r['actual'],r['upper_bound']) for r in rows);n=len(rows)
    def points(key):return ' '.join(f'{60+i/(n-1)*870:.2f},{300-r[key]/high*245:.2f}' for i,r in enumerate(rows))
    polygon=points('upper_bound')+' '+' '.join(f'{60+i/(n-1)*870:.2f},{300-rows[i]["lower_bound"]/high*245:.2f}' for i in range(n-1,-1,-1))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 360" role="img" aria-label="Historical test daily rental counts and prequential forecasts"><rect width="100%" height="100%" fill="white"/><text x="20" y="25" font-family="sans-serif" font-size="19">July–December 2012 · daily rentals</text><polygon points="'+polygon+'" fill="#d6ebef"/><polyline points="'+points('actual')+'" stroke="#193b5a" fill="none" stroke-width="1.6"/><polyline points="'+points('prediction')+'" stroke="#d47420" fill="none" stroke-width="1.5"/><line x1="60" y1="300" x2="930" y2="300" stroke="#718096"/><text x="60" y="325" font-family="sans-serif">2012-07-01</text><text x="810" y="325" font-family="sans-serif">2012-12-31</text><text x="60" y="347" font-family="sans-serif" font-size="12">Navy: actual · Orange: forecast · Shaded: validation-calibrated nominal 90% band</text><text x="6" y="60" font-family="sans-serif" font-size="11">'+str(round(high))+'</text><text x="25" y="303" font-family="sans-serif" font-size="11">0</text></svg>'

def main():
    OUT.mkdir(exist_ok=True);c=json.loads((ROOT/'config.json').read_text())
    with (ROOT/'data/day.csv').open() as f:rows=list(csv.DictReader(f))
    start=next(i for i,r in enumerate(rows) if r['dteday']>=c['validation_start'])
    forecasts=run_forecasts(rows,c['models'],start)
    validation=[r for r in forecasts if r['date']<c['test_start']]
    scores=[];params={}
    critical=c['shortfall_cost_per_trip_usd']/(c['shortfall_cost_per_trip_usd']+c['excess_capacity_cost_per_trip_usd'])
    for name in c['models']:
        v=[r for r in validation if r['model']==name]
        scores.append(dict(model=name,days=len(v),wape=sum(abs(r['error']) for r in v)/sum(r['actual'] for r in v),mae=statistics.mean(abs(r['error']) for r in v)))
        params[name]=dict(interval_radius=quantile([abs(r['error']) for r in v],c['interval_level'],True),capacity_adjustment=quantile([r['error'] for r in v],critical))
    chosen=min(scores,key=lambda r:(r['wape'],r['model']))['model'];csv_write(OUT/'validation_model_selection.csv',scores)
    scored=[]
    for r in forecasts:
        p=params[r['model']];q=max(0.,r['prediction']+p['capacity_adjustment']);actual=r['actual']
        scored.append(dict(**r,phase='validation' if r['date']<c['test_start'] else 'test',lower_bound=max(0.,r['prediction']-p['interval_radius']),upper_bound=r['prediction']+p['interval_radius'],capacity=q,shortfall=max(actual-q,0),excess=max(q-actual,0),decision_cost=decision_cost(actual,q,c['shortfall_cost_per_trip_usd'],c['excess_capacity_cost_per_trip_usd'])))
    csv_write(OUT/'prequential_forecasts.csv',scored)
    db=sqlite3.connect(':memory:');keys=list(scored[0]);text={'date','model','phase'}
    db.execute('CREATE TABLE scored ('+','.join('"'+k+'"'+(' TEXT' if k in text else ' REAL') for k in keys)+')')
    db.executemany('INSERT INTO scored VALUES ('+','.join(':'+k for k in keys)+')',scored)
    cur=db.execute((ROOT/'analysis.sql').read_text());summary=[dict(zip([x[0] for x in cur.description],r)) for r in cur];csv_write(OUT/'test_evaluation.csv',summary)
    selected=[r for r in scored if r['phase']=='test' and r['model']==chosen];base=[r for r in scored if r['phase']=='test' and r['model']=='seasonal_naive']
    differences=[b['decision_cost']-r['decision_cost'] for b,r in zip(base,selected)]
    rng=random.Random(20261018);block=c['bootstrap_block_days'];buckets=[differences[i:i+block] for i in range(0,len(differences),block)];boot=[]
    for _ in range(c['bootstrap_draws']):
        sample=[]
        while len(sample)<len(differences):sample.extend(rng.choice(buckets))
        boot.append(statistics.mean(sample[:len(differences)]))
    interval=[quantile(boot,.025),quantile(boot,.975)]
    monthly=[]
    for month in sorted({r['date'][:7] for r in selected}):
        g=[r for r in selected if r['date'].startswith(month)]
        monthly.append(dict(month=month,days=len(g),wape=sum(abs(r['error']) for r in g)/sum(r['actual'] for r in g),bias=statistics.mean(r['error'] for r in g),coverage=statistics.mean(r['lower_bound']<=r['actual']<=r['upper_bound'] for r in g)))
    csv_write(OUT/'monthly_drift_monitor.csv',monthly)
    stress=[]
    for under in [2,4,8]:
        for name in [chosen,'seasonal_naive']:
            g=[r for r in scored if r['phase']=='test' and r['model']==name]
            stress.append(dict(model=name,shortfall_cost_usd=under,cost_fixed_capacity_policy=sum(decision_cost(r['actual'],r['capacity'],under,.75) for r in g)))
    csv_write(OUT/'cost_sensitivity.csv',stress)
    chosen_summary=next(r for r in summary if r['model']==chosen);base_summary=next(r for r in summary if r['model']=='seasonal_naive')
    result=dict(source_rows=len(rows),validation_days=len(validation)//len(c['models']),test_days=len(selected),selected_model=chosen,model_selection_metric='validation WAPE only',chosen_test=chosen_summary,baseline_test=base_summary,modeled_cost_saving_usd=base_summary['modeled_decision_cost_usd']-chosen_summary['modeled_decision_cost_usd'],daily_saving_block_bootstrap_95=interval,nominal_interval_level=c['interval_level'],source_sha256=hashlib.sha256((ROOT/'data/day.csv').read_bytes()).hexdigest(),capacity_critical_ratio=critical,calibration=params)
    (OUT/'metrics.json').write_text(json.dumps(result,indent=2,sort_keys=True))
    chart=line_chart(selected);(OUT/'forecast_comparison.svg').write_text(chart)
    sections=[('Decision',f"Validation selects {chosen}; test WAPE {chosen_summary['wape']:.1%}, compared with {base_summary['wape']:.1%} for a seven-day seasonal baseline. Evaluate the operational cost result alongside forecast error; the model was selected before examining July–December test performance."),('Capacity economics',f"Using hypothetical costs of $4 per shortfall trip-equivalent and $0.75 per excess trip-equivalent, fixed validation-calibrated capacity policies imply ${result['modeled_cost_saving_usd']:,.0f} total cost reduction versus the baseline over {len(selected)} historical test days. The seven-day block bootstrap interval for mean daily saving is [${interval[0]:.2f}, ${interval[1]:.2f}]. This is a counterfactual proxy calculation, not realized operating savings."),('Leakage controls','Daily casual and registered counts sum to the target, so neither is a predictor. Observed same-day weather is also excluded because it is unavailable at the prior-day planning cutoff. Features use known calendar information and lagged rentals only. Models refit on the first forecast day of each month using strictly earlier targets. Subsequent daily predictions may use newly observed prior-day rentals, as in a prequential one-day-ahead process; no random train/test split is used.'),('Uncertainty and drift',f"Absolute validation residuals calibrate a nominal 90% band. Actual test coverage is {chosen_summary['empirical_interval_coverage']:.1%}. Temporal drift invalidates exchangeability guarantees; this is empirical calibration, not guaranteed 90% future coverage. Review monthly WAPE, bias and coverage. Bootstrap intervals are approximate historical uncertainty conditional on model, data and invented costs."),('What the capacity units mean','Capacity is daily trip-equivalent service capacity, not a bicycle count. Bikes can serve multiple trips, and the dataset has no station-level rebalancing, availability or true lost-demand observations. Historical realized rentals are the target and a limited proxy for latent demand; stockouts and unmet requests are not observed. A practical fleet-sizing decision needs trip duration, turnaround, station inventory and censored-demand estimation.'),('Data provenance','731 public daily Capital Bikeshare observations from 2011–2012, UCI Bike Sharing dataset. Retrieved from a public GitHub mirror, line endings normalized to LF, pinned with SHA-256. This historical benchmark is not current Washington ridership and does not demonstrate current commercial performance. Original dataset: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset | Fanaee-T (2013), DOI 10.24432/C5W894, CC BY 4.0. Mirror URL and exact fingerprint are in data/provenance.json.'),('Personal understanding','I can explain why a low forecast error does not automatically produce the best capacity decision: underestimating demand and paying for unused capacity have different costs. I would choose a model using a chronological validation period, turn its residuals into an explicit service-capacity rule, and judge the untouched test period on both accuracy and cost. I would also show where uncertainty bands fail instead of treating them as a guarantee.'),('Implementation gates','Use current operator data, validate information availability at the cutoff, model forecast-weather uncertainty if added, infer censored demand, and incorporate station-level inventory, maintenance and rebalancing. Pilot daily capacity recommendations with cost, trip fulfillment and distributional guardrails. Refit cadence and retraining triggers must be set before live evaluation.')]
    report('Mobility Demand Forecasting & Capacity Economics','PUBLIC HISTORICAL DATA · CHRONOLOGICAL EVALUATION · HYPOTHETICAL COSTS',sections,chart)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
