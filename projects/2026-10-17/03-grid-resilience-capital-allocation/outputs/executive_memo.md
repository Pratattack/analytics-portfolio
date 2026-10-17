# Grid Resilience Capital Allocation

PUBLIC BENCHMARKS + HYPOTHETICAL INVESTMENTS | USD | 2026-10-17

## Investment recommendation

Reserve $7.72m of the $20.00m envelope and 5 of 14 crew units. Select 3 upgrades, including 2 critical-service districts. Finite-scenario worst social NPV is $0.83m. This is a conditional screening recommendation; stage-gate engineering validation before committing capital.

## Selected allocation

Texas — automation; North Carolina — automation; Michigan — hardening

## Why optimization matters

The solver checks all 59,049 allocations and finds 24,631 feasible plans. It maximizes the minimum social NPV across four explicit scenarios, subject to budget, crew capacity, one intervention per district and a two-critical-district floor. Equal-weight optimization and an independent dynamic-programming oracle agree to 0.0000000000m. Equal scenario weights are a comparison assumption, not estimated probabilities.

## Tradeoffs and outside-set risk

Worst social NPV: robust $0.83m; equal-weight policy $-8.54m; feasible greedy baseline $-8.54m. Outside-set joint stress gives $-6.32m without changing the chosen plan. Robustness is limited to the stated set; it is not protection against every future outcome. Under execution downside, the fixed plan breaks even at an assumed outage value of $10.92/customer-hour.

## Observed data vs modeled assumptions

Observed: EIA 2024/2023 IEEE-method state SAIDI and reporting coverage for ten purposively selected states. Assumed: ten fictional service districts, customers, critical-service flags, costs, intervention effectiveness, outage valuation, 10-year useful life, 7% discount rate and scenarios. State benchmarks are proxies, not feeder forecasts or utility-specific measurements. Texas and Louisiana coverage is below 80%; no coverage adjustment is applied. All-event minus no-major-event SAIDI is an analytical contrast, not an exact physical attribution to storms.

## Reporting-coverage sensitivity

Excluding Texas and Louisiana under an illustrative 80% reporting-coverage screen changes the selected set to [{'state': 'North Carolina', 'intervention': 'automation'}, {'state': 'South Carolina', 'intervention': 'automation'}, {'state': 'Michigan', 'intervention': 'hardening'}], with worst modeled social NPV $-0.43m and reserve $7.36m. The 80% screen is an analyst assumption, not an EIA quality standard. This checks recommendation sensitivity to data completeness rather than pretending the missing reporting can be repaired by scaling SAIDI.

## Value definition and accounting

Avoided customer-hours × assumed value/customer-hour = annual social benefit. Social NPV subtracts project capex and ongoing O&M; it is not utility profit, tariff revenue or a rate-case return. Capex is paid at time zero. Delay removes early operating years from a fixed ten-year evaluation horizon. The 20% budget reserve is capacity held, not an additional expenditure deducted from NPV. No terminal value, tax, financing, capital replacement or benefits outside outage duration are included.

## Decision gates and delivery plan

Gate 1: obtain feeder outage logs and customer segmentation; validate reporting completeness. Gate 2: engineering estimates and causal effectiveness evidence; quantify overlap and project dependencies. Gate 3: finance/regulatory review of valuation and cost recovery, permitting and resource schedule. Pilot a small package, then compare weather-adjusted interruption duration and realized costs against pre-registered baselines; do not attribute before/after changes to the upgrade alone.

## Personal understanding

I can explain why the highest individual return does not necessarily produce the best portfolio: projects compete for budget and delivery crews, while service commitments impose constraints. This model makes those tradeoffs explicit and chooses an allocation that remains strongest in its worst modeled scenario. I would present the assumptions beside the recommendation rather than call the result a guaranteed return.

## Interview defense

If asked why I did not build a machine-learning predictor, I would explain that two annual aggregate observations do not support a credible feeder-outage forecasting claim. The appropriate contribution here is transparent decision optimization, data lineage, counterfactual scenario testing, and independently checked calculations. The next useful data are feeder-level historical outages, treatment timing, asset condition and engineering cost estimates.

## Source and freshness

https://www.eia.gov/electricity/annual/html/epa_11_02.html | EIA Electric Power Annual Table 11.2 (2024/2023 snapshot), retrieved 2026-10-17. Pinned historical data, not a claim that 2024 is the latest available release. Original selected rows and a SHA-256 fingerprint are bundled. No proprietary data or employer endorsement.

