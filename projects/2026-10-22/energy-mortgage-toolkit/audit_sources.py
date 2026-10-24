"""Independent full-original comparison. Run after downloading original source files into --cache."""

import argparse, json, gzip, hashlib, csv, io
from pathlib import Path
from decimal import Decimal
from lxml import html
from config import ROOT, ARO, MORT
from common import sha, dump
from mortgage import source

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    a = ap.parse_args()
    count = 0
    filings = []
    for m in json.loads((ROOT / ARO / "data/ledger_sources.json").read_text()):
        b = (a.cache / f"{m['ticker']}-{m['report_end'][:4]}.htm").read_bytes()
        assert sha(b) == m["original_html_sha256"]
        tr = html.fromstring(b)
        nodes = list(tr.iter())
        for f in m["table_numeric_cells"]:
            e = nodes[f["element_index"]]
            assert e.get("name") == f["tag"] and e.get("contextref") == f["context"]
            s = (
                "".join(e.itertext())
                .replace(",", "")
                .replace("$", "")
                .strip()
                .replace("(", "")
                .replace(")", "")
            )
            s = "".join(s.split())
            v = Decimal(0) if s in ["", "—", "–", "-"] else Decimal(s)
            v *= Decimal(10) ** int(e.get("scale", "0"))
            v = -v if e.get("sign") == "-" else v
            assert float(v) == f["value"]
            count += 1
        filings.append(
            {
                "ticker": m["ticker"],
                "end": m["report_end"],
                "original_sha256": sha(b),
                "numeric_ledger_cells": len(m["table_numeric_cells"]),
            }
        )
    raw = gzip.decompress((a.cache / "hmda.csv.gz").read_bytes())
    m = json.loads((ROOT / MORT / "data/source_manifest.json").read_text())
    assert sha(raw) == m["original_sha256"]
    rr = list(csv.DictReader(io.StringIO(raw.decode())))
    projected = source()
    assert len(rr) == len(projected)
    for i, (r, p) in enumerate(zip(rr, projected)):
        assert int(p["source_row"]) == i + 2
        for k in m["projected_fields"]:
            if k != "source_row":
                assert r[k] == p[k], (i, k)
    result = {
        "status": "PASS",
        "audit_date": "2026-10-22",
        "original_sec_filings": len(filings),
        "numeric_ledger_cells_independently_checked": count,
        "hmda_rows_compared_to_full_original": len(rr),
        "projected_source_fields_compared": len(m["projected_fields"]) - 1,
        "filings": filings,
        "scope": "Actual full originals retrieved and audited; repeat with network recollection via acquire.py and pin_aro_tables.py. Standard CI validates pinned snapshots offline, not fresh SEC downloads.",
    }
    dump(Path(__file__).parent / "source_audit.json", result)
    print({k: v for k, v in result.items() if k != "filings"})
