# Data dictionary and lineage

| File / field | Definition and unit |
|---|---|
| `data/source_manifest.json` | Issuer CIK, companyfacts URL, original 2025 filing URL, accession, filing date and HTML SHA-256 |
| `data/pinned_archives.json` | Exact gzip and decompressed JSON fingerprints; source identity and original-document hash |
| `data/raw/*-2025-inline.json.gz` | Numeric inline-XBRL observations with original `source_id`, `context_id`, issuer identifier, dimensions, dates, scale, sign, unit measure, displayed numeric text and decoded value |
| `triangle_cells.csv: group_id` | Issuer plus stable hash of all non-accident-year dimensions; distinct scopes are never merged by label |
| `accident_year` | Year of the insured accident/cohort in the exact XBRL accident-year member |
| `valuation_year` | December 31 cumulative-report valuation date |
| `metric=paid` | Net cumulative paid claims and allocated claim-adjustment expense, USD; not an annual increment |
| `metric=incurred` | Net cumulative incurred claims and allocated claim-adjustment expense, USD; includes estimates |
| `source_lineage.csv: pointer` | JSON pointer to the frozen numeric observation, linked to the original filing element ID and context |
| `triangle_inventory.csv: eligible` | Whether this particular paid-development model's gates pass; not a source-quality or insurer-safety score |
| `reported_unpaid` | 2025 incurred minus paid over identical accepted accident-year/line scopes, USD |
| `chain_ladder_unpaid` | Volume-factor modeled ultimate minus latest paid, default tail 1.00, USD |
| `gap` | Modeled less disclosed comparable unpaid, USD; negative is not authorization to release reserves |
| `tail_10pct_increment` | Change in modeled unpaid when the ultimate tail factor rises from 1.00 to 1.10, USD |
| `development_factors.csv: support` | Number of observed positive-denominator pairs supporting that age's factor |
| `masked_diagonal_diagnostic.csv` | Cutoff, target valuation year, actual reported movement, both predictions and absolute errors, USD |
| `model_tail_sensitivity.csv` | Separate modeled outcomes for method and assumed-tail choices; no probabilities |
| `sql_current_balances.csv` | Independent SQL join of paid/incurred cells by exact scope, year and metric |

Blanks and undisclosed cells remain absent. They are never changed to zero. A displayed dash is decoded as zero only where the numeric inline fact itself uses that zero representation; an explicit XBRL nil is rejected. All retained monetary observations must declare USD.

The included numerical facts and corporate filing metadata are public source data with original attribution. Issuer narrative HTML is not redistributed. The MIT license covers original project code and authored analysis, not third-party rights or endorsement.
