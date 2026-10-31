# Currency Netting & Hedge-Policy Challenge

Matching same-currency payments and receipts reduces the hypothetical basket’s hedged-notional base from $17.2 million gross to $6.8 million net, a 60.5% reduction. On the later-month replay, the fitted policy has lower empirical 90% CVaR than a uniform 50% hedge ($66,474 versus $85,969).

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
Cash flows are hypothetical, same-currency and same-date, valued in USD at the base spot; legal netting and timing feasibility are assumed. The budget-lock proxy freezes covered cash flows at base spot and charges an assumed 15 basis points per monthly horizon. It is not a quoted forward, option or executed hedge and excludes rate differentials, basis, collateral, credit and bid-ask costs. Historical cash-cost replay is not realized P&L or a forecast. Only 45 holdout months are available, leaving about 4.5 observations of tail mass. No future coverage guarantee or significant outperformance is established. FRED history may be revised; no real-time vintage backtest is claimed.

Browser rendering, mobile interaction, focus traversal and download clicks have not been tested because the owner excludes browser operation. Numeric calculator parity is checked independently between Python and JavaScript. There are no remote fonts, API keys, server calls, telemetry or automatic user-data storage in the offline tools.
