"""Explicit source refresh. SEC public API; no API key. Does not run in CI."""
from pathlib import Path
import urllib.request, json, gzip, hashlib, time, os
from extract import ALIASES
ROOT=Path(__file__).resolve().parent
ISSUERS={'semiconductor-inventory-funding':{'AMAT':6951,'LRCX':707549,'KLAC':319201,'TER':97210,'ONTO':704532,'COHU':21535},'freight-rail-capital-review':{'UNP':100885,'CSX':277948,'NSC':702165}}
def main():
 for project,issuers in ISSUERS.items():
  raw=ROOT/project/'data/raw';raw.mkdir(parents=True,exist_ok=True);manifest=[]
  for ticker,cik in issuers.items():
   u=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'
   req=urllib.request.Request(u,headers={'User-Agent':os.environ.get('SEC_USER_AGENT','IndependentPortfolioResearch/1.0 public-data research')})
   for attempt in range(4):
    try:
     with urllib.request.urlopen(req,timeout=90) as r: b=r.read()
     break
    except Exception:
     if attempt==3: raise
     time.sleep(1+attempt)
   original_hash=hashlib.sha256(b).hexdigest();original_bytes=len(b)
   obj=json.loads(b);assert obj['cik']==cik
   keep={t for tags in ALIASES.values() for t in tags}
   obj['facts']={'us-gaap':{k:v for k,v in obj['facts']['us-gaap'].items() if k in keep}}
   b=json.dumps(obj,separators=(',',':')).encode()
   p=raw/f'{ticker}.json.gz';p.write_bytes(gzip.compress(b,mtime=0))
   manifest.append({'ticker':ticker,'cik':cik,'url':u,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sha256_uncompressed':hashlib.sha256(b).hexdigest(),'sha256_archive':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes_uncompressed':len(b),'original_response_sha256':original_hash,'original_response_bytes':original_bytes,'snapshot_scope':'Lossless projection of specified US-GAAP tags; all original entries and array indices for retained tags preserved'})
   (raw.parent/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
   print(ticker,len(b),flush=True);time.sleep(.2)
  (raw.parent/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
