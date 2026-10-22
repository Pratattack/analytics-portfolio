"""Independent Decimal reconciliation against recollected original document nodes.

Run after collection using --cache, or --live to recollect the pinned URLs.
Offline CI checks this audit's pinned HTML hashes and numerical source pointers; it
cannot attest to a fresh external source download.
"""
import argparse,json,csv,hashlib
from decimal import Decimal
from lxml import html
from config import ROOT,LAND,HOTEL
from acquire import get

def run(cache=None,live=False):
 for project in [LAND,HOTEL]:
  root=ROOT/project;manifest=json.loads((root/'data/source_manifest.json').read_text());rows=list(csv.DictReader((root/'outputs/source_lineage.csv').open()));checks=[]
  for m in manifest:
   used=[r for r in rows if r['source_file']==m['file']]
   if not used:continue
   if live:b=get(m['url'])
   else:
    hits=[p for p in cache.glob(m['ticker']+'-*-meta.json') if json.loads(p.read_text())['accessionNumber']==m['accession']];assert len(hits)==1;b=hits[0].with_name(hits[0].name.replace('-meta.json','.htm')).read_bytes()
   assert hashlib.sha256(b).hexdigest()==m['original_html_sha256'];nodes=list(html.fromstring(b).iter())
   for r in used:
    e=nodes[int(r['cell_index'])];assert str(e.tag).lower().endswith(':nonfraction');assert e.get('name')==r['tag'];assert e.get('contextref')==r['context']
    lexical=''.join(e.itertext()).strip().replace(',','').replace('−','-');v=Decimal(0) if lexical in ['—','–','-'] else Decimal(lexical);v*=Decimal(10)**int(e.get('scale','0'));v*=(-1 if e.get('sign')=='-' else 1);assert v==Decimal(r['value_usd']), (r, str(v), lexical)
    checks.append({'record':r['record'],'metric':r['metric'],'accession':m['accession'],'element_index':int(r['cell_index']),'original_html_sha256':m['original_html_sha256'],'status':'PASS'})
  result={'status':'PASS','method':'Separate Decimal numeric/sign/scale calculation on original HTML nodes, not projected source values','operands':len(checks),'checks':checks}
  (root/'data/original_html_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(project,len(checks),'original source operands independently reconciled')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=__import__('pathlib').Path);ap.add_argument('--live',action='store_true');a=ap.parse_args();assert a.cache or a.live;run(a.cache,a.live)
