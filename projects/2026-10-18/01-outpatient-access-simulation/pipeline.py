from common import *
from model import generate,simulate
import sqlite3

def main():
    OUT.mkdir(exist_ok=True);c=json.loads((ROOT/'config.json').read_text());all_rows=[];sample={};records_for_sample=None
    for seed in range(40):
        req,absence=generate(c,10000+seed)
        for p in c['policies']:
            result,records=simulate(c,p,req,absence)
            all_rows.append(dict(seed=seed,phase='development' if seed<10 else 'holdout',policy=p['name'],**result))
            if seed==10:sample[p['name']]=(result,records)
    csv_write(OUT/'replications.csv',all_rows)
    summaries=[]
    for p in c['policies']:
        for phase in ['development','holdout']:
            group=[r for r in all_rows if r['policy']==p['name'] and r['phase']==phase]
            summaries.append(dict(policy=p['name'],phase=phase,replications=len(group),**{k:statistics.mean(r[k] for r in group) for k in ['urgent_service','routine_service','mean_booked_wait','completed','unbooked','incremental_capacity_cost']}))
    csv_write(OUT/'policy_summary.csv',summaries)
    eligible=[r for r in summaries if r['phase']=='development' and r['urgent_service']>=c['minimum_urgent_service'] and r['routine_service']>=c['minimum_routine_service']]
    selected=min(eligible,key=lambda r:r['incremental_capacity_cost'])['policy'] if eligible else None
    # If none passes development, retain the candidate with highest minimum access rate for diagnosis only.
    diagnostic=max([r for r in summaries if r['phase']=='development'],key=lambda r:min(r['urgent_service'],r['routine_service']))['policy']
    name=selected or diagnostic
    base=[r for r in all_rows if r['policy']=='fcfs' and r['phase']=='holdout'];chosen=[r for r in all_rows if r['policy']==name and r['phase']=='holdout']
    pairs=[]
    for a,b in zip(base,chosen):
        assert a['seed']==b['seed']
        pairs.append(dict(seed=a['seed'],urgent_service_delta=b['urgent_service']-a['urgent_service'],routine_service_delta=b['routine_service']-a['routine_service'],completed_delta=b['completed']-a['completed'],incremental_modeled_contribution=(b['completed']-a['completed'])*c['contribution_per_completed_visit_usd']-b['incremental_capacity_cost']))
    csv_write(OUT/'paired_holdout_comparison.csv',pairs)
    chosen_summary=next(r for r in summaries if r['phase']=='holdout' and r['policy']==name)
    stress=[]
    p=next(p for p in c['policies'] if p['name']==name)
    for scenario,factor,absence_prob in [('demand_plus_20pct',1.2,.08),('staff_absence',1.,.25),('joint_stress',1.2,.25)]:
        for seed in range(10):
            req,absence=generate(c,20000+seed,factor,absence_prob);result,_=simulate(c,p,req,absence)
            stress.append(dict(scenario=scenario,seed=seed,**result))
    csv_write(OUT/'stress_tests.csv',stress)
    result,records=sample[name];csv_write(OUT/'sample_request_outcomes.csv',records)
    db=sqlite3.connect(':memory:');db.execute('CREATE TABLE outcomes(request_id INT PRIMARY KEY,request_day INT,urgent INT,appointment_day INT,wait_days INT,completed INT,in_cohort INT,slot_class TEXT)')
    db.executemany('INSERT INTO outcomes VALUES (:request_id,:request_day,:urgent,:appointment_day,:wait_days,:completed,:in_cohort,:slot_class)',records)
    cur=db.execute((ROOT/'analysis.sql').read_text());sql=[dict(zip([x[0] for x in cur.description],r)) for r in cur];csv_write(OUT/'sample_sql_audit.csv',sql)
    metrics=dict(selected_policy=selected,diagnostic_candidate=name,development_eligible=len(eligible),holdout=chosen_summary,paired_95_mc_intervals={k:mean_ci([r[k] for r in pairs]) for k in ['urgent_service_delta','routine_service_delta','completed_delta','incremental_modeled_contribution']},holdout_targets_met=chosen_summary['urgent_service']>=.9 and chosen_summary['routine_service']>=.9,sample_metrics=result,replication_count=len(all_rows),stress_replications=len(stress),config_sha256=hashlib.sha256((ROOT/'config.json').read_bytes()).hexdigest())
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2,sort_keys=True))
    chart=bars('Holdout routine appointments booked within seven business days (%)',[(r['policy'],100*r['routine_service']) for r in summaries if r['phase']=='holdout']);(OUT/'access_comparison.svg').write_text(chart)
    sections=[('Decision',f"Development-selected policy: {selected or 'none passes both access targets'}. Holdout target pass: {metrics['holdout_targets_met']}. Diagnostic candidate: {name}. Choose the least-cost policy meeting both 90% booking targets in development, then inspect separate holdout performance before a pilot. Do not deploy a failing policy simply because it ranks best."),('Holdout outcomes',f"Across 30 independent holdout replications: urgent within one business day {chosen_summary['urgent_service']:.1%}; routine within seven business days {chosen_summary['routine_service']:.1%}; mean booked wait {chosen_summary['mean_booked_wait']:.2f} business days. Average unbooked cohort requests at the horizon: {chosen_summary['unbooked']:.2f}. Booked-wait averages exclude unbooked requests, so access rates retain all cohort requests in their denominators."),('Financial tradeoff',f"Paired mean incremental modeled contribution versus FCFS: ${metrics['paired_95_mc_intervals']['incremental_modeled_contribution'][0]:,.0f}; approximate 95% Monte Carlo interval [${metrics['paired_95_mc_intervals']['incremental_modeled_contribution'][1]:,.0f}, ${metrics['paired_95_mc_intervals']['incremental_modeled_contribution'][2]:,.0f}]. Assumptions: $75 contribution per completed visit, $65 per extra staffed slot per evaluation business day, and one-time setup. This is not observed revenue, clinical benefit or a complete provider P&L. Access improvement may justify a cost even without positive modeled contribution."),('Experiment and measurement design','Ten development replications select a policy; thirty disjoint holdout replications evaluate it. Common random request and absence streams make comparisons paired. Intervals describe simulation uncertainty conditional on invented parameters, not causal clinical effectiveness. A request is counted as timely access when booked within its target, regardless of attendance; completed visits and no-shows are reported separately.'),('Stress and capacity','Three stress cases test 20% higher arrivals, more frequent absence and both together, each with ten replications. A booking-calendar audit enforces physical capacity. Business-day steps represent booking access; there is no intraday queue, patient acuity prediction, treatment allocation, emergency workflow, clinician continuity or downstream referral model.'),('Data and assumptions','All requests, urgency labels, no-show probabilities and staffing assumptions are synthetic. Urgency is an exogenous administrative request label, not a clinical classification inferred by the model. A 40-day warmup precedes the 160-business-day evaluation cohort, followed by a drain period. Every request has one outcome; unbooked requests are explicitly censored, not erased. Capacity lost to absence is assumed known when booking, an optimistic limitation requiring prospective real-world testing.'),('Personal understanding','I can explain why protecting same-day slots can improve urgent access while unintentionally worsening routine access or leaving capacity unused. Releasing unused reserved slots and adding capacity address different causes. I would examine both patient groups, no-shows, unbooked requests and staffing costs rather than presenting a single average wait as success.'),('Implementation gates','Validate arrival, cancellation, no-show and staffing distributions using governed operational data; engage scheduling and clinical leaders to define appropriate service targets; test continuity and patient preferences; then run a time-limited operational pilot with predefined access, staff workload and equity guardrails. The simulation provides a planning case, not a clinical scheduling instruction.'),('Source context','AHRQ, Open Access Scheduling for Routine and Urgent Appointments: https://www.ahrq.gov/cahps/quality-improvement/improvement-guide/6-strategies-for-improving/access/strategy6a-openaccess.html (reviewed 2026-10-18). It motivates measuring demand and available appointment slots; none of its reported case-study outcomes calibrate this simulation.')]
    report('Outpatient Access & Capacity: Test the Policy Before the Pilot','SYNTHETIC OPERATIONS CASE · PAIRED SIMULATION · NO PATIENT DATA',sections,chart)
    print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
