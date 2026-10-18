# Evidence design, data contracts and decision limits

## Question and stakeholders

A consulting or utility strategy analyst needs to identify which reported reliability outcomes deserve deeper diligence, determine whether a predictive benchmark adds evidence, and calculate how an explicitly assumed improvement could bound an investment's social value. The audience includes finance, operations and engineering; none has supplied proprietary project evidence here.

The deliverable supports **review and assumption testing**, not outage-cause attribution, engineering design, management-performance grading or capital approval.

## Data contract

Each record is one **report year × utility number × state × reporting standard**. The source workbook's `Reliability_States` sheet contains separate IEEE and Other blocks. Both are retained as long-form records, including empty method blocks. A missing block can mean the method does not apply; it is not automatically survey nonresponse.

Headers move from source row 2 in older files to row 3 in newer ones. ETL locates the `Data Year` header and asserts the inspected utility/ownership fields, IEEE/Other block labels and customer columns. Numeric fields accept explicit missing markers, retain zero and reject negatives, non-finite numbers and unrecognized text. Duplicate primary keys fail extraction. U.S. territories are outside this workbench's scope because their separate sheet is not normalized.

Every record retains workbook, sheet and original Excel row. All six official workbooks are bundled and hash-checked, so the panel can be rebuilt offline without trusting a third-party CSV mirror. `source_manifest.json` also records the full source ZIP URLs/hashes; raw ZIPs are acquisition intermediates rather than versioned duplicates.

## Dictionary

| Field | Meaning |
|---|---|
| year | Source report year, not publication date |
| utility_id | EIA utility number; multi-state utilities retain the same identifier |
| utility_name / state / ownership | Source organizational characteristics |
| standard | IEEE or Other; never pooled for comparison |
| saidi_all / saidi_normal | All-event and no-major-event interruption-duration indices, minutes/customer/year |
| saifi_all / saifi_normal | Corresponding interruption-frequency indices |
| customers | Customer count in the applicable reporting-method block |
| automatic | Source indicator for automatic outage recording |
| source_file / source_sheet / source_row | Exact normalized-record lineage |

SAIDI is an index, not a count of distinct outage events. Multiplying it by its reported customer denominator yields customer-minutes, not a causal storm-loss decomposition. Reported customers are not necessarily unique people or establishments. No customer-level personal data are present.

## Source-component reconciliation and quarantine

For each available official state-summary row, recompute all-event IEEE SAIDI as sum(customer count × utility SAIDI) / sum(eligible customer counts), using records with positive customers and nonmissing all-event SAIDI. Compare with the workbook's published state summary. The fixed 0.11-minute tolerance allows more than the half-step implied by one-decimal rounding; it is a project acceptance rule, not an EIA standard.

All 102 comparisons across 2023 and 2024 pass. Twenty-six of the 51 comparisons in 2025 fail. The code retains the differences, marks that release quarantined and selects the latest release with available state summaries and no exceptions: **2024**. It does not change source values, assume the summary or microdata is correct, or assert a root cause. Earlier years without comparable state-summary sheets remain historical inputs, not independently state-reconciled releases.

This gate establishes consistency under the specified aggregation, not complete validation of EIA survey responses. Some legitimate scope or revision difference may explain the exceptions; that possibility has not been established. Contacting the source provider or resolving revision history is outside the completed work.

## Descriptive peer cohorts

The operational review uses only IEEE records with nonmissing normal-day SAIDI and positive customers in the accepted decision year. Every row of the focal utility is excluded from its peers, including other states of the same utility.

Peer fallback order is state plus ownership, ownership plus customer-size band, ownership, then national. The first group containing at least 15 other observations is used; national is the final fallback. Size bands are under 10k, 10k–100k, 100k–1m and 1m+. These are analyst choices. A large peer percentile means the utility-state's reported duration is greater than many members of that descriptive cohort. It does not account for hazards, density, geography, equipment mix, outage definitions or regulatory duties.

Review flags identify customer-count changes over 25%, gaps in valid IEEE history, reporting-method transitions, no prior history and normal-day values exceeding all-event values. Flags request investigation; the latter is not automatically labeled a source error. Customer counts are not adjusted or imputed.

## Next-report benchmark diagnostic

2020–2022 provide initial history; **2023** selects among last report, trailing-three-report log median, and peer-shrinkage weights of 25%, 50% and 75%. The metric is mean absolute error weighted by **previous-report customer counts**, available before the target report year. Candidate models share the same matched target cohort and require a valid prior-year IEEE record. Recent medians use available valid observations within three preceding years; sparse-history counts are exported.

**2024** calibrates a symmetric absolute-log-residual band using a nominal 90% rank adjustment. **2025** is held out for diagnostic evaluation. Peer values, historical targets and prediction weights are strictly from earlier report years; current customer counts are retained for descriptive inspection but do not determine fitting or selection. Changing every target-year outcome leaves predictions unchanged, as tested.

The apparent weighted-MAE advantage is tested with 600 bootstrap resamples of entire EIA utility clusters. All states of a utility move together. The error-difference interval crosses zero. A complete six-year IEEE cohort provides an attrition sensitivity comparison; it does not eliminate survivorship or unobserved reporting bias.

The promotion gate requires a strictly positive lower error-reduction bound, at least nominal empirical interval coverage, and a nonquarantined test release. It fails. No forecast is supplied as a promoted operating recommendation.

**Publication-date caveat:** final revised files were downloaded in 2026, and original historical release vintages were not reconstructed. EIA's annual release timing means a report-year split is not a January-1 forecast experiment. The project explicitly avoids claiming a historical real-time information set. Temporal dependence, peer clustering and revisions also limit nominal interval interpretation.

## Conditional investment economics

For a user-selected utility from the accepted view:

1. Observed normal-day SAIDI × observed reported customers × assumed reduction / 60 gives an avoided customer-hour proxy/year.
2. Multiply by assumed USD/customer-hour and subtract assumed annual added O&M.
3. Discount that constant annual net social value across the chosen finite horizon.
4. The resulting present value is a **conditional break-even up-front cost**. Subtract proposed capex to show a conditional surplus/deficit.

The calculator neither estimates intervention effectiveness nor values utility cash profits. It excludes outage-duration heterogeneity, willingness-to-pay differences, capex timing, benefit ramp, taxes, financing, degradation, cost recovery and engineering interactions. Defaults are openly hypothetical. The Texas scenario CSV is an assumption grid, not an investment shortlist.

## Architecture and verification

`acquire.py` retrieves official releases. `etl.py` enforces the data contract and lineage. `analysis.py` builds the warehouse, peer review, diagnostics and gate status. `warehouse.sql` exposes audited weighted aggregation. `app.py` provides a local read-only interface. `export_workbench.py` embeds the same resources in a standalone offline HTML. `report.py` produces figures and the decision memo.

Sixteen tests cover missing values, numeric validation, hand-calculated scenario values, peer exclusion/fallback, target leakage, release quarantine, filtering, API errors, HTTP headers and unlisted paths. Independent checks re-read all source cells, reconstruct SQL aggregates and weighted errors, and delete/rebuild all derived artifacts for exact within-environment hash equality. Figures were visually inspected. Full local-HTML browser testing was blocked by this environment's URL policy; it is not claimed. API/HTTP tests run in-process with a temporary local server.

Reproducibility does not establish causal validity or source-provider correctness. A passing code test is separate from a failing data-release or predictive-promotion gate.
