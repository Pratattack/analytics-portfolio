"""Offline source contracts, independent checks and empty-output reproduction."""
from pathlib import Path
import json,csv,math,tempfile,shutil,subprocess,sys,re
import common,credit,restaurant,presentation
from common import ROOT,CREDIT,REST,digest,readcsv,dump
HERE=Path(__file__).resolve().parent

def same(a,b):
 if isinstance(a,dict):assert set(a)==set(b);[same(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b);[same(x,y) for x,y in zip(a,b)]
 elif isinstance(a,(float,int)) and not isinstance(a,bool):assert math.isclose(a,b,rel_tol=1e-7,abs_tol=1e-8),(a,b)
 elif isinstance(a,str) and isinstance(b,str):
  try:av=float(a);bv=float(b)
  except ValueError:assert a==b,(a,b)
  else:assert math.isclose(av,bv,rel_tol=1e-7,abs_tol=1e-8),(a,b)
 else:assert a==b,(a,b)

def compare_csv(a,b):
 x=readcsv(a);y=readcsv(b);assert len(x)==len(y)
 for r,s in zip(x,y):
  assert set(r)==set(s)
  for k in r:
   try:av=float(r[k]);bv=float(s[k])
   except (ValueError,TypeError):assert r[k]==s[k],(k,r[k],s[k]);continue
   assert math.isclose(av,bv,rel_tol=1e-7,abs_tol=1e-8),(k,av,bv)

def compare_html(a,b):
 s=a.read_text();t=b.read_text();assert '<meta charset="utf-8">' in t and '<title>' in t
 if a.name=='app.html':
  def data(z):return json.loads(re.search(r'<script>const DATA=(.*?);window.RESEARCH_DATA',z,re.S).group(1))
  same(data(s),data(t))
  # All code/layout outside the generated numerical DATA object must reproduce exactly.
  s=re.sub(r'<script>const DATA=.*?;window.RESEARCH_DATA','<script>const DATA=OMITTED;window.RESEARCH_DATA',s,flags=re.S);t=re.sub(r'<script>const DATA=.*?;window.RESEARCH_DATA','<script>const DATA=OMITTED;window.RESEARCH_DATA',t,flags=re.S)
 assert s==t

def main():
 subprocess.run([sys.executable,str(HERE/'test_research.py')],check=True)
 originals={str(p.relative_to(ROOT)):digest(p) for slug in [CREDIT,REST] for p in (ROOT/slug/'outputs').iterdir() if p.is_file()}
 with tempfile.TemporaryDirectory() as d:
  target=Path(d)
  for slug in [CREDIT,REST]:shutil.copytree(ROOT/slug/'data',target/slug/'data')
  for mod in [common,credit,restaurant,presentation]:mod.ROOT=target
  credit.analyze();restaurant.analyze();presentation.build()
  compared=0;exact=0
  for slug in [CREDIT,REST]:
   for p in (ROOT/slug/'outputs').iterdir():
    if not p.is_file():continue
    q=target/slug/'outputs'/p.name;assert q.exists();exact+=p.read_bytes()==q.read_bytes();compared+=1
    if p.suffix=='.json':same(json.loads(p.read_text()),json.loads(q.read_text()))
    elif p.suffix=='.csv':compare_csv(p,q)
    elif p.suffix=='.html':compare_html(p,q)
    else:assert p.read_bytes()==q.read_bytes()
 for mod in [common,credit,restaurant,presentation]:mod.ROOT=ROOT
 record={'status':'PASS','analytical_tests':12,'source_checks':'FRED full-response projection and monthly continuity; source fingerprints, 24 original SEC cells, same-accession panel lineage; 32 retained issuer-years with explicit missing coverage.','independent_checks':'Finite-difference logistic gradient, rank/Brier hand fixtures, independent SQL scores; 216 HiGHS LP checks, 2D vertex enumeration and no-rent-double-count hand cases.','reproduction':{'empty_output_files':compared,'byte_identical_in_this_run':exact,'numeric_tolerance':'relative 1e-7, absolute 1e-8; code/layout exact, numerical HTML data checked semantically'},'browser':'Separate required gate; this script does not execute or certify browser acceptance.','output_sha256':originals}
 dump(HERE/'verification.json',record);print('PASS: analytical contracts and empty-output reproduction',compared,'files;',exact,'byte-identical in this run.')
if __name__=='__main__':main()
