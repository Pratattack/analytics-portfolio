"""Intentional recollection and documented numerical projections; no network during verification."""

import json, gzip, hashlib, csv, io, time, urllib.request, argparse
from pathlib import Path
from inline import parse
from config import ROOT, ARO, MORT

FIELDS = "activity_year lei derived_msa-md county_code census_tract action_taken loan_type loan_purpose lien_status reverse_mortgage open-end_line_of_credit business_or_commercial_purpose loan_amount loan_to_value_ratio interest_rate rate_spread total_loan_costs lender_credits discount_points loan_term intro_rate_period negative_amortization interest_only_payment balloon_payment other_nonamortizing_features construction_method occupancy_type total_units income debt_to_income_ratio conforming_loan_limit".split()


def h(b):
    return hashlib.sha256(b).hexdigest()


def get(u):
    with urllib.request.urlopen(
        urllib.request.Request(
            u,
            headers={
                "User-Agent": "IndependentPortfolioResearch/1.0 public-data study"
            },
        ),
        timeout=120,
    ) as r:
        return r.read()


def save_parts(root, b):
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    parts = []
    for i in range(0, len(b), 200000):
        p = raw / f"hmda.csv.gz.part{i//200000:03}"
        x = b[i : i + 200000]
        p.write_bytes(x)
        parts.append({"file": p.name, "sha256": h(x), "bytes": len(x)})
    return parts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path)
    a = ap.parse_args()
    root = ROOT / ARO
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest = []
    if a.cache:
        meta = [
            json.loads(p.read_text())
            for p in a.cache.glob("*-meta.json")
            if p.name.split("-")[0] in ["COP", "EOG", "DVN", "FANG", "APA", "MUR"]
        ]
    else:
        meta = json.loads((root / "data/source_manifest.json").read_text())
    for m in sorted(
        meta, key=lambda m: (m["ticker"], m.get("reportDate", m.get("report_end")))
    ):
        b = (
            (a.cache / (m["ticker"] + "-" + m["reportDate"][:4] + ".htm")).read_bytes()
            if a.cache
            else get(m["url"])
        )
        fs = parse(b)
        payload = json.dumps(fs, separators=(",", ":")).encode()
        name = m["ticker"] + "-" + m.get("reportDate", m.get("report_end")) + ".json.gz"
        z = gzip.compress(payload, mtime=0)
        (raw / name).write_bytes(z)
        manifest.append(
            {
                "ticker": m["ticker"],
                "cik": m["cik"],
                "report_end": m.get("reportDate", m.get("report_end")),
                "filed": m.get("filingDate", m.get("filed")),
                "accession": m.get("accessionNumber", m.get("accession")),
                "url": m["url"],
                "file": name,
                "original_html_sha256": h(b),
                "snapshot_sha256": h(payload),
                "archive_sha256": h(z),
                "numeric_cells": len(fs),
            }
        )
    (root / "data/source_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(ARO, len(manifest), "pinned filings")
    root = ROOT / MORT
    u = "https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?msamds=26420&years=2025&actions_taken=1"
    b = gzip.decompress((a.cache / "hmda.csv.gz").read_bytes()) if a.cache else get(u)
    rows = list(csv.DictReader(io.StringIO(b.decode())))
    s = io.StringIO(newline="")
    w = csv.DictWriter(s, fieldnames=["source_row"] + FIELDS, lineterminator="\n")
    w.writeheader()
    for i, r in enumerate(rows):
        w.writerow({"source_row": i + 2, **{k: r[k] for k in FIELDS}})
    projection = s.getvalue().encode()
    z = gzip.compress(projection, mtime=0)
    parts = save_parts(root, z)
    m = {
        "url": u,
        "retrieved_date": "2026-10-22",
        "vintage": "2025 snapshot as served by official Data Browser; no loan-level lock/closing dates public",
        "original_sha256": h(b),
        "original_bytes": len(b),
        "rows": len(rows),
        "projected_fields": ["source_row"] + FIELDS,
        "projection_sha256": h(projection),
        "archive_sha256": h(z),
        "parts": parts,
        "privacy_scope": "Public financial/product fields and tract cluster only; demographic fields omitted; repeated public rows retained, not deduplicated.",
    }
    (root / "data/source_manifest.json").write_text(json.dumps(m, indent=2) + "\n")
    for name, endpoint in [
        ("filers", "view/filers"),
        ("aggregate", "view/aggregations"),
    ]:
        u = (
            "https://ffiec.cfpb.gov/v2/data-browser-api/"
            + endpoint
            + "?msamds=26420&years=2025"
            + ("&actions_taken=1" if name == "aggregate" else "")
        )
        p = (a.cache / (name + ".json")) if a.cache else None
        try:
            b = p.read_bytes() if p and p.exists() else get(u)
            if p:
                p.write_bytes(b)
            (root / "data" / f"{name}.json").write_bytes(b)
            m[name] = {"url": u, "sha256": h(b)}
        except Exception as e:
            raise RuntimeError(f"{name} source collection failed: {e}")
    (root / "data/source_manifest.json").write_text(json.dumps(m, indent=2) + "\n")
    print(MORT, len(rows), "source rows", len(z), "compressed projected bytes")
