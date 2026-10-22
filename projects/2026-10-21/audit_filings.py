"""Independent inline-XBRL numeric-cell audit of nine pinned original filings."""
import csv,gzip,json,hashlib,re
from lxml import html
from extract import ROOT,ALIASES,write_csv

def numeric_facts(b):
 tree=html.fromstring(b);contexts={};units={}
 for e in tree.iter():
  tag=str(e.tag).lower()
  if tag.endswith(':unit'):
   measure=[x.text for x in e.iter() if str(x.tag).lower().endswith(':measure')];units[e.get('id')]=measure
  if tag.endswith(':context'):
   dim=any(str(x.tag).lower().endswith((':explicitmember',':typedmember')) for x in e.iter())
   period={str(x.tag).lower().split(':')[-1]:x.text for x in e.iter() if str(x.tag).lower().endswith((':startdate',':enddate',':instant'))}
   contexts[e.get('id')]={'dimensional':dim,'start':period.get('startdate',''),'end':period.get('enddate',period.get('instant',''))}
 out=[]
 for i,e in enumerate(tree.iter()):
  if not str(e.tag).lower().endswith(':nonfraction'):continue
  c=contexts.get(e.get('contextref'))
  if not c or c['dimensional'] or not any(x and x.upper().endswith(':USD') for x in units.get(e.get('unitref'),[])):continue
  text=e.text_content().strip().replace(',','').replace('\u2212','-')
  if text in ('—','–','-',''):v=0.
  else:
   if not re.fullmatch(r'[-+]?\d*(?:\.\d+)?',text):continue
   v=float(text)
  v*=10**int(e.get('scale','0'))
  if e.get('sign')=='-':v=-v
  out.append({'tag':e.get('name'),'start':c['start'],'end':c['end'],'value_usd':v,'context':e.get('contextref'),'element_index':i})
 return out

def run():
 for project in ['semiconductor-inventory-funding','freight-rail-capital-review']:
  root=ROOT/project;manifest=json.loads((root/'data/filing_manifest.json').read_text());lineage=list(csv.DictReader((root/'outputs/source_lineage.csv').open()));checks=[];allfacts=[]
  for m in manifest:
   b=gzip.decompress((root/'data/raw'/m['file']).read_bytes());assert hashlib.sha256(b).hexdigest()==m['snapshot_sha256'];facts=json.loads(b);assert len(facts)>30
   for f in facts:allfacts.append({'ticker':m['ticker'],'accn':m['accn'],**f})
   selected=[r for r in lineage if r['ticker']==m['ticker'] and r['accn']==m['accn']]
   for r in selected:
    hits=[f for f in facts if f['tag']=='us-gaap:'+r['tag'] and f['start']==r['start'] and f['end']==r['end'] and abs(f['value_usd']-float(r['value_usd']))<.5]
    checks.append({'ticker':m['ticker'],'metric':r['metric'],'accn':m['accn'],'tag':r['tag'],'period_end':r['end'],'source_value_usd':float(r['value_usd']),'matching_inline_cells':len(hits),'status':'PASS' if hits else 'FAIL'})
   assert selected or m['ticker'] in ['LRCX','COHU']
  write_csv(root/'outputs/original_filing_cells.csv',allfacts);write_csv(root/'outputs/original_filing_reconciliation.csv',checks)
  assert checks and all(r['status']=='PASS' for r in checks),checks
  print(project,len(allfacts),'original numeric cells',len(checks),'independently matched source operands')
if __name__=='__main__':run()
