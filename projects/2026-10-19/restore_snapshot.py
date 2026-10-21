"""Restore only pinned official raw observations from the immutable public research release."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

BASE = Path(__file__).resolve().parent
REPOSITORY = BASE.parents[1]
SNAPSHOT_SHA256 = 'e3a0c0c8c780394f39fb2d60f291c69d49efd6f3e01444c0e0908c30b6d63d6b'
SNAPSHOT_TAG = 'research-2026-10-19-6d3bd3a997d8'


def restore(archive, repository, expected_names, expected_digest=SNAPSHOT_SHA256):
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected_digest, 'Snapshot archive fingerprint mismatch'
    pending = []
    with zipfile.ZipFile(archive) as bundle:
        manifest = json.loads(bundle.read('SNAPSHOT_MANIFEST.json'))
        for name in sorted(expected_names):
            path = PurePosixPath(name)
            assert not path.is_absolute() and '..' not in path.parts, 'Unsafe source path'
            assert '/data/raw/' in name and name.startswith('projects/2026-10-19/'), 'Not an allowed source member'
            data = bundle.read(name)
            expected = manifest['members'][name]
            assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'], 'Source member fingerprint mismatch'
            target = repository / name
            if target.exists():
                assert target.read_bytes() == data, 'Existing raw source differs; retained without overwrite'
            else:
                pending.append((target, data))
    # Validate every selected member and existing destination before creating any files.
    for target, data in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return len(expected_names)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    from collect import PROJECTS, collect
    names = set()
    for project in PROJECTS:
        pinned = json.loads((BASE / project / 'data/pinned_content.json').read_text())
        for filename in pinned:
            assert PurePosixPath(filename).name == filename, 'Unsafe source filename'
            names.add(f'projects/2026-10-19/{project}/data/raw/{filename}')
    count = restore(args.archive, REPOSITORY, names)
    for project in PROJECTS:
        collect(project)  # Independently check original observation fingerprints after archive/member hashes.
    print(f'{count} source members restored and observation fingerprints verified from {SNAPSHOT_TAG}; no fresh-source claim')


if __name__ == '__main__':
    main()
