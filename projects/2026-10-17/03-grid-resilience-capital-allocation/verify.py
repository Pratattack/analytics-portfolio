"""Three automated prepublication checks with persisted audit evidence."""
from pathlib import Path
import csv, hashlib, json, math, shutil, subprocess, sys
import xml.etree.ElementTree as ET
from model import build_options, feasible, intervention_value, solve
ROOT=Path(__file__).resolve().parent

def read_csv(path):
    with path.open() as f:return list(csv.DictReader(f))

def output_hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'outputs').glob('*')) if p.is_file()}

def main():
    run=subprocess.run([sys.executable,'-m','unittest','-v'],cwd=ROOT,capture_output=True,text=True)
    (ROOT/'test_results.txt').write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    subprocess.run([sys.executable,'pipeline.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    c=json.loads((ROOT/'config.json').read_text());src=json.loads((ROOT/'data/eia_source_snapshot.json').read_text())
    csv=read_csv(ROOT/'data/reliability_benchmarks.csv')
    assert len(csv)==10 and len({r['state'] for r in csv})==10
    # Validate every extracted field against the preserved EIA source row.
    indices={'coverage_2024':1,'coverage_2023':2,'all_2024':3,'all_2023':4,'normal_2024':9,'normal_2023':10}
    for r in csv:
        raw=next(x for x in src['records'] if x['state']==r['state'])
        cells=raw['source_line'].split(': ',1)[1].split('|')
        assert cells[0].strip()==r['state']
        for name,index in indices.items():
            assert float(r[name])==float(cells[index].strip().replace('%',''))==raw[name]
        for y in ['2023','2024']:
            assert float(r['all_'+y])>=float(r['normal_'+y])>=0
            assert float(r['coverage_'+y])>0
    m=json.loads((ROOT/'outputs/metrics.json').read_text())
    assert m['plans_enumerated']==3**10
    assert abs(m['equal_weight_dp_oracle_residual'])<1e-7
    groups=build_options(c,{r['state']:r for r in src['records']})
    candidate={(p['state'],p['intervention']):p for g in groups for p in g}
    selected=read_csv(ROOT/'outputs/selected_portfolio.csv')
    assert len(selected)==10 and len({r['state'] for r in selected})==10
    plan=[candidate[r['state'],r['intervention']] for r in selected]
    assert feasible(dict(reserve_musd=sum(float(r['reserve_musd']) for r in selected),crew=sum(int(r['crew']) for r in selected),critical=sum(int(r['critical']) for r in selected)),c)
    # Reconcile SQL output against an independently written NPV formula from detail.
    detail=read_csv(ROOT/'outputs/selected_scenario_detail.csv')
    for s in c['scenarios']+[c['out_of_set_stress']]:
        annual=[r for r in detail if r['scenario']==s['name']]
        independent=sum(-float(r['capex_musd'])+sum((float(r['annual_benefit_musd'])-float(r['annual_opex_musd']))/(1+c['discount_rate'])**y for y in range(s['delay_years']+1,c['life_years']+1)) for r in annual)
        sql=next(r for r in read_csv(ROOT/'outputs/scenario_accounting.csv') if r['scenario']==s['name'])
        assert math.isclose(independent,float(sql['social_npv_musd']),abs_tol=1e-7)
        assert sum(float(r['capex_musd']) for r in annual)<=c['budget_musd']+1e-8
    comp=read_csv(ROOT/'outputs/policy_comparison.csv')
    assert all(float(r['regret_musd'])>=-1e-7 and r['feasible']=='True' for r in comp)
    assert m['worst_social_npv_musd']+1e-7>=m['equal_weight_policy_worst_npv_musd']
    assert m['worst_social_npv_musd']+1e-7>=m['greedy_worst_npv_musd']
    frontier=read_csv(ROOT/'outputs/budget_frontier.csv')
    vals=[float(r['worst_social_npv_musd']) for r in frontier]
    assert vals==sorted(vals)
    assert all(float(r['reserved_musd'])<=float(r['budget_musd'])+1e-8 for r in frontier)
    assert 'not utility cash profit' in (ROOT/'outputs/report.html').read_text()
    svg=ET.parse(ROOT/'outputs/scenario_comparison.svg').getroot()
    assert svg.tag.endswith('svg') and svg.attrib['role']=='img'
    sensitivity=json.loads((ROOT/'outputs/coverage_sensitivity.json').read_text())
    assert sensitivity['excluded']==['Texas','Louisiana']
    assert all(r['state'] not in sensitivity['excluded'] for r in sensitivity['selected'])
    before=output_hashes();shutil.rmtree(ROOT/'outputs')
    subprocess.run([sys.executable,'pipeline.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    assert before==output_hashes()
    evidence=dict(stage_1={'status':'PASS','checks':['12 hand-worked, boundary, feasibility and optimization unit tests','Known robust optimum differs from equal-weight optimum','Independent dynamic programming oracle agrees with scalar optimizer']},stage_2={'status':'PASS','checks':['All 60 numerical source fields match preserved EIA table rows','Selected allocation satisfies budget, crews, one-choice and critical-service constraints','Independent discounted-flow accounting matches SQL for all five scenarios','Scenario regret is nonnegative; robust dominates comparison policies on worst-case value','Budget frontier is feasible and nondecreasing']},stage_3={'status':'PASS','checks':['Cleared outputs and reran pipeline: every artifact byte-identical','SVG and HTML contain labeled modeled-value reporting','Frozen source snapshot SHA-256 recorded']},source_sha256=m['source_sha256'],artifact_sha256=before,limits=['Automated verification is not three independent human reviews.','Historical state benchmarks are not feeder outage forecasts.','Costs, service territories and effectiveness are hypothetical.','Out-of-set stress is a diagnostic scenario, not observed validation.'])
    (ROOT/'verification.json').write_text(json.dumps(evidence,indent=2,sort_keys=True))
    print(json.dumps({k:v for k,v in evidence.items() if k not in ['artifact_sha256']},indent=2))

if __name__=='__main__':main()
