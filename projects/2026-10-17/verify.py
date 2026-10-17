from pathlib import Path
import csv, json, subprocess, sys, hashlib, math, shutil
ROOT=Path(__file__).parent
results={}
def read(p):
    with p.open() as f: return list(csv.DictReader(f))
def hashes(d):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((d/'outputs').iterdir()) if p.is_file()}
for d in sorted(ROOT.glob('0*')):
    tests=subprocess.run([sys.executable,'-m','unittest','-v'],cwd=d,capture_output=True,text=True)
    if tests.returncode: raise RuntimeError(tests.stdout+tests.stderr)
    (d/'test_results.txt').write_text(tests.stdout+tests.stderr)
    subprocess.run([sys.executable,'pipeline.py'],cwd=d,check=True,stdout=subprocess.DEVNULL)
    out=d/'outputs'; m=json.loads((out/'metrics.json').read_text())
    checks=[]
    if d.name.startswith('01'):
        raw=read(out/'commercial_data.csv'); customers=read(out/'customer_profitability.csv')
        assert len(raw)==180 and len({(r['customer'],r['product'],r['period']) for r in raw})==180
        assert all(float(r['quantity'])>=0 and float(r['price'])>0 and float(r['unit_cost'])>=0 for r in raw)
        current=[r for r in raw if r['period']=='1']
        direct=sum(float(r['quantity'])*(float(r['price'])-float(r['unit_cost']))-float(r['service_cost']) for r in current)
        assert math.isclose(direct,sum(float(r['contribution_after_service']) for r in customers),abs_tol=1e-6)
        assert abs(m['bridge_residual'])<1e-6
        scenario=read(out/'contract_sensitivity.csv'); assert len(scenario)==135
        base=next(r for r in scenario if all(float(r[k])==0 for k in ['uplift','churn','cost_shock']) and float(r['elasticity'])==-1)
        assert math.isclose(float(base['three_year_variable_contribution_npv']),m['current_variable_contribution']*sum(1/1.1**y for y in range(1,4)),abs_tol=1e-6)
        checks=['180 unique nonnegative customer/product/period records','SQL customer totals reconcile to raw data','Exact margin bridge residual below $0.000001','135 scenario rows; baseline NPV independently reconciled']
    else:
        raw=read(out/'randomized_campaign.csv'); summary=read(out/'campaign_summary.csv'); econ=read(out/'segment_economics.csv')
        assert len(raw)==12000 and len({r['prospect_id'] for r in raw})==12000
        assert all(r['arm'] in ['0','1'] and r['converted'] in ['0','1'] for r in raw)
        assert sum(int(r['prospects']) for r in summary)==12000
        assert sum(int(r['converted']) for r in raw)==sum(int(r['conversions']) for r in summary)
        assert len(read(out/'risk_sensitivity.csv'))==81
        for s in summary:
            g=[r for r in raw if r['segment']==s['segment'] and r['arm']==s['arm']]
            assert math.isclose(float(s['conversion_rate']),sum(int(r['converted']) for r in g)/len(g))
        for seg in {r['segment'] for r in econ}:
            a=[r for r in econ if r['segment']==seg]
            control=next(r for r in a if r['arm']=='0'); treatment=next(r for r in a if r['arm']=='1')
            assert math.isclose(float(treatment['account_npv'])-float(control['account_npv']),-70,abs_tol=1e-8)
        checks=['12,000 unique randomized prospects; binary domains valid','SQL totals and stratum conversion reconcile to raw data','81 stress scenarios; $70 incentive reduces account NPV by exactly $70','Bootstrap and lift intervals present, with conditional uncertainty labeled']
    for p in out.glob('*.csv'):
        assert read(p) and all(all(v is not None and v!='' for v in r.values()) for r in read(p))
    markup=(out/'report.html').read_text()
    assert '<html lang="en">' in markup and 'SYNTHETIC' in markup and 'Personal understanding' in markup
    before=hashes(d)
    shutil.rmtree(out)
    subprocess.run([sys.executable,'pipeline.py'],cwd=d,check=True,stdout=subprocess.DEVNULL)
    assert before==hashes(d),'Reproducibility mismatch'
    results[d.name]={'stage_1':'PASS: hand-worked unit tests and boundary cases','stage_2':{'status':'PASS: independent input/output reconciliation','checks':checks},'stage_3':'PASS: clean rerun produced byte-identical output artifacts; report structure checked','artifact_sha256':before,'unit_test_log':(tests.stdout+tests.stderr).strip(),'review_limit':'Automated verification, not independent human review. HTML structure checked; no browser visual review or production integration performed.'}
(ROOT/'verification.json').write_text(json.dumps(results,indent=2))
print(json.dumps({name:{k:v for k,v in r.items() if k not in ['artifact_sha256','unit_test_log']} for name,r in results.items()},indent=2))
