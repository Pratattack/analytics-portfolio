"""Refetch modeled provider PDFs. Changed sources never overwrite archived evidence."""
from pathlib import Path
import json,hashlib,urllib.request,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]

def main():
    wanted={p['source_id'] for p in json.loads((ROOT/'data/plans.json').read_text())}
    sources=[s for s in json.loads((ROOT/'data/source_manifest.json').read_text()) if s['id'] in wanted]
    target=ROOT/'data/raw';target.mkdir(exist_ok=True)
    def fetch(s):
        try:
            with urllib.request.urlopen(s['url'],timeout=30) as r:b=r.read()
            digest=hashlib.sha256(b).hexdigest()
            if digest!=s['sha256']:
                (target/(s['id']+'-changed.pdf')).write_bytes(b)
                return {'source_id':s['id'],'status':'changed_or_incomplete','original_sha256':s['sha256'],'new_sha256':digest}
            (target/(s['id']+'.pdf')).write_bytes(b)
            return {'source_id':s['id'],'status':'identical_snapshot'}
        except Exception as e:return {'source_id':s['id'],'status':'unavailable','error':str(e)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,sources))
    (ROOT/'results/source_reverification.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
    if any(r['status']!='identical_snapshot' for r in rows):raise SystemExit(1)

if __name__=='__main__':main()
