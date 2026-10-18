from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request,zipfile,hashlib,json
ROOT=Path(__file__).resolve().parent
URLS={2025:'https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip',**{y:f'https://www.eia.gov/electricity/data/eia861/archive/zip/f861{y}.zip' for y in range(2020,2025)}}
def download(item):
    year,url=item;p=ROOT/'data/raw'/f'f861{year}.zip'
    if not p.exists():
        with urllib.request.urlopen(url,timeout=60) as response:p.write_bytes(response.read())
    with zipfile.ZipFile(p) as z:
        selected=[n for n in z.namelist() if 'Reliability' in n and n.endswith('.xlsx')]
        for name in selected:(ROOT/'data/raw'/Path(name).name).write_bytes(z.read(name))
    return dict(year=year,url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reliability_files=selected)
if __name__=='__main__':
    (ROOT/'data/raw').mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(download,sorted(URLS.items())))
    (ROOT/'data/source_manifest.json').write_text(json.dumps(dict(retrieved='2026-10-18',landing_page='https://www.eia.gov/electricity/data/eia861/',files=records),indent=2))
    print(json.dumps(records,indent=2))
