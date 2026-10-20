# Bank deposit cost attribution

Across 4,018 comparable insured banks, quarterly domestic deposit interest expense changed by $-5.01bn from Q2 2025 to Q2 2026. The proxy-rate component contributes $-10.31bn.

## Decision

Separate balance growth, interest-bearing mix migration and the residual proxy-rate effect before recommending blanket repricing. This is an accounting bridge for a bank-treasury workstream, not a forecast of depositor behavior or an assessment of bank safety. The review queue is ranked by positive proxy-rate expense contribution, with asset-size peer medians for context. No savings are booked.

## Evidence

The pinned FDIC panel contains 48,814 bank-quarters across 11 dates. The latest insured domestic-bank universe has 4,238 institutions and $20.722tn total deposits, consistent with the Q2 2026 QBP rounded industry scale. 89 bank-quarters have expense/contract flags. The screen keeps 4,018 matched banks, representing 91.0% of latest domestic deposits. It excludes 220 latest institutions because of missing accepted pairs or a greater-than-30% balance change; the latter is a structural-break heuristic, not proof of a merger. Before that growth screen, the matched expense change is $-3.81bn.

The screened change decomposes into balance volume $5.242bn, mix $0.057bn, and proxy rate $-10.310bn. Six possible replacement orders allocate interactions symmetrically. The aggregate arithmetic residual is 0.00000000 thousand dollars. Exact reconciliation does not validate an economic causal interpretation.

## Business tradeoff

The scenario grid models a generic $1bn interest-bearing balance, a 2.5% starting proxy rate, a 4.5% replacement funding rate, 10–25bp cuts, 25–100% targeted shares, 0–30% attrition and $100,000 annual fixed cost. These inputs are invented, separate from the empirical bank bridge. A larger cut saves more on retained balances but can increase replacement funding costs if customers leave. Real adoption needs account-level rates, contractual renewal dates, customer elasticities, liquidity constraints and treasury approval.

## My understanding and interview defense

A bank's expense can fall while its deposit base grows. The bridge asks how much of the observed change comes from volume, from the share that earns interest and from expense per interest-bearing balance. The rate is derived using two quarter-end balances, not regulatory daily-average deposits, and it absorbs timing, composition and measurement effects. It is neither a quoted product rate nor a causal deposit beta.

I should be able to hand-compute one three-factor bridge, explain why order averaging avoids an arbitrary interaction allocation, trace every input to its FDIC JSON pointer, show which bank-quarters fail YTD reconciliation and demonstrate how attrition erases a seemingly attractive rate-cut saving. I should also explain that size peers omit business-model differences and certificate matching does not completely neutralize acquisitions.
