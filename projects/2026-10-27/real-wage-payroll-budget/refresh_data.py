"""Explicit opt-in refresh. Default analysis never accesses the network."""
from pathlib import Path
import argparse,urllib.request,hashlib,json,datetime,csv,io
p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');a=p.parse_args()
if not a.refresh: p.error('Refreshing changes the snapshot. Pass --refresh, then rerun analysis and tests.')
root=Path(__file__).resolve().parent;mp=root/'data/source_manifest.json';m=json.loads(mp.read_text());today=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
for s in m['sources']:
 url=s['url'].split('&coed=')[0]+'&coed='+today
 b=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PortfolioResearch/1.0'}),timeout=60).read()
 rows=list(csv.reader(io.StringIO(b.decode())));assert rows[0]==['observation_date',s['series']] and len(rows)>2
 (root/'data/raw'/(s['series']+'.csv')).write_bytes(b)
 s.update(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),retrieved_utc=today)
m.update(retrieved_utc=today,analysis_cutoff=today);mp.write_text(json.dumps(m,indent=2)+'\n')
print('Snapshot replaced. Regenerate outputs and review the new findings before publication.')
