# Method, timing, contracts and dictionary

## Decision specification

Select up to ten investigations with at most two per destination airport. All slots have equal assumed investigation cost for prioritization; costs can be changed in the separate economics scenario. Candidates need six or more peer-comparable Jan–Aug 2024 months and at least 1,000 total reported flights. The 2024 score is the sum of signed carrier-delay excess minutes; negative-score sites are never added just to fill slots. Sort ties by carrier then airport. Greedy descending scores solve the uniform-slot partition-cap problem; an exhaustive small-instance oracle verifies it. This is not a general cost-constrained knapsack solver.

The baseline ranks raw carrier-delay minutes within the same discovery cohort, under identical constraints. No policy or candidate selection uses 2025 or 2026 data. The 2025 period is a validation checkpoint; the 2026 period is a final retrospective diagnostic. Both use January–August to reduce unequal-season exposure. September–December data are retained in the audited warehouse but do not enter the policy comparison. No hyperparameter search is performed.

All raw data are the October 19, 2026 snapshot, potentially including revisions. A chronological data split does not establish what was publicly available on an earlier decision date. Original publication vintages have not been reconstructed. Do not call this a prospective trading/operational backtest.

## Peer definition and estimand

For carrier i, airport a, month t, benchmark = sum(other carriers' carrier-delay minutes) / sum(other carriers' reported arrival flights). Require at least three other operating carriers and 1,000 other-carrier flights in that airport-month. Exclude the focal carrier from both sums. Peer excess = focal carrier minutes minus focal flights × peer benchmark. It is signed, measured in minutes, and not a causal effect.

Use the reported `arr_flights` denominator; it includes the flight-disposition categories retained in the export. Carrier minutes cover categorized delays of at least 15 minutes; this metric is carrier-categorized minutes per reported flight, not mean delay among completed flights. Cancellation and diversion rates are retained for a pilot's guardrails but no cancellation savings are imputed.

Capture = sum of positive site-level signed excess among the chosen sites / sum of positive site-level signed excess among observed members of the original eligible pool. Sum within a site over the period before applying max(0, excess). Missing sites do not become zero-performance observations; observed counts accompany the denominator. Diagnostic presence means at least one peer-eligible month, not eight complete months. The history and queue expose months of coverage for review.

## Acceptance and uncertainty

Publication requires reproducible arithmetic, independent source/SQL audits, functioning CLI scenarios and output review. Source-row contracts are separate from model/decision gates. Retrospective stability gate requires a positive lower bound on the exploratory difference interval and all selected sites observed; prospective deployment also needs operational comparability, flight-level controls, original vintages and pilot evidence, and therefore remains unmet.

The exploratory interval resamples circular blocks of two months, four blocks per draw, across the eight diagnostic months. It keeps all carrier-airport observations within the same sampled month together and repeats months with replacement. 2,000 draws, fixed seed. Eight months provide limited information about serial/seasonal dependence; the interval is neither a population sampling interval nor a full-year reliability guarantee. Its point estimate measures benchmark concentration, not the treatment effect of investigation.

## Data contracts and lineage

- Natural key: year × month × operating carrier × destination airport; duplicates fail the run.
- All 32 requested months must occur; source-file and decompressed-file hashes must match.
- Numeric blanks, nonfinite or negative measures are quarantined. Blank names remain text, never invented labels.
- Cause minutes must sum to total delayed minutes within 1 minute; fractional cause counts must sum to delayed-flight counts within 0.031 flights (five rounded categories).
- Delayed + cancelled + diverted flights cannot exceed reported flights. Zero exposure is excluded.
- A strict run excludes reconciliation failures. A permissive sensitivity retains numerically complete rows that fail only cause reconciliation; it never restores missing values.
- Every normalized row retains its original CSV physical data-row number (header is row 1). No newline-containing source fields were found; tests trace values by CSV record index.
- No flight-level double counting is tested because flights are not the input unit. The export has one operating-carrier/airport/month key; no separate marketing-network aggregates are concatenated.

## Source data dictionary

| Field | Meaning / unit |
|---|---|
| year, month | Reporting calendar month |
| carrier, carrier_name | Operating-carrier code and reported name; code is the key |
| airport, airport_name | Destination airport code and reported name |
| arr_flights | Reported arrival flight count, including dispositions |
| arr_del15 | Flights arriving at least 15 minutes late |
| carrier_ct, weather_ct, nas_ct, security_ct, late_aircraft_ct | Fractional counts allocated among causes by reported delay minutes; not integer event counts |
| arr_cancelled, arr_diverted | Flight-disposition counts |
| arr_delay | Total categorized arrival delay minutes |
| carrier_delay | Minutes in carrier category; narrow core outcome |
| weather_delay, nas_delay, security_delay, late_aircraft_delay | Other delay-minute categories, retained separately |

## Derived outputs

| File / column | Meaning |
|---|---|
| source_audited_peer_rows.csv.gz | Valid peer-comparable source rows with `source_row`, excluded-self peer carriers/flights/rate and signed `excess_minutes` |
| site_history.csv | Jan–Aug annual site aggregates, discovery membership and selection indicator |
| investigation_shortlist.csv | Fixed 2024 shortlist; actual 2026 coverage and signed excess; investigation status |
| policy_evaluation.csv | Policy-year coverage, positive-excess capture, signed excess and flights |
| sql_airport_totals.csv | Auditable valid-row airport/month SQL totals |
| quarantine.csv | Source location and reasons for exclusion; original values remain in raw ZIP |
| scenario_sensitivity.csv | Hypothetical price, recoverability and cost assumptions; modeled net and break-even fraction |
| metrics.json | Counts, exploratory interval, distinct retrospective/prospective gates and sensitivity results |

Scenario modeled net = max(0, signed excess) × assumed USD/minute × assumed recoverable fraction − site count × assumed site cost. This is a one-period thought experiment tied to the stated minutes, not an annualized benefit or measured saving. Recovery fraction has no empirical calibration. Some rows deliberately have negative net value.
