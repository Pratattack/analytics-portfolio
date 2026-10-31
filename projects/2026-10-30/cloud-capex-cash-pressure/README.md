# Cloud Capital Spending & Cash-Flow Pressure

Alphabet's January-September 2026 cash purchases of property and equipment exceed operating cash flow by $4.804 billion. On a common trailing-year basis, operating cash remaining after those purchases is still $19.747 billion. The measurement window changes the funding story.

## Start with the evidence
Open `outputs/report.html` for the question, findings and limits, or `outputs/workbench.html` for the self-contained scenario tool. These are independent portfolio research prototypes. They do not claim company adoption, achieved savings, AI investment returns or realized hedge performance.

## Reproduce offline

Requires Python 3.11+ and Node.js 18+ for full verification.

```bash
python -m pip install -r requirements.txt
python analyze.py
python verify.py
```

`data/` contains the pinned evidence and source manifest, including URLs, timestamps, dates, units and raw-source hashes. `data_hashes.json` pins included inputs. `reconcile.sql` independently checks derived totals. `outputs/` includes SVG charts, CSV evidence and the browser-local calculator. `docs/executive_memo.md` explains decision use. The full source is needed for Python reproduction; extract the downloadable outputs package before opening its HTML.

## Interpretation and limitations
These are consolidated company cash flows, not isolated AI or cloud-segment spending. Cash property purchases omit noncash finance-lease additions and do not measure total investment commitments. Cash after capex is before acquisitions, financing and shareholder distributions and is not a liquidity or covenant test. Fiscal YTD spans differ across companies and are never ranked as equal windows. Historical facts are original-current disclosure selections under a 120-day filing window, with prior YTD comparatives from the same current filing; they are not a real-time investment backtest. Amazon is excluded from the paired PPE comparison because its productive-asset cash tag has a different scope. No AI return, stock valuation or financing recommendation is inferred.

Browser rendering, mobile interaction, focus traversal and download clicks have not been tested because the owner excludes browser operation. Numeric calculator parity is checked independently between Python and JavaScript. There are no remote fonts, API keys, server calls, telemetry or automatic user-data storage in the offline tools.
