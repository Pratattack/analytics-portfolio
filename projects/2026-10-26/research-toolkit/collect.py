"""Build small, auditable input projections from official public responses."""
from pathlib import Path
from datetime import date
import json,csv,gzip,hashlib,urllib.request,time,argparse
from inline import parse
ROOT=Path(__file__).resolve().parent.parent
CACHE=Path(__file__).resolve().parents[4]/'finance-oct26-source'
ISS={'DRI':940944,'TXRH':1289460,'EAT':703351,'BLMN':1546417,'CAKE':887596,'BJRI':1013488}
TAGS={'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'],'ebit':['OperatingIncomeLoss'],'lease_cost':['OperatingLeaseCost'],'lease_cash':['OperatingLeasePayments']}
def get(u):
 for k in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'PrathameshSinghIndependentResearch/1.0 public financial research'}),timeout=60) as r:return r.read()
  except Exception:
   if k==2:raise
   time.sleep(2)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def annual(f):
 return f.get('form')=='10-K' and f.get('start') and f['filed']<='2026-10-26' and 330<=(date.fromisoformat(f['end'])-date.fromisoformat(f['start'])).days<=380 and '2019-01-01'<=f['end']<='2025-12-31'
def main():
 p=ROOT/'credit-spread-recession-audit/data';p.mkdir(parents=True,exist_ok=True);(ROOT/'restaurant-lease-operating-leverage/data').mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True);u='https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAA10YM,GS10,TB3MS,USREC&cosd=1960-01-01&coed=2024-12-31';raw=CACHE/'fred.download';
 if not raw.exists():raw.write_bytes(get(u))
 src=raw; rows=list(csv.DictReader(src.open()));rows=[x for x in rows if '1960-01-01'<=x['observation_date']<='2024-12-31'];out=p/'monthly.csv'
 with out.open('w') as f:w=csv.DictWriter(f,fieldnames=['observation_date','BAA10YM','GS10','TB3MS','USREC']);w.writeheader();w.writerows(rows)
 (p/'original_response.csv').write_bytes(raw.read_bytes());meta={'url':u,'sha256':sha(raw.read_bytes()),'raw_file':'original_response.csv','raw_sha256':sha(raw.read_bytes())};meta.update(series={x:'https://fred.stlouisfed.org/series/'+x for x in ['BAA10YM','GS10','TB3MS','USREC']},projection_sha256=sha(out.read_bytes()),rows=len(rows),observation_cutoff='2024-12-31',retrieval_date='2026-10-26',vintage='As-served revised history; not an ALFRED real-time vintage.');dump(p/'manifest.json',meta)
 panel=[];facts=[];audits=[];manifest=[];exclusions=[]
 for ticker,cik in ISS.items():
  fp=CACHE/f'{ticker}.json'
  if not fp.exists():fp.write_bytes(get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'))
  b=fp.read_bytes();obj=json.loads(b);fs=obj['facts']['us-gaap'];candidates={}
  for field,tags in TAGS.items():
   for priority,tag in enumerate(tags):
    for f in fs.get(tag,{}).get('units',{}).get('USD',[]):
     if annual(f):
      key=(f['start'],f['end'],f['accn']);candidates.setdefault(key,{}).setdefault(field,[]).append(dict(f,tag=tag,priority=priority))
  byend={}
  for key,d in candidates.items():
   if set(d)==set(TAGS):
    selected={k:min(v,key=lambda x:(x['priority'],x['filed'])) for k,v in d.items()}
    if any(len(set(x['val'] for x in v if x['priority']==selected[k]['priority']))>1 for k,v in d.items()):raise ValueError('Conflicting duplicate')
    byend.setdefault(key[1],[]).append((max(x['filed'] for x in selected.values()),key,selected))
  for end,options in sorted(byend.items()):
   filed,key,d=min(options,key=lambda v:(v[0],v[1][2]));row=dict(ticker=ticker,start=key[0],end=end,filed=filed,accn=key[2],**{k:v['val'] for k,v in d.items()});panel.append(row)
   facts.extend(dict(ticker=ticker,field=k,unit='USD',**v) for k,v in d.items())
  retained=[x for x in panel if x['ticker']==ticker];latest=max(retained,key=lambda x:x['end']);accn=latest['accn'];sp=CACHE/f'{ticker}-sub.json'
  if not sp.exists():sp.write_bytes(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json'))
  sub=json.loads(sp.read_bytes());r=sub['filings']['recent'];i=r['accessionNumber'].index(accn);url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace("-", "")}/{r["primaryDocument"][i]}'
  hp=CACHE/f'{ticker}-latest.htm'
  if not hp.exists():hp.write_bytes(get(url))
  hb=hp.read_bytes();numeric=parse(hb);retained_numeric=[]
  for field in TAGS:
   fact=next(f for f in facts if f['ticker']==ticker and f['field']==field and f['accn']==accn and f['start']==latest['start'] and f['end']==latest['end'])
   hits=[x for x in numeric if x['tag']=='us-gaap:'+fact['tag'] and not x['dimensions'] and x['start']==fact['start'] and x['end']==fact['end'] and x['unit']=='iso4217:USD']
   assert hits and all(abs(x['value']-fact['val'])<=max(1,10**(-int(x['decimals'])) if x['decimals']!='INF' else 0) for x in hits),(ticker,field,hits,fact)
   retained_numeric.append(hits[0]);audits.append(dict(ticker=ticker,field=field,value=fact['val'],tag=fact['tag'],context=hits[0]['context'],element_index=hits[0]['element_index'],url=url))
  nb=(json.dumps(retained_numeric,indent=2,sort_keys=True)+'\n').encode();np=ROOT/'restaurant-lease-operating-leverage/data'/f'{ticker}-filing.json';np.write_bytes(nb)
  manifest.append(dict(ticker=ticker,cik=cik,companyfacts_url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json',companyfacts_sha256=sha(b),original_url=url,original_sha256=sha(hb),projection=np.name,projection_sha256=sha(nb),filed=latest['filed'],end=latest['end'],cells=len(retained_numeric),original_numeric_cells=len(numeric)))
  for year in range(2019,2026):
   if not any(x['end'].startswith(str(year)) for x in retained):exclusions.append(dict(ticker=ticker,year=year,reason='No same-accession four-field annual observation'))
  print(ticker,latest['end'],len(retained),'original-audit PASS',flush=True)
 p=ROOT/'restaurant-lease-operating-leverage/data'
 for name,vals in [('panel.json',panel),('lineage.json',facts),('source_manifest.json',manifest),('original_audit.json',audits),('exclusions.json',exclusions)]:dump(p/name,vals)
 dump(p/'hashes.json',{x.name:sha(x.read_bytes()) for x in sorted(p.iterdir()) if x.name!='hashes.json'})
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();CACHE=a.cache;ROOT=a.output
 if ROOT.exists() and any(ROOT.iterdir()):raise SystemExit('Output must be empty; quarantine new vintages instead of overwriting pinned inputs.')
 main()
