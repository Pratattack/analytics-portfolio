from pathlib import Path
import csv,hashlib,json,math,subprocess,sys,sqlite3,xml.etree.ElementTree as ET
import openpyxl
from analysis import read_panel,valid,score
ROOT=Path(__file__).resolve().parent
def read_csv(p):
    with p.open() as f:return list(csv.DictReader(f))
def run(script):subprocess.run([sys.executable,script],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'outputs').glob('*')) if p.is_file()}
def main():
    pinned=json.loads((ROOT/'data/workbook_manifest.json').read_text())
    for item in pinned:
        assert hashlib.sha256((ROOT/'data/raw'/item['file']).read_bytes()).hexdigest()==item['sha256'],'Pinned source workbook changed; review the new release before regenerating manifests'
    run('etl.py');run('analysis.py');run('export_workbench.py');run('report.py')
    test=subprocess.run([sys.executable,'-m','unittest','-v'],cwd=ROOT,capture_output=True,text=True);(ROOT/'test_results.txt').write_text(test.stdout+test.stderr)
    if test.returncode:raise RuntimeError(test.stdout+test.stderr)
    rows=read_panel();assert len(rows)==11552;assert len({(r['year'],r['utility_id'],r['state'],r['standard']) for r in rows})==len(rows)
    manifests=json.loads((ROOT/'data/workbook_manifest.json').read_text());books={}
    for item in manifests:
        p=ROOT/'data/raw'/item['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
        b=openpyxl.load_workbook(p,read_only=True,data_only=True);books[p.name]=list(b['Reliability_States'].values);b.close()
    def parse(x):return None if x is None or x in ['.',''] else float(x)
    # Independent cell-level re-read: different parsing routine from etl.number.
    for r in rows:
        source=books[r['source_file']][r['source_row']-1];assert source[1]==r['utility_id'] and source[3]==r['state']
        a,n,c=(5,8,14) if r['standard']=='IEEE' else (17,20,23)
        assert parse(source[a])==r['saidi_all'];assert parse(source[n])==r['saidi_normal'];assert parse(source[c])==r['customers']
    m=json.loads((ROOT/'outputs/metrics.json').read_text());recon=read_csv(ROOT/'outputs/published_state_reconciliation.csv')
    assert len(recon)==153 and all(r['within_rounding_tolerance']=='True' for r in recon if r['year'] in ['2023','2024'])
    assert sum(r['within_rounding_tolerance']=='False' for r in recon)==26
    assert m['decision_view_year']==2024 and m['quarantined_years']==[2025]
    predictions=read_csv(ROOT/'outputs/report_year_predictions.csv')
    assert all(int(r['last_input_year'])<int(r['target_year']) for r in predictions)
    targets=[r for r in predictions if r['model']==m['selected_model'] and r['target_year']=='2025']
    independent=sum(abs(float(r['actual'])-float(r['prediction']))*float(r['lag_customers']) for r in targets)/sum(float(r['lag_customers']) for r in targets)
    assert math.isclose(independent,m['selected_test']['lag_customer_weighted_mae'],abs_tol=1e-8)
    assert m['bootstrap']['percentile_95'][0]<0<m['bootstrap']['percentile_95'][1] and not m['predictive_component_promotable']
    # Reconcile every normal-day SQL aggregate to normalized records.
    sql=read_csv(ROOT/'outputs/state_weighted_reliability.csv')
    for s in sql:
        g=[r for r in rows if valid(r) and r['year']==int(float(s['year'])) and r['state']==s['state']]
        mean=sum(r['saidi_normal']*r['customers'] for r in g)/sum(r['customers'] for r in g)
        assert math.isclose(mean,float(s['weighted_normal_saidi_minutes']),abs_tol=1e-7)
    for p in (ROOT/'outputs').glob('*.svg'):ET.parse(p)
    workbench=(ROOT/'outputs/workbench.html').read_text();assert 'fetch(url)' not in workbench and 'OFFLINE=' in workbench and 'quarantined' in workbench
    before=hashes()
    # Remove derived DB to make its byte layout deterministic on rebuild.
    for p in (ROOT/'outputs').iterdir():
        if p.is_file():p.unlink()
    run('analysis.py');run('export_workbench.py');run('report.py');after=hashes()
    assert before==after,[name for name in before if before[name]!=after.get(name)]
    evidence=dict(stage_1=dict(status='PASS',checks=['Six official workbooks hash-verified','11,552 normalized rows independently compared to original cells','Unique utility/state/year/standard key; missing is never zero']),stage_2=dict(status='PASS',checks=['17 numerical, leakage, peer exclusion, quarantine, API and HTTP tests','All state SQL totals independently recomputed','Report-year cutoffs and held-out weighted error verified']),stage_3=dict(status='PASS',checks=['All derived artifacts deleted and rebuilt byte-identically','SVG XML and offline workbench structure checked']),decision_gates=dict(accepted_view=2024,quarantined_release=2025,unresolved_state_reconciliations=26,predictive_promotion=False),artifact_sha256=after,review_limits=['Real browser execution is tracked separately by the flagship-browser-acceptance CI job; consult its actual result and evidence for this commit.','2025 discrepancies remain unexplained, and that release is excluded from decision inputs.','Three automated stages are not independent external validation.'])
    (ROOT/'verification.json').write_text(json.dumps(evidence,indent=2,sort_keys=True));print(json.dumps({k:v for k,v in evidence.items() if k!='artifact_sha256'},indent=2))
if __name__=='__main__':main()
