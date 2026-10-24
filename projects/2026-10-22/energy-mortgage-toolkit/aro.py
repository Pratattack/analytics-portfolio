"""Original disclosure ledger reconstruction and tight conditional timing bounds."""

import json, itertools, math, sqlite3, gzip
import numpy as np
from scipy.optimize import linprog
from config import ROOT, ARO, CUTOFF
from common import write, dump, sha


def bounds(book, rate, mean, near_cap):
    for k, v, lo, hi in [
        ("book", book, 1, 1e14),
        ("rate", rate, 0, 0.2),
        ("mean", mean, 1, 30),
        ("near_cap", near_cap, 0, 1),
    ]:
        if isinstance(v, bool) or not math.isfinite(v) or not lo <= v <= hi:
            raise ValueError(k + " outside allowed domain")
    t = np.arange(1, 31, dtype=float)
    f = (1 + rate) ** t
    A = np.vstack([np.ones(30), t])
    ub = (t <= 5).astype(float)[None, :]
    sol = []
    for sign in [1, -1]:
        r = linprog(
            sign * f,
            A_ub=ub,
            b_ub=[near_cap],
            A_eq=A,
            b_eq=[1, mean],
            bounds=(0, None),
            method="highs",
        )
        if not r.success:
            return {
                "status": "infeasible assumptions",
                "lower": None,
                "upper": None,
                "min_profile": [],
                "max_profile": [],
            }
        assert (
            abs(r.x.sum() - 1) < 1e-7
            and abs(r.x @ t - mean) < 1e-7
            and r.x[t <= 5].sum() <= near_cap + 1e-7
        )
        sol.append(r)
    return {
        "status": "feasible",
        "lower": float(sol[0].x @ f * book),
        "upper": float(sol[1].x @ f * book),
        "min_profile": sol[0].x.tolist(),
        "max_profile": sol[1].x.tolist(),
    }


def run():
    root = ROOT / ARO
    ledger = json.loads((root / "data/ledger_sources.json").read_text())
    candidate = []
    issues = []
    lineage = []
    for m in ledger:
        assert m["filed"] <= CUTOFF
        b = (root / "data/raw" / m["file"]).read_bytes()
        assert sha(b) == m["archive_sha256"]
        assert sha(gzip.decompress(b)) == m["snapshot_sha256"]
        cells = m["table_numeric_cells"]
        raw_facts = {f["element_index"]: f for f in json.loads(gzip.decompress(b))}
        for f in cells:
            assert {
                k: v
                for k, v in f.items()
                if k not in ["display_value", "display_negative"]
            } == raw_facts[f["element_index"]]
            assert abs(f["display_value"]) == abs(f["value"])
        periods = sorted(
            set(
                (f["start"], f["end"])
                for f in cells
                if f["start"]
                and f["start"].endswith("-01-01")
                and f["end"].endswith("-12-31")
                and f["start"][:4] == f["end"][:4]
            )
        )
        for start, end in periods:
            prev = str(int(start[:4]) - 1) + "-12-31"
            opens = [
                f
                for f in cells
                if f["tag"] == "us-gaap:AssetRetirementObligation"
                and f["end"] == prev
                and not f["start"]
            ]
            closes = [
                f
                for f in cells
                if f["tag"] == "us-gaap:AssetRetirementObligation"
                and f["end"] == end
                and not f["start"]
            ]
            flows = [f for f in cells if f["start"] == start and f["end"] == end]
            if not opens or not closes or len(flows) < 3:
                issues.append(
                    {
                        "ticker": m["ticker"],
                        "end": end,
                        "reason": "missing complete opening/closing ledger scope",
                    }
                )
                continue
            assert (
                len({f["value"] for f in opens})
                == len({f["value"] for f in closes})
                == 1
            )
            residual = (
                opens[0]["display_value"]
                + sum(f["display_value"] for f in flows)
                - closes[0]["display_value"]
            )
            tol = (
                sum(
                    0 if f["decimals"] == "INF" else 0.5 * 10 ** (-int(f["decimals"]))
                    for f in [opens[0], closes[0]] + flows
                )
                + 0.01
            )
            if abs(residual) > tol:
                issues.append(
                    {
                        "ticker": m["ticker"],
                        "end": end,
                        "reason": f"ledger does not reconcile: residual={residual}, declared-rounding tolerance={tol}",
                    }
                )
                continue
            r = {
                "ticker": m["ticker"],
                "year": int(end[:4]),
                "filed": m["filed"],
                "accession": m["accession"],
                "opening": opens[0]["display_value"],
                "closing": closes[0]["display_value"],
                "ledger_residual": residual,
                "rounding_tolerance": tol,
                "accretion": sum(
                    f["display_value"] for f in flows if "Accretion" in f["tag"]
                ),
                "revisions": sum(
                    f["display_value"]
                    for f in flows
                    if "RevisionOfEstimate" in f["tag"]
                ),
                "explicit_cash_paid": (
                    sum(
                        abs(f["display_value"])
                        for f in flows
                        if "CashPaidToSettle" in f["tag"]
                    )
                    if any("CashPaidToSettle" in f["tag"] for f in flows)
                    else None
                ),
                "removed_liability": sum(
                    abs(f["display_value"])
                    for f in flows
                    if "LiabilitiesSettled" in f["tag"]
                ),
            }
            candidate.append(
                (
                    r,
                    m,
                    [("opening", opens[0]), ("closing", closes[0])]
                    + [("flow", f) for f in flows],
                )
            )
    chosen = {}
    for r, m, used in candidate:
        key = (r["ticker"], r["year"])
        if key not in chosen or m["filed"] > chosen[key][1]["filed"]:
            chosen[key] = (r, m, used)
    panel = []
    for key, (r, m, used) in sorted(chosen.items()):
        panel.append(r)
        for role, f in used:
            lineage.append(
                {
                    "ticker": r["ticker"],
                    "year": r["year"],
                    "role": role,
                    "file": m["file"],
                    "url": m["url"],
                    "accession": m["accession"],
                    "element_index": f["element_index"],
                    "context": f["context"],
                    "tag": f["tag"],
                    "normalized_value": f["value"],
                    "presentation_value": f["display_value"],
                    "start": f["start"],
                    "end": f["end"],
                }
            )
    latest = [
        max([r for r in panel if r["ticker"] == t], key=lambda r: r["year"])
        for t in sorted(set(r["ticker"] for r in panel))
    ]
    grid = []
    profiles = []
    for r in latest:
        assert r["year"] == 2025
        for rate, mean, cap in itertools.product(
            [0.03, 0.06, 0.09], [5, 10, 15, 20], [0, 0.25, 0.5]
        ):
            z = bounds(r["closing"], rate, mean, cap)
            key = f"{r['ticker']}|{rate}|{mean}|{cap}"
            grid.append(
                {
                    "ticker": r["ticker"],
                    "discount_rate_assumed": rate,
                    "pv_weighted_mean_year_assumed": mean,
                    "first5_pv_share_cap_assumed": cap,
                    "book_pv": r["closing"],
                    "status": z["status"],
                    "lower_cash_equivalent": z["lower"],
                    "upper_cash_equivalent": z["upper"],
                    "scenario_key": key,
                }
            )
            for label, k in [("lower", "min_profile"), ("upper", "max_profile")]:
                for i, w in enumerate(z[k]):
                    if w > 1e-10:
                        profiles.append(
                            {
                                "scenario_key": key,
                                "bound": label,
                                "year": i + 1,
                                "pv_share": w,
                            }
                        )
    out = root / "outputs"
    write(out / "panel.csv", panel)
    write(out / "source_lineage.csv", lineage)
    write(out / "exclusions.csv", issues, ["ticker", "end", "reason"])
    write(out / "latest.csv", latest)
    write(out / "timing_bounds.csv", grid)
    write(out / "extremal_profiles.csv", profiles)
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE TABLE ledger(ticker TEXT,year INTEGER,opening REAL,closing REAL,accretion REAL,revisions REAL,cash REAL,removed REAL)"
    )
    con.executemany(
        "INSERT INTO ledger VALUES(?,?,?,?,?,?,?,?)",
        [
            (
                r["ticker"],
                r["year"],
                r["opening"],
                r["closing"],
                r["accretion"],
                r["revisions"],
                r["explicit_cash_paid"],
                r["removed_liability"],
            )
            for r in panel
        ],
    )
    q = "SELECT ticker,COUNT(*) observations,SUM(accretion) accretion_sum,SUM(revisions) revision_sum,COUNT(cash) explicit_cash_observations FROM ledger GROUP BY ticker ORDER BY ticker"
    cur = con.execute(q)
    write(
        out / "sql_history.csv",
        [dict(zip([x[0] for x in cur.description], r)) for r in cur.fetchall()],
    )
    (root / "warehouse.sql").write_text(q + ";\n")
    metrics = {
        "observations": len(panel),
        "source_filings": len(ledger),
        "ledger_operands": len(lineage),
        "issuers": len(latest),
        "latest_book_pv": sum(r["closing"] for r in latest),
        "explicit_cash_issuer_years": sum(
            r["explicit_cash_paid"] is not None for r in panel
        ),
        "scenarios": len(grid),
        "infeasible_assumption_combinations": sum(
            r["status"] != "feasible" for r in grid
        ),
        "adoption_gate": False,
        "interpretation": "Conditional common-discount cash equivalents, not issuer forecasts, actuarial estimates or changes to GAAP ARO.",
    }
    dump(out / "metrics.json", metrics)
    print(ARO, metrics)


if __name__ == "__main__":
    run()
