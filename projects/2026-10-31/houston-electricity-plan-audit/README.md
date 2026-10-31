# Houston Electricity Plan Audit

**When does the cheapest electricity plan stop being cheapest?**

Independent portfolio research by Prathamesh Singh. Approved release snapshot: 31 October 2026.

[Portfolio case study](https://prathameshsingh.com/projects/houston-electricity-plan-audit/) | [Interactive calculator](https://prathameshsingh.com/demos/houston-electricity-plan-audit/app/index.html)

## Finding

Under Discount Power's 4 October 2026 Bill Credit Bundle 12 pricing terms, reducing consumption from 1,000 to 999 kWh increases the modeled recurring bill from $72.66 to $197.47. The $125 usage credit disappears. The resulting $124.81 difference is contract arithmetic, not an observed household outcome.

Two hypothetical profiles each total 12,000 kWh across twelve 30-day billing cycles. The steady profile earns twelve credits, while the uneven profile earns six. With energy terms and October delivery charges held constant, their modeled costs are $871.91 and $1,621.91: a $750 difference. This is not a population estimate or a savings claim.

## Open the project

Open `app/index.html` in a browser. It is self-contained, works without a server or external scripts, and supports monthly comparisons, historical/prepaid filters, editable 12-cycle scenarios and CSV exports. No personal data is uploaded. The main source register links to original provider documents.

## Reproduce

Python 3.10+ and Node.js 18+ are sufficient for the core checks. Install the chart dependency with `python3 -m pip install -r requirements.txt`.

```sh
python3 src/analyze.py
python3 src/build_evidence.py
python3 src/build_preview.py
python3 -m unittest discover -s tests -v
node tests/ui_smoke.js
sqlite3 results/audit.sqlite < src/queries.sql
```

On systems without the SQLite command-line program, use Python's built-in `sqlite3` module. Python recomputes the evidence from the manually transcribed, reviewed charge components in `data/plans.json`; extraction is not presented as an automated parser. `app/model.js` independently implements the arithmetic and is checked against Python on 189 combinations.

## Evidence

- Seven modeled contracts from four providers, including four October labels and three older labels.
- Twenty-one source-published price points reconciled within 0.05 cents/kWh, the rounding half-unit of a one-decimal cent quote.
- Twenty-one candidate URLs attempted, eleven complete PDF documents downloaded. Four complete labels excluded from the main engine because additional information or charges are required.
- Two Discount Power contracts share the same monthly price function. Contract count is not a count of independent pricing structures.
- Each source has its original URL, retrieval timestamp, SHA-256 hash and download status in `data/source_manifest.json`. Term-level provenance appears in `data/evidence.csv`.
- Sources are linked, not licensed as our work. Provider PDFs and full extracted text are not redistributed. Use `python3 src/download_sources.py` to attempt independent source reverification. Changed content is saved separately and never silently replaces the original extraction.

The complete local source check passed when this preview was produced. In the shared package, the raw-source hash test is skipped until matching provider PDFs are downloaded; the structured-data analysis and other checks remain reproducible. A document's original bytes may no longer be obtainable if its URL changes.

## Important boundaries

This is a purposive contract audit, not an exhaustive comparison or current enrollment recommendation. Rates and availability can change, and eligibility is unverified. Date-normalization changes delivery charges only; it does not turn an old offer into a current one. Twelve-cycle totals are conditional scenarios, not forecasts. Six- and nine-month contracts are excluded from the twelve-cycle comparison. The Payless historical label reserves price-change discretion, so its multi-cycle scenario is especially conditional.

The model excludes taxes, deposits, optional services, penalties, local special charges and nonrecurring fees. Time-of-use and solar offers are not reconstructed without interval or export data. No causal, behavioral or realized-savings claim is made.

## Contents

- `docs/executive_memo.md`: question, findings, decision implications and limitations.
- `docs/methodology.md`: formulas, normalization and design decisions.
- `docs/interview_notes.md`: how to understand and defend the analysis.
- `docs/portfolio_case_study.md`: proposed website copy for approval.
- `results/`: charts, CSV evidence, SQLite database and machine-readable findings.
- `tests/`: 21 tests, including boundary cases and Python/JavaScript agreement.

## Attribution and license

Original code is MIT licensed. Source facts and provider documents retain their original ownership; the MIT license does not cover those documents. Matplotlib is used under its upstream license; no fonts, icon packs, logos or paid services are bundled. System fonts are used in the app. No affiliation, provider endorsement or client engagement is claimed.
