# Forecast timing, decision economics and data dictionary

## Decision design

A hypothetical operator sets next-day trip-equivalent service capacity. The target is observed daily rentals. Candidates are a seven-day seasonal-naive forecast, a four-week same-weekday mean, and standardized ridge models with penalties 1, 10 and 100. Lowest validation WAPE determines the winner; test results do not change model choice or capacity calibration.

## Chronological windows

| Window | Purpose |
|---|---|
| 2011 | Initial history; first 28 days unavailable as training targets because lags are required |
| 2012-01-01 to 2012-06-30, 182 days | Validation forecasts, model selection and residual calibration |
| 2012-07-01 to 2012-12-31, 184 days | Final prequential test evaluation |

Ridge models refit on the first forecast day of each month using all targets strictly before that date. The information set then grows daily through newly observed lagged rentals. This is a prequential one-day-ahead process, not a fixed-origin six-month-ahead forecast and not an untouched static model. Test observations may enter later lag features and later prespecified refits after they occur; they do not enter earlier predictions or hyperparameter selection.

## Features and leakage controls

Predictors comprise intercept, elapsed-year trend, annual sine/cosine, known holiday, six weekday indicators, lag-1, lag-7, trailing-seven-day mean and trailing-28-day mean. Standardization parameters are calculated within the fit's training window; the intercept is not penalized. Predictions are clipped at zero.

`casual` and `registered` are excluded because they add exactly to `cnt`. Same-day observed weather is excluded because it is unavailable at the prior-day decision cutoff. A real weather-enabled model would need archived as-issued forecasts, not realized future weather. Calendar encodings are derived from date; the source `season` coding is retained but not reinterpreted or used.

## Uncertainty and capacity rule

For each model, validation residuals are actual minus forecast. A nominal 90% symmetric band uses an absolute-residual order statistic at ceil((n+1)×0.9), with its lower endpoint truncated at zero. Time dependence and drift mean this rank adjustment does not establish distribution-free future coverage. The report evaluates actual coverage month by month.

Assumed underage cost is $4 per trip-equivalent and overage cost $0.75. The critical ratio is 4/(4+0.75), approximately 0.8421. Capacity is max(forecast plus the validation signed-residual quantile at this ratio, 0). Daily modeled cost is max(actual minus capacity,0)×4 + max(capacity minus actual,0)×0.75. Each baseline is calibrated using its own validation residuals, providing a more credible comparator than an unbuffered baseline.

All test capacities use fixed validation calibration. Validation rows in the exported scored file also show the final calibration **retrospectively** for diagnostics; those validation capacity costs and bands are not claimed as prospective results and do not drive model choice. The final test-period policy remains out of sample with respect to selection and calibration.

## Statistical comparison

A seven-day moving-block-style resampling of consecutive, non-overlapping historical test blocks produces 400 bootstrap draws of average paired cost savings. Blocks are sampled with replacement until the original test length is reached, and the last sample is truncated. The percentile interval is approximate and conditional on this historical series, model choices and cost assumptions. With only 184 test days, it does not quantify all future regime risk.

## Input and output dictionary

| Field | Meaning/use |
|---|---|
| dteday | Source daily date, 2011-01-01 through 2012-12-31 |
| cnt | Observed total rentals, the prediction target |
| casual / registered | Source target components; retained for validation, prohibited as predictors |
| instant | Source record identifier, unused in modeling |
| holiday | Known calendar flag; used as a feature |
| yr / mnth / weekday / workingday / season | Original source calendar fields; date-derived encodings replace most of them |
| weathersit / temp / atemp / hum / windspeed | Source observed weather; deliberately unused |
| index | Zero-based daily position in the pinned CSV |
| train_end_index | Last target permitted in the fitted model, strictly before prediction index |
| latest_target_lag_index | Most recent target observation available for lagged features |
| error | Actual minus prediction; positive means underprediction |
| lower_bound / upper_bound | Validation-calibrated nominal interval |
| capacity | Hypothetical trip-equivalent service capacity/day |
| shortfall / excess | Realized-count proxy differences versus hypothetical capacity |
| decision_cost | Assumed asymmetric operating loss, in USD |

## Source provenance and validation

The pinned mirror contains 731 unique consecutive dates. Checks establish cnt = casual + registered, nonnegative counts, exact source-file SHA-256, training cutoffs, feature isolation, chronological partitions, validation-only selection and independent SQL/accounting totals. The mirror is not independently byte-compared with the original UCI ZIP; that limitation is recorded. Dataset attribution and CC BY 4.0 terms are in `data/provenance.json` and README.

## Limits and implementation gates

Recorded rentals may be censored by historical availability. The data do not reveal true lost demand, station stocks, maintenance outages, trip length, bike turnaround or redistribution. Do not translate daily rentals directly into physical bike requirements. Cost estimates and capacity policies are invented. Daily aggregation, old data, missing archived weather forecasts and a short evaluation window limit generalization.

Actual adoption requires current operator data, verified data-availability cutoffs, station-level availability and censored-demand estimation, fleet/crew constraints, prospective forecast monitoring, pilot measurements and predeclared retraining triggers. The current deliverable is a reproducible analytical case and decision report, not a production service.
