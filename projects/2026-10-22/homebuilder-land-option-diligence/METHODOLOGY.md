# Methodology and pre-specified decision boundary

## Empirical scope

Select PHM, MTH and KBH because their original filings disclose contract prices and deposits with identifiable boundaries. This is a purposive diligence sample, not a representative industry estimate. Use annual 2019–2025 originals plus the latest filed 2026 quarter as available through 2026-10-21. Comparative 2018 totals and historical categories are included when disclosed. Select the latest available disclosure for a given issuer/scope/date; this is an as-of-cutoff disclosure panel, not a backtest of as-known-then data. No causal or predictive inference is made.

PHM: deposits include pre-acquisition costs; disclosed price is already remaining. MTH: price is aggregate and cash deposits are credited; committed means internal acquisition status, not mandatory specific performance. KBH: cash deposit price is aggregate; separately disclosed pre-acquisition costs belong in the observed cost register but are not credited again against remaining purchase price. Totals and their component rows are never added together. Report dates differ across issuers.

Highest declared precision resolves rounded narrative duplicates only if rounding intervals overlap. Contradictory same-scope values stop extraction. Meritage's historical nonrefundable option, nonrefundable purchase and refundable purchase components are summed to construct off-balance-sheet committed scope; a reported aggregate can contain recorded balance-sheet contracts. The 2026 reused tag follows its actual table caption, not its legacy taxonomy name. Refund rights remain unobserved.

## Conditional model and baseline

Let K be remaining purchase price, D reported deposits, V the assumed present net value of land after all subsequent development costs, and A = refund_fraction × D the assumed walkaway recovery. Immediate exercise payoff is V−K, immediate abandonment A, and the baseline is max(V−K,A). Sunk deposits are not paid again. Exercise exceeds abandonment only when V/K > 1+A/K. With A=0 the deposit does not change that marginal threshold.

For a hypothetical one-year extension with unchanged strike, state values uV/dV, assumed probability p, discount r and immediately paid extension fraction e, wait payoff = [p max(uV−K,A) + (1−p) max(dV−K,A)]/(1+r) − eK. Compare with the best immediate baseline. The application exposes every input; boundaries are enforced identically in Python and JavaScript. The grid is V/K in {0.8,1,1.2}, p in {.25,.5,.75}, r in {.05,.1,.2}, e in {0,.02,.05}, u=1.25, d=.75. Refund sensitivities add {0,.5,1}. These are deliberately broad challenge assumptions, not empirically calibrated probabilities or prices.

An aggregate option cannot value each tract's selective exercise. The convex max operation on a portfolio differs from the sum of individual options. Correlation, minimum-take schedules, operating control, tax, financing and extension enforceability are absent. The displayed policy is conditional on the assumed common-state aggregate illustration. No dollar result is a measured saving, option appraisal or recommended land trade. No confidence interval is appropriate for unestimated probabilities.

## Acceptance gates

Require immutable inputs, exact context selectors, category totals, full source lineage, independent source arithmetic, independent policy enumeration and reproducibility. Require actual browser acceptance before publication. Real investment adoption stays false until parcel-level valuations and contractual rights are supplied, regardless of software success.
