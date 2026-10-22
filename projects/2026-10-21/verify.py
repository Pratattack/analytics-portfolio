"""Three stages. Browser evidence is produced by the separate executed suite."""
from pathlib import Path
import subprocess,sys,tempfile,shutil,hashlib,json,os
os.environ["OPENBLAS_NUM_THREADS"]="1"
ROOT=Path(__file__).resolve().parent

def call(*args,cwd=ROOT):subprocess.run([sys.executable,*args],cwd=cwd,check=True)
def files(root):
 return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ['semiconductor-inventory-funding','freight-rail-capital-review'] for p in (root/name/'outputs').iterdir() if p.is_file() and p.suffix not in ['.png'] and p.name!='executive_brief.md'}
def main():
 print('STAGE 1: pinned source, lineage, temporal and source-boundary contracts',flush=True)
 call('analyze.py');call('audit_filings.py');call('presentation.py')
 print('STAGE 2: hand-worked cases, SVD, Decimal cash-flow and independent SQL reconciliation',flush=True)
 call('-m','unittest','-v','test_research')
 print('STAGE 3: fresh directory, no outputs, offline deterministic rebuild',flush=True)
 before=files(ROOT)
 with tempfile.TemporaryDirectory() as tmp:
  clean=Path(tmp)/'research';shutil.copytree(ROOT,clean,ignore=shutil.ignore_patterns('outputs','__pycache__','browser_evidence','screenshots'))
  call('analyze.py',cwd=clean);call('audit_filings.py',cwd=clean);call('presentation.py',cwd=clean);after=files(clean);assert before==after,{k for k in before if before.get(k)!=after.get(k)}
 result={'analytical_stages':'PASS','derived_files_reproduced':len(before),'browser_acceptance':'SEPARATE: see browser_evidence/results.json or CI artifact; not implied by analytical PASS','python':sys.version.split()[0]}
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
