# Methods and data dictionary

## Economic question and decision

Does adding credit spreads improve twelve-month recession classification over a Treasury-curve model and an expanding unconditional probability? The decision owner is a credit-research model-governance committee. The measurable objective is lower held-out Brier loss, with an uncertainty check, adequate event coverage and no retrospective tuning of the test outcomes. No trading P&L, recession timing causality or live forecast is claimed.

## Official sources and timing

- [BAA10YM](https://fred.stlouisfed.org/series/BAA10YM): monthly Moody's seasoned Baa yield less ten-year Treasury yield, percentage points. This is not an option-adjusted spread or a matched-duration default premium.
- [GS10](https://fred.stlouisfed.org/series/GS10): ten-year Treasury constant maturity, percent.
- [TB3MS](https://fred.stlouisfed.org/series/TB3MS): three-month Treasury bill secondary market rate, discount basis, percent. Comparing its convention with a ten-year constant-maturity yield is a conventional slope proxy, not an exact arbitrage spread.
- [USREC](https://fred.stlouisfed.org/series/USREC): NBER-based monthly recession indicator, 0/1. Turning points are dated retrospectively, with announcement delays.

`data/original_response.csv` preserves the full as-served response and its hash. `monthly.csv` retains 1960–2024 without interpolation. The endpoint may return wider history than requested; local date filtering is explicit and independently tested. The analysis panel contains origins 1970–2023. Twelve future labels require observations through December 2024; 2024 origins are censored. No current 2026 risk estimate is produced.

All features use month t−1. The credit change is BAA10YM(t−1) minus BAA10YM(t−4). Target y(t) is one if any USREC(t+1), …, USREC(t+12) is one. It predicts occurrence within the window, not necessarily recession onset; consecutive positive months are overlapping outcomes.

**Vintage limit:** the downloaded history is revised, not ALFRED vintages. Even when a training target's economic period has elapsed, its eventual NBER label may not have been announced. The twelve-month label gap prevents direct forward-period leakage, but cannot establish real-time information availability. This is retrospective model research.

## Estimation and frozen comparison design

At every origin, training starts in 1970 and includes only origins whose full target windows end by the current origin. Each fit standardizes features using only its training sample. Logistic coefficients minimize summed Bernoulli negative log likelihood plus λ/2 times squared non-intercept coefficients. The intercept is unpenalized. The optimizer supplies an analytical gradient, checked against finite differences.

The curve model uses GS10−TB3MS. The candidate adds BAA10YM and its trailing three-month change. Each independently chooses λ from 0.1, 1, 10 using expanding-origin Brier loss during 2000–2006. Those target windows finish by December 2007; test origins begin January 2008. Selected specifications stay fixed, while coefficients update using matured historical labels. An expanding training-label mean supplies a simpler probability baseline.

Review thresholds are selected only from 2000–2006 candidate predictions for assumed missed-alert costs 1, 3, 5 and 10 relative to false-alert cost 1. The primary dashboard begins with the 5:1 scenario. The curve and unconditional models are shown at the same threshold for comparability; thresholds were not separately optimized for them. Brier/AUROC do not depend on a threshold.

## Validation, dependence and adoption

Holdout origins cover 2008–2023: 192 months and 30 positive targets in only two contiguous positive runs. Brier, log loss, AUROC and confusion counts are reported; ranking ability is not probability calibration. A 2,000-replicate circular block bootstrap of paired monthly Brier differences uses blocks of 12/24/36 months. These are descriptive resampling bands, not a remedy for two crises or regime shifts. The pandemic-origin exclusion and two subperiods are challenge analyses, not independent replications or tuning targets.

The coded research promotion rule requires upper block bands below zero against both baselines and at least three positive target runs. This internal decision rule is not an externally preregistered study. The current model fails it. A real-time vintage and announcement-delay replay, additional event evidence and stakeholder validation are also required before use.

## Output definitions

`panel.csv`: origin, feature month, target end, curve, spread, spread change, target.
`test_predictions.csv`: candidate/curve/unconditional probabilities, training count, last training origin and label end.
`tuning.csv`: calibration-period penalty comparisons; `thresholds.csv`: assumed cost thresholds.
`sensitivity.csv`: paired Brier differences and block/subperiod challenges; `sql_annual_scores.csv`: independently grouped yearly loss.

Source observations remain the property of their providers. FRED links and original response are retained for attribution and audit; the project does not relicense provider data.
