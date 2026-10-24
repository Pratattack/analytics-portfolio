"""Common-support mortgage pricing comparison; descriptive, not causal or a live quote."""

import csv, gzip, io, json, math, sqlite3, collections
import numpy as np
from config import ROOT, MORT
from common import sha, write, dump


def source():
    root = ROOT / MORT
    m = json.loads((root / "data/source_manifest.json").read_text())
    parts = []
    for p in m["parts"]:
        b = (root / "data/raw" / p["file"]).read_bytes()
        assert sha(b) == p["sha256"] and len(b) == p["bytes"]
        parts.append(b)
    z = b"".join(parts)
    assert sha(z) == m["archive_sha256"]
    b = gzip.decompress(z)
    assert sha(b) == m["projection_sha256"]
    rows = list(csv.DictReader(io.StringIO(b.decode())))
    assert len(rows) == m["rows"] == 123445
    for k in ["filers", "aggregate"]:
        assert sha((root / "data" / f"{k}.json").read_bytes()) == m[k]["sha256"]
    agg = json.loads((root / "data/aggregate.json").read_text())["aggregations"]
    assert sum(r["count"] for r in agg) == len(rows)
    assert sum(float(r["loan_amount"]) for r in rows) == sum(r["sum"] for r in agg)
    assert all(
        r["activity_year"] == "2025"
        and r["derived_msa-md"] == "26420"
        and r["action_taken"] == "1"
        and int(r["source_row"]) == i + 2
        for i, r in enumerate(rows)
    )
    return rows


def num(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (ValueError, TypeError):
        return None


def dti(v):
    if v in ["<20%", "20%-<30%", "30%-<36%"]:
        return 0
    if v in ["50%-60%"]:
        return 3
    n = num(v)
    if n is not None and 36 <= n <= 49:
        return 1 if n < 43 else 2
    return None


def cell(r, fine=False):
    amount = r["amount"]
    ltv = r["ltv"]
    ab = sum(
        amount >= x
        for x in (
            [200000, 300000, 400000, 600000] if fine else [250000, 400000, 600000]
        )
    )
    lb = sum(ltv > x for x in ([70, 80, 90, 95] if fine else [80, 90, 95]))
    return (
        f"A{ab}|L{lb}|D{r['dti_bin']}|{'Harris' if r['county']=='48201' else 'Other'}"
    )


def eligible(rows):
    flow = collections.Counter()
    out = []
    filters = [
        (
            "product",
            lambda r: all(
                r[k] == v
                for k, v in {
                    "loan_type": "1",
                    "loan_purpose": "1",
                    "lien_status": "1",
                    "occupancy_type": "1",
                    "construction_method": "1",
                    "total_units": "1",
                    "loan_term": "360",
                    "intro_rate_period": "NA",
                    "conforming_loan_limit": "C",
                    "reverse_mortgage": "2",
                    "open-end_line_of_credit": "2",
                    "business_or_commercial_purpose": "2",
                    "negative_amortization": "2",
                    "interest_only_payment": "2",
                    "balloon_payment": "2",
                    "other_nonamortizing_features": "2",
                }.items()
            ),
        ),
        (
            "numeric_complete",
            lambda r: all(
                num(r[k]) is not None
                for k in [
                    "loan_amount",
                    "loan_to_value_ratio",
                    "interest_rate",
                    "rate_spread",
                    "total_loan_costs",
                ]
            )
            and dti(r["debt_to_income_ratio"]) is not None,
        ),
        (
            "domain",
            lambda r: 80000 <= float(r["loan_amount"]) <= 1000000
            and 0 < float(r["loan_to_value_ratio"]) <= 110
            and 0 < float(r["interest_rate"]) <= 20
            and -5 <= float(r["rate_spread"]) <= 10
            and 0 <= float(r["total_loan_costs"]) <= 100000
            and r["census_tract"] not in ["NA", "Exempt", ""],
        ),
    ]
    for r in rows:
        flow["source"] += 1
        for name, pred in filters:
            if not pred(r):
                flow["excluded_" + name] += 1
                break
            flow["passed_" + name] += 1
        else:
            v = {
                "source_row": int(r["source_row"]),
                "lei": r["lei"],
                "county": r["county_code"],
                "tract": r["census_tract"],
                "amount": float(r["loan_amount"]),
                "ltv": float(r["loan_to_value_ratio"]),
                "dti_bin": dti(r["debt_to_income_ratio"]),
                "interest": float(r["interest_rate"]),
                "spread": float(r["rate_spread"]),
                "gross_cost": float(r["total_loan_costs"]),
            }
            v["cost_bps"] = v["gross_cost"] / v["amount"] * 10000
            v["cell"] = cell(v)
            out.append(v)
    return out, dict(flow)


def match(rows, lenders, mincell=10, fine=False):
    grouped = collections.defaultdict(list)
    for r in rows:
        if r["lei"] in lenders:
            grouped[cell(r, fine), r["lei"]].append(r)
    cells = sorted(
        c
        for c in set(k[0] for k in grouped)
        if all(len(grouped.get((c, l), [])) >= mincell for l in lenders)
    )
    weights = np.array([min(len(grouped[c, l]) for l in lenders) for c in cells], float)
    if not cells:
        return [], [], []
    weights /= weights.sum()
    summary = []
    detail = []
    for l in lenders:
        allr = [r for r in rows if r["lei"] == l]
        rr = [r for c in cells for r in grouped[c, l]]
        z = {
            "lei": l,
            "eligible_n": len(allr),
            "matched_n": len(rr),
            "retained_share": len(rr) / len(allr),
            "common_cells": len(cells),
            "naive_spread": sum(r["spread"] for r in allr) / len(allr),
            "matched_spread": sum(
                w * np.mean([r["spread"] for r in grouped[c, l]])
                for c, w in zip(cells, weights)
            ),
            "matched_gross_cost_bps": sum(
                w * np.mean([r["cost_bps"] for r in grouped[c, l]])
                for c, w in zip(cells, weights)
            ),
        }
        summary.append(z)
        for c, w in zip(cells, weights):
            rs = grouped[c, l]
            detail.append(
                {
                    "cell": c,
                    "lei": l,
                    "n": len(rs),
                    "target_weight": w,
                    "spread_sum": sum(r["spread"] for r in rs),
                    "spread_mean": np.mean([r["spread"] for r in rs]),
                    "gross_cost_bps_mean": np.mean([r["cost_bps"] for r in rs]),
                }
            )
    return summary, detail, cells


def bootstrap(rows, lenders, cells, detail, reps=400):
    """Positive exponential tract-cluster perturbations; descriptive stability bands, not causal CIs."""
    rr = [r for r in rows if r["lei"] in lenders and r["cell"] in cells]
    tracts = sorted(set(r["tract"] for r in rr))
    ti = {t: i for i, t in enumerate(tracts)}
    keys = [(c, l) for c in cells for l in lenders]
    ki = {k: i for i, k in enumerate(keys)}
    den = np.zeros((len(keys), len(tracts)))
    sums = den.copy()
    for r in rr:
        k = ki[r["cell"], r["lei"]]
        j = ti[r["tract"]]
        den[k, j] += 1
        sums[k, j] += r["spread"]
    rng = np.random.default_rng(20261022)
    noise = rng.exponential(size=(len(tracts), reps))
    means = (sums @ noise) / (den @ noise)
    weights = {r["cell"]: r["target_weight"] for r in detail}
    draw = np.stack([sum(weights[c] * means[ki[c, l]] for c in cells) for l in lenders])
    bands = []
    for i, l in enumerate(lenders):
        lo, hi = np.quantile(draw[i], [0.025, 0.975])
        bands.append(
            {
                "lei": l,
                "perturbation_p025": float(lo),
                "perturbation_p975": float(hi),
                "replicates": reps,
                "tract_clusters": len(tracts),
            }
        )
    pairs = []
    for i in range(len(lenders)):
        for j in range(i + 1, len(lenders)):
            d = draw[i] - draw[j]
            lo, hi = np.quantile(d, [0.025, 0.975])
            pairs.append(
                {
                    "lei_a": lenders[i],
                    "lei_b": lenders[j],
                    "p025_difference": float(lo),
                    "p975_difference": float(hi),
                    "share_a_lower": float(np.mean(d < 0)),
                }
            )
    return bands, pairs


def run():
    root = ROOT / MORT
    rows = source()
    data, flow = eligible(rows)
    counts = collections.Counter(r["lei"] for r in data)
    lenders = [k for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]]
    names = {
        r["lei"]: r["name"]
        for r in json.loads((root / "data/filers.json").read_text())["institutions"]
    }
    summary, detail, cells = match(data, lenders)
    assert cells, "No common support; do not publish rankings"
    bands, pairs = bootstrap(data, lenders, cells, detail)
    by = {r["lei"]: r for r in bands}
    for r in summary:
        r.update(by[r["lei"]])
        r["name"] = names[r["lei"]]
    sensitivity = []
    for fine in [False, True]:
        for n in [5, 10, 20]:
            ss, dd, cc = match(data, lenders, n, fine)
            if not ss:
                sensitivity.append(
                    {
                        "grid": "fine" if fine else "base",
                        "min_per_lender_cell": n,
                        "lei": "",
                        "cells": 0,
                        "matched_spread": None,
                        "matched_n": 0,
                    }
                )
            for r in ss:
                sensitivity.append(
                    {
                        "grid": "fine" if fine else "base",
                        "min_per_lender_cell": n,
                        "lei": r["lei"],
                        "cells": len(cc),
                        "matched_spread": r["matched_spread"],
                        "matched_n": r["matched_n"],
                    }
                )
    out = root / "outputs"
    balance = []
    disclosures = []
    raw_by_id = {int(r["source_row"]): r for r in rows}
    for l in lenders:
        allr = [r for r in data if r["lei"] == l]
        base = [r for r in detail if r["lei"] == l]
        for v in ["amount", "ltv"]:
            adjusted = sum(
                d["target_weight"]
                * np.mean([r[v] for r in allr if r["cell"] == d["cell"]])
                for d in base
            )
            balance.append(
                {
                    "lei": l,
                    "variable": v,
                    "eligible_mean": np.mean([r[v] for r in allr]),
                    "standardized_within_bin_mean": adjusted,
                    "caution": "Coarsening aligns bin weights, not exact within-bin means.",
                }
            )
        for field in ["lender_credits", "discount_points"]:
            vals = [raw_by_id[r["source_row"]][field] for r in allr]
            disclosures.append(
                {
                    "lei": l,
                    "field": field,
                    "eligible_n": len(vals),
                    "numeric_including_reported_zero": sum(
                        num(v) is not None for v in vals
                    ),
                    "blank": vals.count(""),
                    "NA": vals.count("NA"),
                    "Exempt": vals.count("Exempt"),
                    "other_nonnumeric": sum(
                        num(v) is None and v not in ["", "NA", "Exempt"] for v in vals
                    ),
                }
            )
    write(out / "covariate_balance.csv", balance)
    write(out / "pricing_disclosure.csv", disclosures)
    write(out / "eligible.csv", data)
    write(out / "lenders.csv", summary)
    write(out / "common_cells.csv", detail)
    write(out / "sensitivity.csv", sensitivity)
    write(out / "pair_stability.csv", pairs)
    write(out / "exclusion_flow.csv", [{"stage": k, "n": v} for k, v in flow.items()])
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE loans(lei TEXT,cell TEXT,spread REAL,cost_bps REAL)")
    con.executemany(
        "INSERT INTO loans VALUES(?,?,?,?)",
        [(r["lei"], r["cell"], r["spread"], r["cost_bps"]) for r in data],
    )
    q = "SELECT lei,cell,COUNT(*) n,SUM(spread) spread_sum,AVG(spread) spread_mean,AVG(cost_bps) gross_cost_bps_mean FROM loans GROUP BY lei,cell ORDER BY lei,cell"
    cur = con.execute(q)
    write(
        out / "sql_cells.csv",
        [dict(zip([x[0] for x in cur.description], r)) for r in cur.fetchall()],
    )
    (root / "warehouse.sql").write_text(q + ";\n")
    metrics = {
        "source_rows": len(rows),
        "eligible_rows": len(data),
        "selected_lenders": len(lenders),
        "common_cells": len(cells),
        "matched_rows": sum(r["matched_n"] for r in summary),
        "selected_eligible_rows": sum(r["eligible_n"] for r in summary),
        "replicates": 400,
        "clusters": bands[0]["tract_clusters"],
        "lender_spread_range_naive": max(r["naive_spread"] for r in summary)
        - min(r["naive_spread"] for r in summary),
        "lender_spread_range_matched": max(r["matched_spread"] for r in summary)
        - min(r["matched_spread"] for r in summary),
        "adoption_gate": False,
        "interpretation": "Historical product/observed-risk overlap comparison, not causal lender effects, fair-lending conclusions or individual quotes.",
    }
    dump(out / "metrics.json", metrics)
    print(MORT, metrics)


if __name__ == "__main__":
    run()
