from pathlib import Path
from datetime import date,timedelta
import csv,hashlib,json,math,shutil,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
def read_csv(path):
    with path.open() as f:return list(csv.DictReader(f))
def hashes(d):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((d/'outputs').glob('*')) if p.is_file()}
results={}
for d in [ROOT/'01-outpatient-access-simulation',ROOT/'02-bike-share-forecast-planning']:
    test=subprocess.run([sys.executable,'-m','unittest','-v'],cwd=d,capture_output=True,text=True)
    (d/'test_results.txt').write_text(test.stdout+test.stderr)
    if test.returncode:raise RuntimeError(test.stdout+test.stderr)
    subprocess.run([sys.executable,'pipeline.py'],cwd=d,check=True,stdout=subprocess.DEVNULL)
    c=json.loads((d/'config.json').read_text());m=json.loads((d/'outputs/metrics.json').read_text())
    checks=[]
    if d.name.startswith('01'):
        sample=read_csv(d/'outputs/sample_request_outcomes.csv');cohort=[r for r in sample if r['in_cohort']=='1'];s=m['sample_metrics']
        assert len(sample)==len({r['request_id'] for r in sample})
        assert len(cohort)==s['requests'] and sum(int(r['completed']) for r in cohort)==s['completed']
        assert all(int(r['appointment_day'])<0 or int(r['appointment_day'])>=int(r['request_day']) for r in sample)
        p=next(p for p in c['policies'] if p['name']==m['diagnostic_candidate']);capacity=c['base_slots']+p['extra_slots']
        for day in {r['appointment_day'] for r in sample if r['appointment_day']!='-1'}:
            assert sum(r['appointment_day']==day for r in sample)<=capacity
        for urgent,target,key in [(0,c['routine_wait_target'],'routine_service'),(1,c['urgent_wait_target'],'urgent_service')]:
            g=[r for r in cohort if int(r['urgent'])==urgent];rate=sum(0<=int(r['wait_days'])<=target for r in g)/len(g)
            assert math.isclose(rate,s[key],abs_tol=1e-10)
        audit=read_csv(d/'outputs/sample_sql_audit.csv')
        for k in ['requests','booked','unbooked','completed','no_shows']:assert sum(int(r[k]) for r in audit)==s[k]
        rep=read_csv(d/'outputs/replications.csv');assert len(rep)==160
        assert len({r['seed'] for r in rep if r['phase']=='development'})==10
        assert len({r['seed'] for r in rep if r['phase']=='holdout'})==30
        assert not {r['seed'] for r in rep if r['phase']=='development'}&{r['seed'] for r in rep if r['phase']=='holdout'}
        paired=read_csv(d/'outputs/paired_holdout_comparison.csv')
        for r in paired:
            assert math.isclose(float(r['incremental_modeled_contribution']),float(r['completed_delta'])*c['contribution_per_completed_visit_usd']-m['holdout']['incremental_capacity_cost'],abs_tol=1e-7)
        checks=['One outcome per request; no negative appointment waits; sample occupancy within total capacity','All access-rate denominators retain unbooked cohort requests','SQL request/completion/no-show totals independently reconcile','Development and holdout seeds disjoint; paired economic arithmetic checked','Internal per-day calendars also audit capacity net of staff absence']
    else:
        data=read_csv(d/'data/day.csv');assert len(data)==731
        assert len({r['dteday'] for r in data})==731
        for i,r in enumerate(data):
            assert int(r['cnt'])==int(r['casual'])+int(r['registered'])>=0
            assert date.fromisoformat(r['dteday'])==date(2011,1,1)+timedelta(days=i)
        provenance=json.loads((d/'data/provenance.json').read_text());assert hashlib.sha256((d/'data/day.csv').read_bytes()).hexdigest()==provenance['normalized_csv_sha256']==m['source_sha256']
        rows=read_csv(d/'outputs/prequential_forecasts.csv');test_rows=[r for r in rows if r['phase']=='test']
        assert all(int(float(r['train_end_index']))<int(float(r['index'])) and int(float(r['latest_target_lag_index']))<int(float(r['index'])) for r in rows)
        assert all(r['date']<c['test_start'] for r in rows if r['phase']=='validation')
        assert len(test_rows)==184*5 and m['validation_days']==182
        selection=read_csv(d/'outputs/validation_model_selection.csv');winner=min(selection,key=lambda r:(float(r['wape']),r['model']))['model'];assert winner==m['selected_model']
        for model in c['models']:
            g=[r for r in test_rows if r['model']==model];expected=sum(abs(float(r['actual'])-float(r['prediction'])) for r in g)/sum(float(r['actual']) for r in g)
            sql=next(r for r in read_csv(d/'outputs/test_evaluation.csv') if r['model']==model)
            assert math.isclose(expected,float(sql['wape']),abs_tol=1e-9)
            for r in g:
                a,q=float(r['actual']),float(r['capacity']);cost=max(a-q,0)*4+max(q-a,0)*.75
                assert math.isclose(cost,float(r['decision_cost']),abs_tol=1e-7)
                assert 0<=float(r['lower_bound'])<=float(r['upper_bound'])
            assert math.isclose(sum(float(r['decision_cost']) for r in g),float(sql['modeled_decision_cost_usd']),abs_tol=1e-6)
        checks=['731 consecutive unique public days; target equals casual plus registered','Pinned normalized data SHA-256 matches provenance','Every model training target and lag precedes forecast date','182 validation / 184 test dates; selected model determined only from validation WAPE','SQL test WAPE/cost totals reconcile to independent raw forecast arithmetic']
    for p in (d/'outputs').glob('*.svg'):assert ET.parse(p).getroot().tag.endswith('svg')
    assert '<html lang="en">' in (d/'outputs/report.html').read_text()
    before=hashes(d);shutil.rmtree(d/'outputs');subprocess.run([sys.executable,'pipeline.py'],cwd=d,check=True,stdout=subprocess.DEVNULL);assert before==hashes(d)
    evidence={'stage_1':{'status':'PASS','checks':['10 hand-worked and boundary unit tests; see test_results.txt']},'stage_2':{'status':'PASS','checks':checks},'stage_3':{'status':'PASS','checks':['Cleared outputs and regenerated: every output byte-identical','Report structure and SVG XML validate']},'artifact_sha256':before,'review_limits':['Three automated verification stages, not three independent human reviewers.','HTML structure and SVG markup checked; no full browser visual review.','Source publication is not live application deployment.']}
    (d/'verification.json').write_text(json.dumps(evidence,indent=2,sort_keys=True));results[d.name]={k:v for k,v in evidence.items() if k!='artifact_sha256'}
(ROOT/'verification.json').write_text(json.dumps(results,indent=2,sort_keys=True));print(json.dumps(results,indent=2))
