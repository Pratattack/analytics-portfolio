# Does a fitted currency hedge beat a simple 50% policy?

A fitted hedge lowers the historical tail-cost diagnostic, but does it justify the complexity? Test it against uniform coverage after netting the cash flows that genuinely offset.

## Finding
Within-currency netting reduces the hypothetical transaction base from $17.2 million gross to $6.8 million net, or 60.5%. On the later-month replay, the frozen fitted policy has an empirical 90% adverse-cost CVaR of $66,474 versus $85,969 for uniform 50% coverage, including an assumed charge. That is a historical diagnostic, not an achieved hedge result or future guarantee.

## Decision use
Confirm which flows can legally settle together before hedging gross positions. Require a proposed allocation to beat a simple coverage rule on later observations, using actual execution costs before adoption. The historical result supports further investigation, not an implementation claim.

## Method
Normalize quotes to USD per foreign-currency unit, audit missing values without forward filling, and separate completed months from partial October. Net same-currency payments and receipts. Fit a constrained empirical adverse-cost CVaR policy on earlier months, freeze it and compare with uniform 50% coverage on 45 later months. Reconcile notional totals in SQL and replay cash costs independently in JavaScript.

## Limits
The budget-lock proxy freezes covered exposure at base spot; it is not a quoted forward or option. Rate differentials, collateral, credit, basis and bid-ask costs are omitted. Netting assumes same-currency, same-date settlement. Only 45 holdout months provide about 4.5 observations of tail mass. Current history may be revised; no real-time backtest, statistical superiority, actual savings or predictive coverage is claimed.
