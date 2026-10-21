import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from restore_snapshot import restore


class SnapshotContracts(unittest.TestCase):
    name = 'projects/2026-10-19/airline-delay-intervention-screen/data/raw/bts_export.zip'

    def archive(self, folder, bad_member=False):
        path = folder / 'source.zip'
        content = b'public fixture'
        manifest = {'members': {self.name: {'bytes': len(content), 'sha256': 'bad' if bad_member else hashlib.sha256(content).hexdigest()}}}
        with zipfile.ZipFile(path, 'w') as bundle:
            bundle.writestr(self.name, content)
            bundle.writestr('SNAPSHOT_MANIFEST.json', json.dumps(manifest))
            bundle.writestr('unrelated.txt', b'must not extract')
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_restore_only_allowed_members(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary); archive, digest = self.archive(folder)
            root = folder / 'repository'
            self.assertEqual(restore(archive, root, {self.name}, digest), 1)
            self.assertEqual((root / self.name).read_bytes(), b'public fixture')
            self.assertFalse((root / 'unrelated.txt').exists())

    def test_archive_fingerprint_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary); archive, _ = self.archive(folder)
            with self.assertRaises(AssertionError): restore(archive, folder / 'repository', {self.name}, 'bad')
            self.assertFalse((folder / 'repository').exists())

    def test_member_fingerprint_fails_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary); archive, digest = self.archive(folder, bad_member=True)
            with self.assertRaises(AssertionError): restore(archive, folder / 'repository', {self.name}, digest)
            self.assertFalse((folder / 'repository').exists())

    def test_existing_source_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary); archive, digest = self.archive(folder)
            root = folder / 'repository'; target = root / self.name
            target.parent.mkdir(parents=True); target.write_bytes(b'local work')
            with self.assertRaises(AssertionError): restore(archive, root, {self.name}, digest)
            self.assertEqual(target.read_bytes(), b'local work')


if __name__ == '__main__':
    unittest.main()
