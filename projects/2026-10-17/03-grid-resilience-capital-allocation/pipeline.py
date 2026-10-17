from pathlib import Path
import csv, hashlib, html, json, sqlite3
from model import build_options, evaluate, feasible, greedy, independent_equal_weight_dp, intervention_value, solve

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'

def csv_write(path,rows):
    rows=list(rows)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def bar_chart(plans,names):
    width=860; top=62; rowh=38
    values=[(f'{p} / {s}',v) for p,d in plans.items() for s,v in zip(names,d['totals']['values'])]
    low=min(0,min(v for _,v in values));high=max(v for _,v in values)
    left=290; span=510
    def x(v):return left+(v-low)/(high-low)*span
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {top+len(values)*rowh+40}" role="img" aria-label="Scenario social net present value by portfolio"><rect width="100%" height="100%" fill="#ffffff"/><text x="22" y="28" font-family="sans-serif" font-size="19">Scenario social NPV · USD millions (modeled)</text><line x1="{x(0)}" y1="45" x2="{x(0)}" y2="{top+len(values)*rowh}" stroke="#718096"/>']
    for i,(label,v) in enumerate(values):
        y=top+i*rowh; color='#087f8c' if label.startswith('robust') else '#587093'
        svg.append(f'<text x="22" y="{y+17}" font-family="sans-serif" font-size="12">{html.escape(label)}</text><rect x="{min(x(0),x(v))}" y="{y}" width="{abs(x(v)-x(0))}" height="23" fill="{color}"/><text x="{x(v)+5}" y="{y+17}" font-family="sans-serif" font-size="12">{v:.2f}</text>')
    svg.append('</svg>');return ''.join(svg)

def main():
    OUT.mkdir(exist_ok=True)
    c=json.loads((ROOT/'config.json').read_text()); source=json.loads((ROOT/'data/eia_source_snapshot.json').read_text())
    benchmarks={r['state']:r for r in source['records']}
    csv_write(ROOT/'data/reliability_benchmarks.csv',[{k:v for k,v in r.items() if k!='source_line'} for r in source['records']])
    groups=build_options(c,benchmarks)
    robust=solve(groups,c);equal=solve(groups,c,objective='equal_weight');g=greedy(groups,c)
    oracle=independent_equal_weight_dp(groups,c)
    assert abs(oracle-equal['score'])<1e-7
    plans={'robust':robust,'equal_weight':equal,'greedy':g}
    names=[s['name'] for s in c['scenarios']]
    candidates=[]
    for group in groups:
        for p in group[1:]:
            candidates.append({k:v for k,v in p.items() if k!='values'}|{name+'_npv_musd':v for name,v in zip(names,p['values'])})
    csv_write(OUT/'candidate_economics.csv',candidates)
    csv_write(OUT/'selected_portfolio.csv',[{k:v for k,v in p.items() if k!='values'} for p in robust['plan']])
    sql_rows=[]
    for p in robust['plan']:
        if p['intervention']=='none':continue
        district=next(d for d in c['districts'] if d['state']==p['state'])
        option=next(o for o in c['interventions'] if o['name']==p['intervention'])
        for scenario in c['scenarios']+[c['out_of_set_stress']]:
            vals=intervention_value(district,option,scenario,benchmarks[p['state']],c)
            sql_rows.append(dict(state=p['state'],intervention=p['intervention'],scenario=scenario['name'],**vals))
    csv_write(OUT/'selected_scenario_detail.csv',sql_rows)
    db=sqlite3.connect(':memory:')
    fields=list(sql_rows[0]);db.execute('CREATE TABLE selected ('+','.join(k+(' TEXT' if k in ['state','intervention','scenario'] else ' REAL') for k in fields)+')')
    db.executemany('INSERT INTO selected VALUES ('+','.join(':'+k for k in fields)+')',sql_rows)
    cur=db.execute((ROOT/'analysis.sql').read_text());totals=[dict(zip([x[0] for x in cur.description],row)) for row in cur]
    csv_write(OUT/'scenario_accounting.csv',totals)
    for name,value in zip(names,robust['totals']['values']):
        assert abs(next(r['social_npv_musd'] for r in totals if r['scenario']==name)-value)<1e-7
    frontier=[]
    for budget in [8,12,16,20,24,28]:
        p=solve(groups,c,budget=budget)
        frontier.append(dict(budget_musd=budget,reserved_musd=p['totals']['reserve_musd'],worst_social_npv_musd=p['score'],crew=p['totals']['crew'],projects=sum(x['intervention']!='none' for x in p['plan'])))
    csv_write(OUT/'budget_frontier.csv',frontier)
    scenario_opt=[solve(groups,c,objective='scenario',scenario_index=i)['score'] for i in range(len(names))]
    comparison=[]
    for policy,p in plans.items():
        for i,name in enumerate(names):
            comparison.append(dict(policy=policy,scenario=name,social_npv_musd=p['totals']['values'][i],scenario_oracle_npv_musd=scenario_opt[i],regret_musd=scenario_opt[i]-p['totals']['values'][i],feasible=feasible(p['totals'],c)))
    csv_write(OUT/'policy_comparison.csv',comparison)
    # Evaluate the fixed selected allocation outside the uncertainty set; no reoptimization.
    external=next(r for r in totals if r['scenario']==c['out_of_set_stress']['name'])
    # Fixed-allocation benefit multiplier needed for break-even in execution downside.
    downside=next(r for r in totals if r['scenario']=='execution_downside')
    # Recompute the PV of gross benefit, since delay affects all annual cash flows.
    s=c['scenarios'][-1];pv_factor=sum((1+c['discount_rate'])**(-t) for t in range(1,c['life_years']+1) if t>s['delay_years'])
    break_even=(downside['capex_musd']+downside['annual_opex_musd']*pv_factor)/(downside['annual_social_benefit_musd']*pv_factor)
    stress=[]
    for multiplier in [.5,.75,1.,1.25,1.5]:
        changed=json.loads(json.dumps(c));changed['value_per_customer_hour_usd']*=multiplier
        p=solve(build_options(changed,benchmarks),changed)
        stress.append(dict(value_per_customer_hour_usd=changed['value_per_customer_hour_usd'],worst_social_npv_musd=p['score'],reserved_musd=p['totals']['reserve_musd'],selected=';'.join(x['state']+':'+x['intervention'] for x in p['plan'] if x['intervention']!='none')))
    csv_write(OUT/'valuation_sensitivity.csv',stress)
    screened=json.loads(json.dumps(c))
    screened['districts']=[d for d in c['districts'] if min(benchmarks[d['state']]['coverage_2023'],benchmarks[d['state']]['coverage_2024'])>=80]
    screened_plan=solve(build_options(screened,benchmarks),screened)
    coverage_case=dict(rule='Exclude states with IEEE reporting coverage below 80% in either year; illustrative screening rule, not an EIA quality threshold',excluded=[d['state'] for d in c['districts'] if d not in screened['districts']],worst_social_npv_musd=screened_plan['score'],reserved_musd=screened_plan['totals']['reserve_musd'],selected=[{'state':p['state'],'intervention':p['intervention']} for p in screened_plan['plan'] if p['intervention']!='none'])
    (OUT/'coverage_sensitivity.json').write_text(json.dumps(coverage_case,indent=2,sort_keys=True))
    summary=dict(selected=[{'state':p['state'],'intervention':p['intervention']} for p in robust['plan'] if p['intervention']!='none'],budget_musd=c['budget_musd'],reserved_musd=robust['totals']['reserve_musd'],crew=robust['totals']['crew'],critical_districts=robust['totals']['critical'],worst_social_npv_musd=robust['score'],equal_weight_policy_worst_npv_musd=min(equal['totals']['values']),greedy_worst_npv_musd=min(g['totals']['values']),equal_weight_npv_musd=sum(robust['totals']['values'])/len(names),external_stress_npv_musd=external['social_npv_musd'],downside_fixed_plan_break_even_hour_value_usd=break_even*c['value_per_customer_hour_usd'],plans_enumerated=robust['enumerated'],feasible_plans=robust['feasible_count'],equal_weight_dp_oracle_residual=oracle-equal['score'],source_sha256=hashlib.sha256((ROOT/'data/eia_source_snapshot.json').read_bytes()).hexdigest())
    (OUT/'metrics.json').write_text(json.dumps(summary,indent=2,sort_keys=True))
    chart=bar_chart(plans,names);(OUT/'scenario_comparison.svg').write_text(chart)
    selected='; '.join(p['state']+' — '+p['intervention'] for p in robust['plan'] if p['intervention']!='none')
    sections=[
      ('Investment recommendation',f"Reserve ${summary['reserved_musd']:.2f}m of the $20.00m envelope and {summary['crew']} of 14 crew units. Select {len(summary['selected'])} upgrades, including {summary['critical_districts']} critical-service districts. Finite-scenario worst social NPV is ${summary['worst_social_npv_musd']:.2f}m. This is a conditional screening recommendation; stage-gate engineering validation before committing capital."),
      ('Selected allocation',selected),
      ('Why optimization matters',f"The solver checks all {summary['plans_enumerated']:,} allocations and finds {summary['feasible_plans']:,} feasible plans. It maximizes the minimum social NPV across four explicit scenarios, subject to budget, crew capacity, one intervention per district and a two-critical-district floor. Equal-weight optimization and an independent dynamic-programming oracle agree to {summary['equal_weight_dp_oracle_residual']:.10f}m. Equal scenario weights are a comparison assumption, not estimated probabilities."),
      ('Tradeoffs and outside-set risk',f"Worst social NPV: robust ${summary['worst_social_npv_musd']:.2f}m; equal-weight policy ${summary['equal_weight_policy_worst_npv_musd']:.2f}m; feasible greedy baseline ${summary['greedy_worst_npv_musd']:.2f}m. Outside-set joint stress gives ${summary['external_stress_npv_musd']:.2f}m without changing the chosen plan. Robustness is limited to the stated set; it is not protection against every future outcome. Under execution downside, the fixed plan breaks even at an assumed outage value of ${summary['downside_fixed_plan_break_even_hour_value_usd']:.2f}/customer-hour."),
      ('Observed data vs modeled assumptions','Observed: EIA 2024/2023 IEEE-method state SAIDI and reporting coverage for ten purposively selected states. Assumed: ten fictional service districts, customers, critical-service flags, costs, intervention effectiveness, outage valuation, 10-year useful life, 7% discount rate and scenarios. State benchmarks are proxies, not feeder forecasts or utility-specific measurements. Texas and Louisiana coverage is below 80%; no coverage adjustment is applied. All-event minus no-major-event SAIDI is an analytical contrast, not an exact physical attribution to storms.'),
      ('Reporting-coverage sensitivity',f"Excluding Texas and Louisiana under an illustrative 80% reporting-coverage screen changes the selected set to {coverage_case['selected']}, with worst modeled social NPV ${coverage_case['worst_social_npv_musd']:.2f}m and reserve ${coverage_case['reserved_musd']:.2f}m. The 80% screen is an analyst assumption, not an EIA quality standard. This checks recommendation sensitivity to data completeness rather than pretending the missing reporting can be repaired by scaling SAIDI."),
      ('Value definition and accounting','Avoided customer-hours × assumed value/customer-hour = annual social benefit. Social NPV subtracts project capex and ongoing O&M; it is not utility profit, tariff revenue or a rate-case return. Capex is paid at time zero. Delay removes early operating years from a fixed ten-year evaluation horizon. The 20% budget reserve is capacity held, not an additional expenditure deducted from NPV. No terminal value, tax, financing, capital replacement or benefits outside outage duration are included.'),
      ('Decision gates and delivery plan','Gate 1: obtain feeder outage logs and customer segmentation; validate reporting completeness. Gate 2: engineering estimates and causal effectiveness evidence; quantify overlap and project dependencies. Gate 3: finance/regulatory review of valuation and cost recovery, permitting and resource schedule. Pilot a small package, then compare weather-adjusted interruption duration and realized costs against pre-registered baselines; do not attribute before/after changes to the upgrade alone.'),
      ('Personal understanding','I can explain why the highest individual return does not necessarily produce the best portfolio: projects compete for budget and delivery crews, while service commitments impose constraints. This model makes those tradeoffs explicit and chooses an allocation that remains strongest in its worst modeled scenario. I would present the assumptions beside the recommendation rather than call the result a guaranteed return.'),
      ('Interview defense','If asked why I did not build a machine-learning predictor, I would explain that two annual aggregate observations do not support a credible feeder-outage forecasting claim. The appropriate contribution here is transparent decision optimization, data lineage, counterfactual scenario testing, and independently checked calculations. The next useful data are feeder-level historical outages, treatment timing, asset condition and engineering cost estimates.'),
      ('Source and freshness',source['source_url']+' | EIA Electric Power Annual Table 11.2 (2024/2023 snapshot), retrieved 2026-10-17. Pinned historical data, not a claim that 2024 is the latest available release. Original selected rows and a SHA-256 fingerprint are bundled. No proprietary data or employer endorsement.')]
    memo='# Grid Resilience Capital Allocation\n\nPUBLIC BENCHMARKS + HYPOTHETICAL INVESTMENTS | USD | 2026-10-17\n\n'
    for h,b in sections:memo+='## '+h+'\n\n'+b+'\n\n'
    (OUT/'executive_memo.md').write_text(memo)
    html_sections=''.join('<section><h2>'+html.escape(h)+'</h2><p>'+html.escape(b)+'</p></section>' for h,b in sections)
    table='<table><tr><th>Budget ($m)</th><th>Reserved ($m)</th><th>Worst social NPV ($m)</th></tr>'+''.join(f"<tr><td>{r['budget_musd']}</td><td>{r['reserved_musd']:.2f}</td><td>{r['worst_social_npv_musd']:.2f}</td></tr>" for r in frontier)+'</table>'
    report='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Grid Resilience | Investment Committee</title><style>body{margin:0;background:#edf2f6;color:#142e43;font:16px/1.6 system-ui}main{max-width:1100px;margin:auto;padding:36px 24px}header,section,figure{background:white;border:1px solid #dce4eb;border-radius:12px;padding:26px;margin:20px 0}header{border-top:7px solid #087f8c}h1{font-size:40px;line-height:1.15;max-width:800px}h2{color:#087f8c}p{white-space:pre-wrap}small{letter-spacing:.08em;color:#537186}svg{display:block;width:100%;height:auto}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px;border-bottom:1px solid #dce4eb}a{color:#006e7a}@media(max-width:600px){h1{font-size:30px}main{padding:16px}section,figure,header{padding:18px}}</style><main><header><small>INVESTMENT COMMITTEE CASE · ELECTRIC UTILITIES</small><h1>Spend the resilience budget where it holds up under stress.</h1><p>Exact portfolio optimization using public reliability benchmarks and transparent investment assumptions.</p><strong>Public data + hypothetical investments. Social value, not utility cash profit.</strong></header><figure>'+chart+'</figure><section><h2>Budget frontier</h2>'+table+'</section>'+html_sections+'</main></html>'
    (OUT/'report.html').write_text(report)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
