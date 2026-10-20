# Method, accounting contracts and dictionary

The explicit simple baseline holds the before-period interest-bearing mix and proxy rate constant while applying the after-period endpoint-average domestic balance: E_baseline = D_after × s_before × r_before / 4. It totals $89.466bn versus $78.903bn observed in the screened comparison cohort. The difference is an accounting diagnostic, not an out-of-sample forecast error or a causal rate effect. Tests independently reconcile it using E_before × D_after / D_before.

## Decision and scope

A hypothetical bank-treasury research team needs to explain changing funding expense and decide what further evidence to gather before deposit repricing. The industry is insured domestic banking, including commercial banks and savings institutions, rather than consumer-credit-card acquisition. Quarterly API filters require `INSAGNT1:DIF` and exclude `BKCLASS:OI` foreign branches. Do not filter on today's activity status to reconstruct historical panels.

Eleven quarter-end universes run from December 31, 2023 through June 30, 2026. Q4 2023 supplies lagged endpoint balances for Q1 2024. The principal comparison is Q2 2025 versus Q2 2026. Using the same quarter reduces seasonal/day-count differences but does not establish causality. All responses are the October 19, 2026 snapshot; source index metadata are retained. Historical publication/revision vintages have not been reconstructed. There is no forecast, out-of-time model training or causal rate elasticity estimation.

## Input and expense gates

Natural key is FDIC certificate × report date. File date, API total and retrieved row count must agree; duplicates fail. API limit is 10,000, above each date's universe; no unverified pagination truncation is accepted. Missing or nonfinite required numeric values fail that row's contract and remain missing, not zero. Enforce 0 ≤ domestic noninterest-bearing deposits ≤ domestic deposits ≤ total deposits, plus nonnegative deposit expense.

For Q1, compare reported quarterly domestic deposit expense with YTD expense. For later quarters with a predecessor, compare quarterly expense with current YTD minus previous YTD expense. Tolerance is $1,000, because the API reports thousands of dollars. Disagreements are flags; they may reflect source adjustments, merger accounting, revisions or other effects not identified here. Do not assume they are arithmetic errors. Flagged current bank-quarters are excluded from accepted proxies, while previous endpoint stocks can still be used if their stock contracts hold. Report all flags and the resulting cohort exclusions.

If no previous quarter exists, no endpoint-average proxy is produced. For non-Q1 first observed quarters, YTD reconciliation is unavailable and is not claimed. The source record remains in the industry totals. Latest-universe count must equal the Q2 2026 reference count of 4,238 institutions. Industry totals include quarantined rows as reported, with their issues visible; cohort analysis does not silently replace industry totals.

## Exact three-factor identity

For a bank-quarter:

- D = average of previous and current endpoint domestic deposit balances.
- B = average of previous and current endpoint (domestic deposits − domestic noninterest-bearing deposits).
- s = B/D, the endpoint-average interest-bearing share.
- r = 4 × reported quarterly domestic deposit expense / B, an annualized **proxy** rate.
- E = D × s × r / 4, exactly equal to reported quarterly expense by construction.

Require B ≥ $1m for numerical stability. The endpoint average is not the regulatory daily-average balance. r absorbs intraperiod timing, product mix, acquisition/revision effects and the limitations of that denominator. It is not a posted offer rate or a pure price effect. Four-times-quarter annualization is a convention, not an annual earnings forecast.

For before/after factor vectors, calculate the marginal expense change from replacing each factor across all six order permutations. Average each factor's marginal contribution. The three signed contributions sum exactly to observed expense change. An independent analytic formula verifies every bank: for factor x with the other factors y,z, its contribution is Δx × [y0z0 + (Δy z0 + y0 Δz)/2 + Δy Δz/3] / 4. This is a fair allocation of accounting interactions, not an identified causal effect.

## Matched cohort and sensitivity

Match the same certificate in both target periods and require accepted proxies. Exclude bank pairs with absolute growth above 30% in average domestic deposits year-over-year or current endpoint domestic deposits quarter-over-quarter. This heuristic reduces conspicuous structural breaks but is not a merger detector and does not neutralize all M&A. Excluded banks are retained in an auditable register. Show 20%, 30%, 50% and no-growth-filter sensitivities and the full unscreened bridge.

Size-only peer buckets use comparison-period assets: below $1bn, $1bn–$10bn, above/equal $10bn. Each bank's median comparison excludes itself. Business model, geography and funding-products differ within buckets; a rate gap is context for review, never a claim of recoverable savings. The review queue orders positive proxy-rate expense contributions; it is not an insolvency, fraud or credit-risk assessment.

No population confidence interval is fabricated: this is an accounting census-like administrative panel with cohort exclusions, not a random sample. Uncertainty is primarily definitional, selection-related and behavioral. Sensitivity and adoption gates address those limitations; extra resampling would not identify a causal pricing effect.

## Hypothetical repricing scenario

Let B be modeled interest-bearing balance in **USD**, t targeted share, a attrition among targeted balances, c rate cut, r current proxy rate, w replacement funding rate and F annual fixed cost. Retained-balance savings = B t (1−a)c. Additional replacement cost = B t a(w−r). Net annual modeled benefit = savings − additional replacement cost − F. All lost funding is replaced; replacement principal is not an expense, only incremental interest is counted.

When c+w−r > 0, break-even attrition is (c−F/(Bt))/(c+w−r). A negative threshold means there is no profitable nonnegative attrition level under these assumptions; a threshold outside [0,1] is retained rather than presented as a feasible observed rate. When the denominator is nonpositive, a simple maximum-attrition threshold is not returned. CLI bounds require c≤r and valid fractions. Inputs must be supplied as decimal annual rates, except `--cut-bp` in basis points.

The grid uses a generic invented $1bn bank balance, 2.5% current rate and 4.5% replacement rate. None is presented as a named bank's product-level truth. No empirical elasticity, customer targeting model, liquidity coverage model or campaign response is estimated.

## Source dictionary

All source balance, income and expense amounts are **thousand USD**, nominal. The official dictionary is preserved as `data/raw/risview_properties.yaml.gz`.

| Field | Meaning |
|---|---|
| CERT, NAME, STALP | FDIC certificate, reported name and state |
| REPDTE | Quarter-end date, YYYYMMDD |
| BKCLASS, INSAGNT1 | Institution class and primary insurance fund; universe filters |
| ASSET | Total assets, used only for descriptive size peers |
| DEP, DEPDOM | Total deposits and domestic-office deposits |
| DEPNI, DEPNIDOM | Noninterest-bearing total and domestic deposits; DEPNI retained in raw source |
| EDEP, EDEPDOM | YTD total and domestic deposit interest expense; total expense retained in raw source |
| EDEPDOMQ | Reported quarterly domestic deposit expense, principal outcome |
| NETINCQ | Quarterly net income, preserved for context; not used to value repricing |
| DEPUNINS | Reported estimated uninsured deposits; preserved, not converted into a run-risk score |

## Derived dictionary

| File / columns | Meaning |
|---|---|
| source_audited_quarterly_panel.csv.gz | Accepted endpoint proxies; original source archive, JSON pointer, current fields, previous date, average balances, interest-bearing share and annualized proxy rate |
| bank_cost_bridge.csv | Screened same-certificate Q2 comparison; signed volume/mix/proxy-rate contributions and residual, coverage fields, size peers |
| unscreened_bridge.csv | All accepted target-date pairs before growth filter |
| quarterly_flags.csv | Source pointer and contract/YTD disagreement reasons |
| cohort_exclusions.csv | Latest certificate excluded from principal bridge and why |
| industry_totals.csv | Reported full-universe institution counts, total/domestic deposits and domestic quarterly expense |
| quarterly_history.csv | Accepted-quarter proxy history with changing coverage; not a fixed-panel trend |
| structural_break_sensitivity.csv | Effect of alternative balance-growth filters |
| review_queue.csv | Highest positive proxy-rate contribution banks; context for investigation |
| retention_scenarios.csv | Explicit hypothetical inputs and annual USD economics, separate from observed bank bridge |
| metrics.json | Source counts, coverage, principal aggregate bridge and broader-cohort sensitivity |
