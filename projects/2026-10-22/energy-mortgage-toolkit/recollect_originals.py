"""Recollect original sources without changing the pinned published dataset; fail on vintage drift."""

import argparse, json, gzip, urllib.request
from pathlib import Path
from config import ROOT, ARO, MORT
from common import sha


def get(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "IndependentPortfolioResearch/1.0 public-source numerical verification"
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--directory", required=True, type=Path)
    a = ap.parse_args()
    a.directory.mkdir(parents=True, exist_ok=True)
    for m in json.loads((ROOT / ARO / "data/source_manifest.json").read_text()):
        b = get(m["url"])
        assert sha(b) == m["original_html_sha256"], "Original SEC document changed"
        (a.directory / f"{m['ticker']}-{m['report_end'][:4]}.htm").write_bytes(b)
    m = json.loads((ROOT / MORT / "data/source_manifest.json").read_text())
    b = get(m["url"])
    assert (
        sha(b) == m["original_sha256"]
    ), "HMDA vintage drift: quarantine recollection; use pinned projection for published results"
    (a.directory / "hmda.csv.gz").write_bytes(gzip.compress(b, mtime=0))
    print("Original hashes matched. Run audit_sources.py --cache", a.directory)
