"""Fetch the two binary assets omitted from the lightweight GitHub source folder."""
from pathlib import Path
import hashlib, json, urllib.request

ROOT = Path(__file__).resolve().parents[1]
for entry in json.loads((ROOT/'content/binary-assets.json').read_text()):
    path = ROOT/entry['path']
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']:
        continue
    request = urllib.request.Request(entry['url'], headers={'User-Agent':'Prathamesh-portfolio-build'})
    data = urllib.request.urlopen(request, timeout=45).read()
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        raise ValueError('Asset changed; review before accepting: '+entry['path'])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print('Fetched and verified '+entry['path'])
