"""Pin original latest annual/quarterly HTML for independent disclosure-cell audit."""
from acquire import ISSUERS,ROOT
from extract import CUTOFF
from audit_filings import numeric_facts
import urllib.request,json,gzip,hashlib,time,concurrent.futures

def get(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'IndependentPortfolioResearch/1.0 public-data research'}),timeout=90) as r:return r.read()
  except Exception:
   if attempt==3:raise
   time.sleep(1+attempt)

def acquire_one(job):
 project,t,cik=job;raw=ROOT/project/'data/raw';sub=get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json');a=json.loads(sub)['filings']['recent']
 eligible=[i for i in range(len(a['form'])) if a['form'][i] in (('10-K','10-Q') if project.startswith('semi') else ('10-K',)) and a['filingDate'][i]<=CUTOFF];i=eligible[0]
 accn=a['accessionNumber'][i];doc=a['primaryDocument'][i];url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace("-","")}/{doc}';b=get(url);p=raw/f'{t}-latest-inline.json.gz';snapshot=json.dumps(numeric_facts(b),separators=(',',':')).encode();p.write_bytes(gzip.compress(snapshot,mtime=0));(raw/f'{t}-submissions.json.gz').write_bytes(gzip.compress(sub,mtime=0))
 m={'ticker':t,'cik':cik,'file':p.name,'url':url,'filed':a['filingDate'][i],'end':a['reportDate'][i],'accn':accn,'original_html_sha256':hashlib.sha256(b).hexdigest(),'snapshot_sha256':hashlib.sha256(snapshot).hexdigest(),'submissions_sha256':hashlib.sha256(sub).hexdigest()};print(t,len(b),flush=True);return project,m
if __name__=='__main__':
 out={p:[] for p in ISSUERS};jobs=[(p,t,c) for p,items in ISSUERS.items() for t,c in items.items()]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for p,m in pool.map(acquire_one,jobs):out[p].append(m)
 for p,items in out.items():(ROOT/p/'data/filing_manifest.json').write_text(json.dumps(items,indent=2)+'\n')
