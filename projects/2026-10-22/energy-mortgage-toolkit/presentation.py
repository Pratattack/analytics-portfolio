"""Self-contained offline workbenches and SVG executive evidence charts."""

import json, csv, html
from config import ROOT, ARO, MORT
from common import read, dump

HERE = __import__("pathlib").Path(__file__).parent
CSS = (HERE / "style.css").read_text()


def number(r):
    for k, v in r.items():
        if v == "":
            r[k] = None
            continue
        try:
            r[k] = float(v)
        except (ValueError, TypeError):
            pass
    return r


def display(v, k):
    if v is None:
        return "Not separately disclosed"
    if isinstance(v, (int, float)):
        if k == "year":
            return str(int(v))
        if k == "retained_share":
            return f"{v:.2%}"
        if "spread" in k:
            return f"{v:.3f}"
        if "bps" in k:
            return f"{v:.1f}"
        return f"{v:,.0f}"
    return str(v)


def table(rows, cols):
    return (
        '<div class="table-scroll" tabindex="0" aria-label="Scrollable evidence table"><table><thead><tr>'
        + "".join("<th>" + html.escape(c.replace("_", " ")) + "</th>" for c in cols)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>"
            + "".join(
                "<td>" + html.escape(display(r.get(c, ""), c)) + "</td>" for c in cols
            )
            + "</tr>"
            for r in rows
        )
        + "</tbody></table></div>"
    )


def svgchart(rows, aro):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 400"><rect width="900" height="400" fill="#ffffff"/><text x="30" y="30" font-family="sans-serif" font-size="18">'
        + (
            "2025 book retirement liability · USD billions"
            if aro
            else "2025 historical APR minus APOR · percentage points"
        )
        + "</text>"
    ]
    vals = [r["closing"] / 1e9 if aro else r["matched_spread"] for r in rows]
    lo = min([0] + vals) - (0.1 if not aro else 0)
    hi = max(vals) + (0.3 if not aro else 0.5)
    x = lambda v: 220 + (v - lo) / (hi - lo) * 580
    for i, r in enumerate(rows):
        y = 75 + i * 49
        label = r["ticker"] if aro else r["name"].split(",")[0][:27]
        v = vals[i]
        parts.append(
            f'<text x="15" y="{y+5}" font-family="sans-serif" font-size="13">{html.escape(label)}</text><line x1="{x(0):.2f}" y1="{y-18}" x2="{x(0):.2f}" y2="{y+18}" stroke="#aaa"/>'
        )
        if aro:
            parts.append(
                f'<rect x="{x(0):.2f}" y="{y-11}" width="{x(v)-x(0):.2f}" height="22" fill="#17675f"/>'
            )
        else:
            a = x(r["perturbation_p025"])
            b = x(r["perturbation_p975"])
            parts.append(
                f'<line x1="{a:.2f}" y1="{y}" x2="{b:.2f}" y2="{y}" stroke="#17675f" stroke-width="5"/><circle cx="{x(v):.2f}" cy="{y}" r="6" fill="#17675f"/><circle cx="{x(r["naive_spread"]):.2f}" cy="{y}" r="5" fill="#c17d35"/>'
            )
        parts.append(
            f'<text x="{830:.2f}" y="{y+5}" font-family="sans-serif" font-size="13">{v:.3f}</text>'
        )
    parts.append(
        '<text x="20" y="385" font-family="sans-serif" font-size="13">'
        + (
            "Observed book values; their different portfolios and discount layers limit comparison."
            if aro
            else "Green: common-support mean + tract perturbation band. Gold: unmatched mean. Descriptive only."
        )
        + "</text></svg>"
    )
    return "".join(parts)


def run(slug):
    aro = slug == ARO
    root = ROOT / slug
    out = root / "outputs"
    metrics = json.loads((out / "metrics.json").read_text())
    rows = [number(r) for r in read(out / ("latest.csv" if aro else "lenders.csv"))]
    history = [
        number(r) for r in read(out / ("panel.csv" if aro else "common_cells.csv"))
    ]
    title = (
        "Upstream Retirement Obligation Review"
        if aro
        else "Houston Mortgage Price Comparability"
    )
    if aro:
        manifest = json.loads((root / "data/source_manifest.json").read_text())
        urls = {(m["ticker"], m["report_end"][:4]): m["url"] for m in manifest}
        records = [
            {
                **r,
                "key": r["ticker"],
                "label": r["ticker"],
                "url": urls[r["ticker"], str(int(r["year"]))],
            }
            for r in rows
        ]
        cols = [
            "ticker",
            "year",
            "opening",
            "closing",
            "accretion",
            "revisions",
            "explicit_cash_paid",
            "removed_liability",
        ]
        controls = [
            ("rate", "Assumed common discount rate", 0.06, 0, 0.2),
            ("mean", "Assumed PV-weighted mean retirement year", 15, 1, 30),
            ("cap", "Maximum first-five-year PV share", 0.25, 0, 1),
        ]
        finding = "Six issuers disclose $15.275B in 2025 book retirement obligations. All 35 retained issuer-year ledgers reconcile. Only COP supplies an explicitly tagged cash-paid series in this extraction; other liability removals cannot be relabeled cash spending."
        decision = "Request asset-level timing, original discount layers, settlement invoices and divestiture transfers before using book ARO to size a reserve. The timing workbench produces tight conditional bounds and exposes infeasible assumptions; it does not estimate actual retirement dates."
        badges = [
            "17 original SEC filings",
            "35 reconciled issuer-years",
            "216 timing cases; 18 infeasible",
        ]
        limits = "The panel samples annual disclosures from 2019, 2022 and 2025 filings and their comparable ledger years; it is not a continuous history. APA uses the current parent only. No asset-level quantities, inflation paths, legal transfer recoveries or issuer-specific discount curves are observed. A common nominal rate is a scenario convention, not GAAP remeasurement."
    else:
        manifest = json.loads((root / "data/source_manifest.json").read_text())
        records = [
            {**r, "key": r["lei"], "label": r["name"], "url": manifest["url"]}
            for r in rows
        ]
        cols = [
            "cell",
            "lei",
            "n",
            "target_weight",
            "spread_mean",
            "gross_cost_bps_mean",
        ]
        controls = [
            ("principal", "Hypothetical loan principal · USD", 350000, 80000, 1000000),
            ("rateA", "Offer A annual note rate", 0.065, 0, 0.2),
            ("rateB", "Offer B annual note rate", 0.06, 0, 0.2),
            ("feeA", "Offer A upfront fees · USD", 3000, 0, 100000),
            ("feeB", "Offer B upfront fees · USD", 9000, 0, 100000),
            ("months", "Holding period · whole months", 60, 1, 360),
            ("discount", "Annual nominal opportunity discount rate", 0.04, 0, 0.2),
        ]
        finding = "Of 123,445 originated loans, 32,095 meet the product and completeness contract. Five lenders contribute 9,344 eligible loans, but only 3,867 remain in 18 common cells. Lender APR-spread range falls from 2.001 to 1.902 percentage points after standardization."
        decision = "Use the evidence to define comparable product/risk buckets, then request contemporaneous Loan Estimates and compare rates, fees and exit balances. Do not choose a lender or infer discrimination from this historical table. A lender affiliated with a builder may bundle incentives that these public fields cannot separate."
        badges = [
            "123,445 official loan rows",
            "18 shared cells · five lenders",
            "400 tract perturbations",
        ]
        limits = "Public HMDA omits usable individual credit scores, exact lock dates, negotiated concessions and borrower shopping alternatives. APOR adjusts the rate-spread benchmark for pricing date but cannot remove selection. Costs are gross, not net of lender credits. Loan amounts are privacy rounded. Common support excludes most selected-lender loans; perturbation bands measure descriptive stability, not population sampling or causal uncertainty."
    chart = svgchart(rows, aro)
    (out / "chart.svg").write_text(chart)
    head = f'<header><span class="eyebrow">Prathamesh Singh · Independent finance research</span><h1>{title}</h1><p>Historical public data and explicit decision assumptions · {('filings through 2026-10-21; collected 2026-10-22' if aro else '2025 reporting year; as-served snapshot collected 2026-10-22')}</p></header><main>'
    intro = (
        f'<section><h2>Decision brief</h2><p>{finding}</p><div class="notice">{decision}</div><div class="metrics">'
        + "".join(
            '<div class="metric"><strong>' + b + "</strong></div>" for b in badges
        )
        + "</div></section>"
    )
    report = (
        head
        + intro
        + '<section><h2>Observed evidence</h2><p class="subtle">Scroll the chart horizontally on narrow screens.</p><div class="chart-scroll" tabindex="0" aria-label="Scrollable evidence chart"><img class="chart" src="chart.svg" alt="'
        + html.escape(title)
        + ' observed evidence chart"/></div>'
        + table(
            rows,
            (
                [
                    "ticker",
                    "closing",
                    "accretion",
                    "explicit_cash_paid",
                    "removed_liability",
                ]
                if aro
                else [
                    "name",
                    "eligible_n",
                    "matched_n",
                    "retained_share",
                    "matched_spread",
                    "matched_gross_cost_bps",
                ]
            ),
        )
        + "</section><section><h2>What would change the decision?</h2><p>"
        + limits
        + '</p><p>See METHODS.md, EXECUTIVE_BRIEF.md, INTERVIEW.md and the machine-readable outputs alongside this report. A false adoption gate means production use is withheld pending additional evidence.</p><a href="app.html">Open local analyst workbench</a></section><footer>Locally runnable/offline application. Source publication does not host a live service.</footer></main>'
    )
    fields = (
        '<div class="control"><label for="issuer">'
        + ("Issuer" if aro else "Lender evidence")
        + '</label><div class="bounded"><select id="issuer">'
        + "".join(
            '<option value="' + r["key"] + '">' + html.escape(r["label"]) + "</option>"
            for r in records
        )
        + "</select></div></div>"
    )
    for id, label, v, lo, hi in controls:
        fields += f'<div class="control"><label for="{id}">{label}</label><input id="{id}" type="number" step="any" value="{v}" min="{lo}" max="{hi}"></div>'
    payload = {
        "kind": "aro" if aro else "mortgage",
        "records": records,
        "history": history,
        "columns": cols,
        "metrics": metrics,
    }
    app = (
        head
        + intro
        + '<section><span class="badge">Scenario controls are assumptions, not observations</span><h2>'
        + (
            "Challenge the timing assumptions"
            if aro
            else "Compare two hypothetical mortgage offers"
        )
        + '</h2><form id="form" novalidate><div class="controls">'
        + fields
        + '</div><div class="actions"><button type="submit">Calculate scenario</button><button type="button" class="secondary" id="reset">Reset</button></div></form><p id="error" role="alert"></p><div aria-live="polite"><div class="metric"><small>'
        + (
            "Conditional cash-equivalent interval · USD"
            if aro
            else "Present cost of A minus B · USD"
        )
        + '</small><strong id="result"></strong></div><p id="detail"></p><div id="profile"></div><a id="source" target="_blank" rel="noopener">Original source</a></div></section><section><h2>Inspect the evidence</h2><label for="search">Search evidence</label><input type="search" id="search" placeholder="Try a year, issuer or cell"/><p id="count" aria-live="polite"></p><div class="table-scroll" tabindex="0" aria-label="Scrollable source evidence"><table><thead><tr>'
        + "".join("<th>" + c.replace("_", " ") + "</th>" for c in cols)
        + '</tr></thead><tbody id="history-body"></tbody></table></div></section><section><h2>Interpretation limits</h2><p>'
        + limits
        + '</p><a href="report.html">Read the executive report</a></section><footer>Works offline. Scenario outputs are modeled and do not approve investments, advise a mortgage selection or forecast an issuer.</footer></main>'
    )
    for name, body in [
        ("report", report),
        (
            "app",
            app
            + '<script type="application/json" id="dataset">'
            + json.dumps(payload, separators=(",", ":"), allow_nan=False).replace(
                "</", "<\\/"
            )
            + "</script><script>"
            + (HERE / "workbench.js").read_text()
            + "</script>",
        ),
    ]:
        (out / (name + ".html")).write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'
            + title
            + "</title><style>"
            + CSS
            + "</style>"
            + body
            + "</html>"
        )


if __name__ == "__main__":
    for p in [ARO, MORT]:
        run(p)
