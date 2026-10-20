"""Package only verified public source data, outputs and browser evidence for this research commit."""
import hashlib
import json
import os
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPOSITORY = BASE.parents[1]
DESTINATION = BASE / 'release_bundle.zip'


def main():
    files = []
    files.append(BASE / 'serve.py')
    for slug in ['airline-delay-intervention-screen', 'bank-deposit-cost-attribution']:
        project = BASE / slug
        for folder in [project / 'data/raw', project / 'outputs']:
            files.extend(path for path in folder.iterdir() if path.is_file())
        files.extend(project / name for name in ['data/source_manifest.json', 'data/pinned_content.json', 'data/observed_provenance.json'])
    evidence = BASE / 'browser_evidence'
    result = json.loads((evidence / 'results.json').read_text())
    assert result['status'] == 'PASS' and len(result['results']) == 24
    assert all(row['status'] == 'PASS' for row in result['results'])
    files.extend(path for path in evidence.iterdir() if path.is_file())
    manifest = {'repository': 'Pratattack/analytics-portfolio', 'commit': os.environ.get('GITHUB_SHA', 'local-verification'), 'members': {}}
    with zipfile.ZipFile(DESTINATION, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in sorted(set(files)):
            relative = str(path.relative_to(REPOSITORY))
            data = path.read_bytes()
            bundle.writestr(relative, data)
            manifest['members'][relative] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        bundle.writestr('SNAPSHOT_MANIFEST.json', json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        bundle.writestr('OPEN_WORKBENCHES.txt', 'This archive contains public official-data snapshots, complete outputs and actual browser evidence for the named research commit.\nExtract it in the repository root to reproduce without downloading revised official observations.\nOpen projects/2026-10-19/airline-delay-intervention-screen/outputs/app.html or projects/2026-10-19/bank-deposit-cost-attribution/outputs/app.html. Both use sibling app.js files.\nIf your browser disallows local files, run python projects/2026-10-19/serve.py --project airline-delay-intervention-screen (or bank-deposit-cost-attribution) and open http://127.0.0.1:8765/app.html.\nNo hosted live service, economic causality or actual business saving is implied.\n')
    print(DESTINATION)


if __name__ == '__main__':
    main()
