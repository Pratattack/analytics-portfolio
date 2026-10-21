# Methodology and assumptions

## Observation scope and information timing

The six purposively selected listed insurers are Travelers, W. R. Berkley, RLI, Hanover, Selective and Cincinnati Financial. This is not an industry census or random sample. Original 2025 annual filings supply net cumulative paid and incurred claims, by accident year and valuation year, at the exact disclosed line and segment dimensions. Amounts are USD; inline scale and sign are applied before analysis. Only an exact accident-year member is accepted; aggregated prior-year members are not relabeled as individual accident years.

The snapshot cutoff is October 20, 2026. The source annual reports were filed in February 2026. Historical columns are observations as disclosed in those filings and may contain revisions, reclassifications or unaudited supplemental information. Masking a historical diagonal does not reconstruct the information available to an analyst at that historical date. No real-time backtest or causal identification is claimed.

## Model gates

Every triangle is inventoried. A model requires consecutive accident years through 2025, all expected cumulative cells, at least five accident years, nonnegative cumulative paid amounts, and nondecreasing supported paid development. Cumulative decreases can arise from recoveries, reinsurance, currency or reporting changes; they are retained as reasons this model is unsuitable, not repaired into monotonic data. The separately disclosed Selective aggregate is not added to its component lines.

The comparable disclosed balance is cumulative incurred minus cumulative paid at valuation year 2025, summed only over the same accepted accident-year and line scopes. It is not the company's entire GAAP claims liability: older accident years and unallocated claim-adjustment expenses can be outside the table. Comparisons across lines still require understanding coverage, inflation, settlement and reinsurance differences.

## Development estimate

For cumulative paid claims `C[a,d]`, the volume-weighted age-to-age factor is `f[d] = sum(C[a,d+1]) / sum(C[a,d])` over supported pairs with positive denominators. Project each accident year's latest cumulative paid through the observed development factors. Multiply the resulting ultimate by an explicitly assumed tail factor. Modeled unpaid equals ultimate minus latest cumulative paid.

The default tail is 1.00, which assumes no additional development beyond the oldest disclosed age. That is a restrictive model convention, not an actuarial estimate. Sensitivities use tail factors 1.00, 1.05 and 1.10, plus median individual age-to-age factors. The workbench permits a tail up to 1.50. A tail increment acts on the projected **ultimate**, not only on the reserve; the independent hand test checks that distinction.

The oldest factor often has only one supporting pair. The method/tail envelope quantifies sensitivity; it is **not a confidence interval, VaR, Mack standard error or calibrated probability distribution**. Actual parameter and process uncertainty can be larger.

## Simple baseline and retrospective diagnostic

For cutoffs 2022, 2023 and 2024, refit using only disclosed cells at or before the cutoff. Eligibility is recalculated from that masked triangle; the 2025 eligibility decision does not filter historical model diagnostics. Predict one further valuation year's movement for existing accident years that still have a supported next development age. The oldest fully observed age and the as-yet-unobserved new accident year are outside that diagnostic.

The simple baseline repeats the last observed annual cumulative-paid increment; for an accident year's first observed year, that increment is its first cumulative amount. WAPE is the sum of absolute prediction errors divided by the sum of absolute observed cumulative movements, over identical matched rows. Source effects mean the target is reported cumulative movement, not a guaranteed pure cash-payment series.

The observed improvement is useful retrospective evidence but is insufficient for promotion: current-cohort selection, revised historical data, few valuation years, source exclusions and the unobserved tail remain. No causal conclusion or validated future accuracy is claimed.

## Decision workflow

The decision table ranks accepted lines by the absolute dollar increment from a 1.00 to 1.10 volume-method tail. This prioritizes the financial sensitivity of a diligence workstream; it is not a performance grade or an optimal capital allocation. A real committee must obtain claims-level triangles, actuarial selections, inflation/settlement explanations, reinsurance terms, statutory capital constraints and independent review before capital actions.
