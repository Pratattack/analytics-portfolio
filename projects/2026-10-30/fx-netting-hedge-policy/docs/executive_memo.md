# Currency netting and hedge-policy challenge

Matching same-currency payments and receipts reduces the hypothetical basket’s hedged-notional base from $17.2 million gross to $6.8 million net, a 60.5% reduction. On the later-month replay, the fitted policy has lower empirical 90% CVaR than a uniform 50% hedge ($66,474 versus $85,969).

## Decision use
Confirm same-currency settlement offsets before purchasing hedges on gross flows. Compare any fitted allocation with uniform coverage on later observations, including deal charges. The gate for production adoption remains unestablished: limited later-month tail evidence and unquoted instruments prevent an implementation claim.

## Limits
Cash flows are hypothetical, same-currency and same-date, valued in USD at the base spot; legal netting and timing feasibility are assumed. The budget-lock proxy freezes covered cash flows at base spot and charges an assumed 15 basis points per monthly horizon. It is not a quoted forward, option or executed hedge and excludes rate differentials, basis, collateral, credit and bid-ask costs. Historical cash-cost replay is not realized P&L or a forecast. Only 45 holdout months are available, leaving about 4.5 observations of tail mass. No future coverage guarantee or significant outperformance is established. FRED history may be revised; no real-time vintage backtest is claimed.
