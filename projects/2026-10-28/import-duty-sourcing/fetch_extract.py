"""Read whitelisted fixed-width text only. Never run bundled Census software."""
from pathlib import Path
from collections import defaultdict
import zipfile,csv,json,hashlib,datetime,shutil
import argparse,urllib.request
parser=argparse.ArgumentParser();parser.add_argument('--archive-dir',type=Path,required=True);parser.add_argument('--download',action='store_true');args=parser.parse_args()
P=Path(__file__).resolve().parent;B=args.archive_dir;B.mkdir(parents=True,exist_ok=True)
if args.download:
 for year in [2025,2026]:
  dest=B/f'imports-{year}-08.zip'
  if not dest.exists():
   url=f'https://www.census.gov/trade/downloads/{year}/Merch/im_m/IMDB{str(year)[2:]}08.ZIP'
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PortfolioResearch'}),timeout=90) as src,dest.open('wb') as out:
    shutil.copyfileobj(src,out)
PREFIXES=('8504','8507','8541')
manifest=[]
for year in [2025,2026]:
 f=B/f'imports-{year}-08.zip'
 with zipfile.ZipFile(f) as z:
  lookup={n.upper():n for n in z.namelist()}
  original_read=z.read;original_open=z.open
  z.read=lambda name:original_read(lookup[name.upper()])
  z.open=lambda name,*args,**kwargs:original_open(lookup[name.upper()],*args,**kwargs)
  names={line[:4].decode():line[11:61].decode('ascii').strip() for line in z.read('COUNTRY.TXT').splitlines()}
  concord={line[:10].decode():line[10:160].decode('ascii').strip() for line in z.read('CONCORD.TXT').splitlines() if line[:4].decode() in PREFIXES}
  (P/'data/raw'/f'concord-{year}.txt').write_bytes(b'\n'.join(line for line in z.read('CONCORD.TXT').splitlines() if line[:4].decode() in PREFIXES)+b'\n')
  (P/'data/raw'/f'country-{year}.txt').write_bytes(z.read('COUNTRY.TXT'))
  if year==2026:(P/'data/raw/import-detail-layout.txt').write_bytes(z.read('Documentation/IMP_DETL.lay'))
  acc=defaultdict(lambda:[0,0,0,0]);selected=0;total=0
  with z.open('IMP_DETL.TXT') as stream:
   for raw in stream:
    total+=1;line=raw.rstrip(b'\r\n');assert len(line)==688,(total,len(line))
    if line[:4].decode() not in PREFIXES:continue
    assert line[22:26]==str(year).encode() and line[26:28]==b'08'
    code=line[:10].decode();country=line[10:14].decode();vals=[int(line[a:b]) for a,b in [(73,88),(103,118),(403,418),(433,448)]]
    assert min(vals)>=0;v=acc[(code,country)]
    for i,x in enumerate(vals):v[i]+=x
    selected+=1
  rows=[dict(year=year,hts10=k[0],hs4=k[0][:4],country=k[1],country_name=names.get(k[1],'UNMAPPED'),description=concord.get(k[0],'UNMAPPED'),value_aug=v[0],duty_aug=v[1],value_ytd=v[2],duty_ytd=v[3]) for k,v in sorted(acc.items())]
  with (P/'data/raw'/f'product-country-{year}.csv').open('w') as out:
   w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  # Published commodity totals are a separate aggregate cross-check, not extra observations.
  totals=defaultdict(lambda:[0,0,0,0])
  for line in z.read('IMP_COMM.TXT').splitlines():
   if line[:4].decode() in PREFIXES:
    for i,(a,b) in enumerate([(117,132),(147,162),(447,462),(477,492)]):totals[line[:4].decode()][i]+=int(line[a:b])
  for chapter,v in totals.items():assert v==[sum(r[k] for r in rows if r['hs4']==chapter) for k in ['value_aug','duty_aug','value_ytd','duty_ytd']],(year,chapter,'Detail does not reconcile')
  (P/'data'/f'published-totals-{year}.json').write_text(json.dumps(totals,indent=2)+'\n')
 digest=hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
 manifest.append(dict(year=year,observation_period='January-August YTD and August monthly',url=f'https://www.census.gov/trade/downloads/{year}/Merch/im_m/IMDB{str(year)[2:]}08.ZIP',archive_sha256=digest,archive_bytes=f.stat().st_size,detail_rows_scanned=total,detail_rows_selected=selected,aggregated_rows=len(rows),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reconciliation='Detailed totals exactly equal independently published IMP_COMM totals for all three HS4 chapters'))
 print(year,len(rows),selected,total,flush=True)
# The pinned official layout is retained in data/raw/import-layout.html.
(P/'data/source_manifest.json').write_text(json.dumps(dict(scope='Prespecified HS4 8504 transformers/static converters, 8507 electric accumulators, 8541 semiconductor devices; no selection by result',sources=manifest,vintage='Pinned retrieved historical files, not a point-in-time policy backtest',software='Only fixed-width text was read; no executable or DLL was extracted or run'),indent=2)+'\n')
