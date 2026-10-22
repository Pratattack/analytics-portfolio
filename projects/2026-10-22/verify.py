"""Three-stage verification. Browser execution is separate and never inferred here."""
import subprocess,sys,tempfile,shutil,json,hashlib,csv
from pathlib import Path
from config import ROOT,LAND,HOTEL

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def call(p,*args,cwd=None):subprocess.run([sys.executable,str(p),*args],check=True,cwd=cwd)
if __name__=='__main__':
 call(ROOT/'analyze.py');call(ROOT/'presentation.py')
 # Stage 1: hashes/schema/semantic reconciliation in extraction and independent recorded source audit.
 for project in [LAND,HOTEL]:
  r=ROOT/project;a=json.loads((r/'data/original_html_audit.json').read_text());assert a['status']=='PASS'
  with (r/'outputs/source_lineage.csv').open() as f:lineage=list(csv.DictReader(f))
  assert len(lineage)==a['operands'];assert all(x['status']=='PASS' for x in a['checks'])
  expected={(x['record'],x['metric'],int(x['cell_index']),x['accession']) for x in lineage};actual={(x['record'],x['metric'],x['element_index'],x['accession']) for x in a['checks']};assert actual==expected
  manifests={x['accession']:x for x in json.loads((r/'data/source_manifest.json').read_text())}
  for x in a['checks']:assert x['original_html_sha256']==manifests[x['accession']]['original_html_sha256']
 print('STAGE 1 PASS: pinned inputs, dimensions, currency, declared precision, scope sums, retained exclusions; recorded independent original-HTML audit matches all operands.')
 # Stage 2: separate Decimal/enumeration and constraint-root calculations, source-pointer + SQL checks.
 subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT),'-p','test_research.py','-v'],check=True)
 print('STAGE 2 PASS: hand-worked cases, 243 independent policy enumerations, 216 Decimal/root reconciliations, SQL and source-pointer accounting.')
 # Stage 3: copy source and pinned inputs, discard outputs, regenerate with no network.
 with tempfile.TemporaryDirectory() as d:
  target=Path(d)/'research';shutil.copytree(ROOT,target,ignore=shutil.ignore_patterns('__pycache__','browser_evidence','screenshots','verification.json'))
  for project in [LAND,HOTEL]:shutil.rmtree(target/project/'outputs')
  call(target/'analyze.py');call(target/'presentation.py')
  for project in [LAND,HOTEL]:
   original=ROOT/project/'outputs';rebuilt=target/project/'outputs';assert sorted(x.name for x in original.iterdir())==sorted(x.name for x in rebuilt.iterdir())
   for p in original.iterdir():assert sha(p)==sha(rebuilt/p.name),p
 print('STAGE 3 PASS: outputs removed and all tables, reports and applications rebuilt byte-identically in an isolated directory. Run browser_test.cjs separately for actual UI acceptance.')
 result={'status':'PASS','stage1':'Pinned numerical sources and recorded independent original-HTML reconciliation; offline CI does not recollect the external URLs.','stage2':'Hand examples, 243 enumerated land policies and 216 independent hotel constraint roots; source pointers and SQL.','stage3':'Isolated regeneration after deleting every output; byte-identical artifacts. Browser execution/evidence separate.','method_adoption':'WITHHELD for both projects','browser_acceptance':'Consult actual workflow and browser_evidence/results.json; never inferred from analytical tests.'}
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
