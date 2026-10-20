# Banking economics: explanation, resume language and interview defense

## Plain-English understanding

This project asks why banks' deposit interest expense changed, rather than assuming every change came from pricing. It separates the amount of deposits, the share that earns interest, and an effective-rate proxy derived from reported expense. Across 4,018 screened banks, quarterly domestic deposit expense fell $5.012bn between Q2 2025 and Q2 2026 even though balance growth added cost. The decomposition helps an economic researcher or treasury team distinguish competing explanations before recommending action.

The decomposition is exact accounting, not causal econometrics. The proxy rate uses two quarter-end balances rather than daily averages, so it absorbs timing and product-composition effects. The six-order Shapley calculation allocates interactions without choosing an arbitrary order; a separate closed-form formula verifies every result. A hypothetical calculator then shows the management tradeoff: cutting rates saves money only on retained balances, while lost deposits may need more expensive replacement funding. Those scenario outcomes are not observed savings.

## Accurate resume bullets

- Built a reproducible Python/SQL banking-economics panel of 48,814 official FDIC bank-quarter records across 11 quarter ends, with source-pointer lineage, quarter/YTD reconciliation and explicit cohort exclusions.
- Decomposed a $5.012bn observed quarterly domestic deposit-expense decline across 4,018 screened banks covering 90.96% of latest domestic deposits; independently reconciled volume, mix and proxy-rate contributions and tested structural-break filter sensitivity.

The expense decline is an observed cohort change, not a saving achieved by the author or a causal policy effect.

## Five interview questions and grounded answers

1. **What is the economic question and baseline?** I ask whether funding expense changed because balances grew, deposits shifted toward interest-bearing accounts, or expense per interest-bearing balance changed. The simple baseline applies the prior period's mix and proxy rate to the current period's average balances. Its gap from actual expense reveals what a volume-only explanation misses; it is an accounting counterfactual, not a validated forecast.
2. **Why use Shapley attribution?** Expense equals average domestic deposits times the interest-bearing share times the annualized proxy rate divided by four. Changing several factors creates interactions. I average each factor's marginal contribution over all six replacement orders. An independently implemented trilinear closed-form allocation checks every bank, and the contributions sum to observed expense change.
3. **Why is the rate a proxy?** The denominator is an average of two endpoint balances, not daily-average deposits or a product-level quoted rate. Timing, acquisitions and within-quarter mix can affect it. The identity is exact by construction; that does not identify pricing power, a monetary-policy beta or depositor behavior.
4. **How did selection change the result?** The principal matched cohort excludes missing/flagged target-period proxies and balance changes above 30%. It contains 4,018 banks and 90.96% of latest domestic deposits. Before the growth screen the matched expense decline is $3.810bn rather than $5.012bn. I expose 20%, 30%, 50% and no-growth-filter cases because certificate matching does not fully neutralize mergers.
5. **How would you decide whether a rate cut is worthwhile?** Compare savings on targeted retained balances with incremental replacement-funding expense and fixed costs. For a generic assumed $1bn balance, 2.5% current rate, 25bp cut on 25% of balances, 4.5% replacement rate and $100,000 fixed cost, the break-even attrition is 9.33%. These are clearly labeled assumptions. A real recommendation needs account-level balances, renewal schedules, measured retention elasticities and liquidity constraints.
