"""Intentional public-source refresh; offline rebuilds never invoke this script.

Original HTML remains in an external cache. Only numerical facts are redistributed.
Recollection needs network access; retained contexts and source URLs are auditable.
"""
import urllib.request,json,gzip,hashlib,time,argparse
from config import ROOT,ISSUERS
from inline import parse

def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'IndependentPortfolioResearch/1.0 public-data research'}),timeout=90) as r:return r.read()
def pin(project,ticker,meta,b):
 root=ROOT/project/'data';raw=root/'raw';raw.mkdir(parents=True,exist_ok=True)
 fs=parse(b);payload=json.dumps(fs,separators=(',',':'),ensure_ascii=False).encode();name=ticker+'-'+meta['reportDate']+'.json.gz';archive=gzip.compress(payload,mtime=0);(raw/name).write_bytes(archive)
 return {'ticker':ticker,'file':name,'cik':meta['cik'],'accession':meta['accessionNumber'],'filed':meta['filingDate'],'report_end':meta['reportDate'],'url':meta['url'],'original_html_sha256':hashlib.sha256(b).hexdigest(),'original_html_bytes':len(b),'snapshot_sha256':hashlib.sha256(payload).hexdigest(),'archive_sha256':hashlib.sha256(archive).hexdigest(),'numeric_facts':len(fs),'projection':'All parseable inline nonfraction cells, original contexts, dimensions, units and element positions; no narrative text.'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=__import__('pathlib').Path);a=ap.parse_args()
 for project,issuers in ISSUERS.items():
  manifest=[]
  if a.cache:
   for ticker in issuers:
    for p in sorted(a.cache.glob(ticker+'-*-meta.json')):
     meta=json.loads(p.read_text());meta['ticker']=ticker;b=p.with_name(p.name.replace('-meta.json','.htm')).read_bytes();manifest.append(pin(project,ticker,meta,b))
  else:
   # Refresh exactly the original-document list, never silently select a new vintage.
   for m in json.loads((ROOT/project/'data/source_manifest.json').read_text()):
    meta={'cik':m['cik'],'reportDate':m['report_end'],'accessionNumber':m['accession'],'filingDate':m['filed'],'url':m['url']};manifest.append(pin(project,m['ticker'],meta,get(m['url'])));time.sleep(.2)
  (ROOT/project/'data/source_manifest.json').write_text(json.dumps(sorted(manifest,key=lambda m:(m['ticker'],m['report_end'])),indent=2)+'\n')
  print(project,len(manifest),'original filings',sum(m['numeric_facts'] for m in manifest),'numerical cells')
