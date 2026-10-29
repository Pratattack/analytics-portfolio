# Private Credit Measurement and Funding Exposure

A 2026 measurement change made private-credit sectors more visible in the Financial Accounts. This project reconciles what the published balances mean before applying a clearly hypothetical asset mark-down. The source observation is **2025 Q4**, published **16 October 2026**, not a live 2026 portfolio.

## Decision and finding

For credit researchers and investment analysts: which funding structures require further diligence, and which totals must not be added together? Table 1 reports $1,458 billion of private loans to U.S. businesses. The final nonfinancial-business debt table reports $1,310 billion, or 5.62% of its denominator. Those scopes differ. Bank loans to private-credit vehicles are an intermediation layer, not another independent loan to the same end borrower.

The domestic reported bank-funding ratios and equity shares differ by vehicle type. The tool applies an assumed mark to U.S. private loans and corporate equities, reduces assets and equity by the same amount, preserves fixed liabilities and the source rounding residual, then compares the result with an explicitly hypothetical equity/assets screen. It also solves the loan mark at which that screen would be crossed. It does not prescribe a regulatory ratio or covenant.

## Comparability controls

Raw HTML is parsed using named rows and numeric columns rather than reading plotted bar heights. USD billions and trillions are explicitly converted. Components tolerate published rounding, not arbitrary reconciliation errors. Blank source cells remain null. In particular, CLO equity is not separately reported in this table, so CLOs are excluded from equity-buffer comparisons. This is not a claim that CLO equity or loss protection is zero. Foreign vehicle estimates and possible syndicated-loan overlap inherit the note's methodological limitations.

The public aggregate tables do not provide confidential Form PF microdata, fund-level dispersion, debt maturities, withdrawal terms or unencumbered liquidity. There is no redemption simulation, default probability, stress-test validation, loss forecast or institution-level contagion model. Immediate marks are accounting scenarios, not estimated defaults or realized losses.

## Source

Federal Reserve FEDS Notes, Introducing Private Credit into the Financial Accounts of the United States, October 16, 2026. Table 1 and final debt composition table. Exact URL, publication date, observation period, retrieval timestamp and raw HTML hash are in `data/source_manifest.json`. Re-run analysis offline to reproduce the pinned publication. Refreshing the HTML is a deliberate source change and requires reviewing the extraction and findings again.

## Reproduce

Python 3.11 or later and Node.js 18 or later were used. From this project directory:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python analyze.py
python -m unittest discover -s tests -v
node tests/parity.cjs
python verify.py
```

Open `outputs/report.html` or `outputs/workbench.html` directly after extracting the project package. Both are self-contained HTML with no remote fonts, account, server, API key, telemetry or automatic browser storage. Supporting CSV links require keeping the extracted folder structure. The tool lets you download its current scenario. Browser interaction was not tested because the owner prohibited browser operation.

Original code and analytical writing are MIT licensed. NumPy, pandas, lxml and Matplotlib are installed separately under their own licenses. Charts are code-generated from source data or explicitly labeled scenarios. No generated artwork is presented as evidence.

## Project files

- `data/`: pinned source snapshots/extracts, source dates, URLs and hashes.
- `analyze.py`: parsing, analytical checks, SQL reconciliation, scenario outputs, charts and HTML generation.
- `reconcile.sql`: independent aggregate arithmetic.
- `outputs/`: analytical report, browser-local scenario tool and downloadable evidence.
- `docs/executive_memo.md`: finding, decision use and limitations.
- `tests/` and `verify.py`: analytical, cross-language and static checks.

No GitHub push or website deployment is performed by these scripts. Source figures are historical observations, not forecasts. Scenario parameters are not probabilities.
