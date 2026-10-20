"""Reproducible official-data collection, guarded by pinned observation fingerprints."""
import argparse
import gzip
import hashlib
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECTS = ['airline-delay-intervention-screen', 'bank-deposit-cost-attribution']


def fingerprint(path):
    if path.suffix == '.zip':
        data = zipfile.ZipFile(path).read('Airline_Delay_Cause.csv')
    elif path.name.endswith('.json.gz'):
        response = json.loads(gzip.decompress(path.read_bytes()))
        records = [item['data'] for item in response['data']]
        assert len(records) == response['meta']['total']
        records.sort(key=lambda row: int(row['CERT']))
        data = json.dumps(records, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    else:
        data = gzip.decompress(path.read_bytes())
    return hashlib.sha256(data).hexdigest()


def collect(project, pin=False):
    root = BASE / project
    manifest = json.loads((root / 'data/source_manifest.json').read_text())
    pinfile = root / 'data/pinned_content.json'
    if isinstance(manifest['files'], dict):
        sources = [{'file': 'bts_export.zip', 'url': manifest['url']}]
    else:
        sources = [{'file': row['file'], 'url': row['url']} for row in manifest['files']]
    if pin:
        pinned = {row['file']: fingerprint(root / 'data/raw' / row['file']) for row in sources}
        pinfile.write_text(json.dumps(pinned, indent=2, sort_keys=True) + '\n')
        return
    pinned = json.loads(pinfile.read_text())
    observed = []
    for row in sources:
        target = root / 'data/raw' / row['file']
        if not target.exists():
            request = urllib.request.Request(row['url'], headers={'User-Agent': 'EconomicsPortfolioResearch/1.0'})
            data = urllib.request.urlopen(request, timeout=180).read()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(gzip.compress(data, mtime=0) if target.suffix == '.gz' else data)
        actual = fingerprint(target)
        assert actual == pinned[row['file']], f"Published source observations changed: {row['file']}. Stop and review the new vintage; do not silently repin."
        observed.append({'file': row['file'], 'content_sha256': actual, 'archive_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    (root / 'data/observed_provenance.json').write_text(json.dumps({'checked_utc': datetime.now(timezone.utc).isoformat(), 'files': observed}, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pin', action='store_true', help='Explicit maintainer operation after source review; never used in CI.')
    parser.add_argument('--project', choices=PROJECTS)
    args = parser.parse_args()
    for project in [args.project] if args.project else PROJECTS:
        collect(project, args.pin)
        print(project, 'fingerprints pinned' if args.pin else 'official observations verified')


if __name__ == '__main__':
    main()
