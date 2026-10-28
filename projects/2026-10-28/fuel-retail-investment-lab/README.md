# Fuel Retail Investment Decision Lab

An independent, anonymized re-analysis by Prathamesh Singh of two user-supplied April 2026 feasibility and risk documents. The project asks which sales, cost, staffing and financing assumptions would support a fuel-retail development, and which unresolved evidence should prevent a numerical screen from being treated as a decision to proceed.

## Finding in the reference illustration

The source's average nonfuel receipts total $138,031 per month and reconcile to its category estimates. Under explicit hypothetical costs and financing, stabilized cash available for debt is $16,504 per month against $16,888 in debt service: 0.98x coverage. A six-month sales ramp lowers opening-year coverage to 0.61x. These are scenario results, not actual project performance or proof of actual infeasibility.

Four of 31 risk labels conflict with the report's own rating thresholds. All eight site-specific evidence gates remain unverified. A corrected risk label is not a calibrated probability, and a coverage pass does not establish site feasibility, valuation, financing approval or readiness to proceed.

## Open the project

- `outputs/workbench.html`: self-contained interactive decision lab. Open directly in a modern browser; it needs no account, server, API key or network access for recalculation.
- `outputs/report.html`: fixed reference research report with sources, charts, methods and limitations. This is also self-contained for reading.
- `docs/executive_memo.md`: concise finding and decision implications.
- `outputs/*.csv`: scenario comparisons, risk audit, monthly cash flow, source reconciliation, SQL parity and sensitivity.

The workbench can save or import current assumptions as JSON, download a scenario memo, and export the current cash flow and coverage grid. Files are generated locally. There is no telemetry, browser storage or upload endpoint. In invalid input states it retains the last valid results and displays an explicit error.

## Reproduce

Python 3.11 or later and Node.js 18 or later were used.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python analyze.py
python build_review.py
python -m unittest discover -s tests -v
node tests/test_parity.cjs
python verify.py
```

`analyze.py` is offline. It uses the sanitized report extracts and default assumption register, runs the cash-flow model, checks source totals, independently reconciles contribution in SQLite, and regenerates scenarios and vector charts. `build_review.py` packages the portable HTML and fixed report. Python and JavaScript are separately implemented and compared over ordinary and boundary scenarios.

## Data and provenance

`data/report_estimates.json` contains selected numerical estimates from F01, an investment decision memo. It is not the underlying market study referenced by that memo, which was not supplied. `data/risk_register.json` preserves the 31 source ratings with rewritten generic descriptions. `data/assumption_register.csv` classifies every model input and states its units and basis. `data/decision_gates.csv` identifies the evidence still needed. `docs/source_audit.md` maps findings to report pages and explains unsupported claims.

Original attachments are intentionally excluded. The project owner authorized use of their contents with names and the exact address omitted. Personal names, business names from the private reports, exact address, city, postal code, parcel identifiers and block-group IDs are not included in this project. This is Prathamesh Singh's analytical re-analysis; the project does not claim authorship of the original reports or employment with a report subject.

External sources were retrieved on 28 October 2026. Raw official snapshots and SHA-256 hashes are in `data/external/` and its manifest:

- Texas Comptroller, expenditure object 7260: retailer lottery compensation is at least 5% of ticket sales; bonuses are separate. The default uses 5%, not an inferred project contract.
- TCEQ RG-475b, revised January 2024: installation responsibilities, notifications, registration, permitted materials and secondary containment. This is general guidance, not verification of a site's approval or environmental condition.
- TxDOT traffic-count source page: identifies authoritative data access. No count station was matched to the private location, so the report's approximate traffic figure remains an unverified estimate and not a current official count.

No external wage, construction-cost, lender-rate or category-margin benchmark is asserted. Those inputs are deliberately hypothetical because scope-matched evidence is unavailable.

## Model conventions

The source sales categories are assumed mutually exclusive. Lottery values are interpreted as face-value ticket sales. Fuel is reported in gallons, with no margin supplied. The model replaces ticket proceeds with assumed commission, applies category gross margins and nonfuel card fees, adds fuel contribution net of variable fuel costs, then subtracts loaded labor, overhead and maintenance capital reserves. Cash available for debt is pre-tax and is not accounting net income or a lender-certified covenant measure.

The monthly debt payment is fixed-rate, amortizing and has no balloon or refinancing. Loan-to-cost applies to acquisition, soft cost and hard cost including fully spent contingency. Acquisition/soft cost are paid at closing; hard-cost draws occur evenly during construction after added delay. Development interest is paid by the sponsor on the average monthly drawn balance. Carry, development interest, loan fees and opening working capital are equity funded, outside the eligible loan budget.

Opening working capital is inventory and other working-capital investment, excluding the loss reserve. It is funded once and is not expensed again. Peak sponsor funding adds maximum cumulative operating deficits through 36 operating months; ongoing losses after that horizon are not included. Ramp-up scales sales while staffing and overhead begin in full. Core-first excludes a wash; full scope adds explicitly hypothetical wash capital, sales, labor and maintenance. Future option value is not modeled.

The financing-capacity ceiling is an algebraic stabilized debt-coverage screen at assumed leverage. It is not fair value or a maximum price to offer. The fuel threshold holds nonfuel contribution fixed; the all-sales threshold holds staffing fixed. Real capacity constraints can invalidate either scenario. Annual totals mean twelve operating months, not a specific calendar year.

## Limitations

Missing evidence includes the underlying feasibility study, current traffic station data and directional exposure, category definitions, sales-tax treatment, supplier/franchise arrangements, operating margins, construction bids, loan terms, civil site fit, access approval, environmental condition and sponsor capacity. Demographics alone do not prove demand or a financial hedge. Existing estimates should not be described as observed sales.

The model excludes income taxes, depreciation, tax shields, terminal proceeds, appreciation, refinancing, prepayment, balloons, future working-capital changes and itemized fuel inventory float. Fixed overhead is a single editable allowance. No NPV, IRR, actual savings, business impact, failure probability or expected-loss estimate is claimed. It does not provide engineering, environmental, legal or lending approval.

## Attribution and license

Original code, generic analytical writing and vector chart composition are MIT licensed. The original private attachments are not redistributed. External government snapshots retain their source terms. TCEQ explicitly permits reproduction of its original material with acknowledgment. This project acknowledges TCEQ, TxDOT and the Texas Comptroller; no endorsement is implied. Matplotlib, NumPy and pandas are installed separately under their own licenses. The HTML uses system fonts and original SVG components, with no proprietary assets or external font dependencies.
