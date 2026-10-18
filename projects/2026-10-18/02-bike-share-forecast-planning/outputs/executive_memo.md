# Mobility Demand Forecasting & Capacity Economics

PUBLIC HISTORICAL DATA · CHRONOLOGICAL EVALUATION · HYPOTHETICAL COSTS

## Decision

Validation selects ridge_1; test WAPE 13.4%, compared with 18.7% for a seven-day seasonal baseline. Evaluate the operational cost result alongside forecast error; the model was selected before examining July–December test performance.

## Capacity economics

Using hypothetical costs of $4 per shortfall trip-equivalent and $0.75 per excess trip-equivalent, fixed validation-calibrated capacity policies imply $145,115 total cost reduction versus the baseline over 184 historical test days. The seven-day block bootstrap interval for mean daily saving is [$540.09, $1143.73]. This is a counterfactual proxy calculation, not realized operating savings.

## Leakage controls

Daily casual and registered counts sum to the target, so neither is a predictor. Observed same-day weather is also excluded because it is unavailable at the prior-day planning cutoff. Features use known calendar information and lagged rentals only. Models refit on the first forecast day of each month using strictly earlier targets. Subsequent daily predictions may use newly observed prior-day rentals, as in a prequential one-day-ahead process; no random train/test split is used.

## Uncertainty and drift

Absolute validation residuals calibrate a nominal 90% band. Actual test coverage is 87.5%. Temporal drift invalidates exchangeability guarantees; this is empirical calibration, not guaranteed 90% future coverage. Review monthly WAPE, bias and coverage. Bootstrap intervals are approximate historical uncertainty conditional on model, data and invented costs.

## What the capacity units mean

Capacity is daily trip-equivalent service capacity, not a bicycle count. Bikes can serve multiple trips, and the dataset has no station-level rebalancing, availability or true lost-demand observations. Historical realized rentals are the target and a limited proxy for latent demand; stockouts and unmet requests are not observed. A practical fleet-sizing decision needs trip duration, turnaround, station inventory and censored-demand estimation.

## Data provenance

731 public daily Capital Bikeshare observations from 2011–2012, UCI Bike Sharing dataset. Retrieved from a public GitHub mirror, line endings normalized to LF, pinned with SHA-256. This historical benchmark is not current Washington ridership and does not demonstrate current commercial performance. Original dataset: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset | Fanaee-T (2013), DOI 10.24432/C5W894, CC BY 4.0. Mirror URL and exact fingerprint are in data/provenance.json.

## Personal understanding

I can explain why a low forecast error does not automatically produce the best capacity decision: underestimating demand and paying for unused capacity have different costs. I would choose a model using a chronological validation period, turn its residuals into an explicit service-capacity rule, and judge the untouched test period on both accuracy and cost. I would also show where uncertainty bands fail instead of treating them as a guarantee.

## Implementation gates

Use current operator data, validate information availability at the cutoff, model forecast-weather uncertainty if added, infer censored demand, and incorporate station-level inventory, maintenance and rebalancing. Pilot daily capacity recommendations with cost, trip fulfillment and distributional guardrails. Refit cadence and retraining triggers must be set before live evaluation.

