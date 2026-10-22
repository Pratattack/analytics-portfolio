# Inventory evidence dictionary

## Shared source and output definitions

- `data/raw/<TICKER>.json.gz`: lossless selected-tag projection of the SEC Company Facts response. All original entries, indices, accession, period, filing date and units for the specified tags are retained. `source_manifest.json` pins source URL, original full-response hash and the projected snapshot hashes. Unused concepts are omitted; original JSON pointers remain valid.
- `data/raw/<TICKER>-latest-inline.json.gz`: numerical USD facts parsed from the original latest qualifying filing. Each retains original inline context and element index. `filing_manifest.json` pins original HTML hash, source URL, filing accession/date/period and numeric-snapshot hash. The full narrative HTML is not redistributed. Parser in `audit_filings.py`; collector in `acquire_filings.py`.
- `data/raw/<TICKER>-submissions.json.gz`: original SEC filing-history metadata; hash is in the filing manifest.
- `outputs/panel.csv`: one admitted consolidated entity-period. USD, unscaled integers. Positive outflow columns are cash spent, not signed cash-flow statement totals. No segments or unconsolidated entities are added.
- `outputs/source_lineage.csv`: every selected numeric operand with source JSON pointer, accession, filing date, start/end, metric and arithmetic role. `annual_plus` less `ytd9_minus` reconstructs Q4; `direct` has weight one.
- `outputs/exclusions.csv`: proposed issuer-periods rejected for missing coherent facts or mismatched periods. Missing values are never replaced with zero. Explicitly reported zero buybacks remain zero.
- `outputs/later_revision_audit.csv`: selected operands that differ in a later available disclosure. The original current-period input is retained; the audit does not infer why a revision occurred.
- `outputs/original_filing_cells.csv`: all entity-wide USD inline facts from the nine latest qualifying source filings; `original_filing_reconciliation.csv` checks overlapping selected operands, not every historical fact against HTML.
- `outputs/sql_summary.csv`: checked entity-level accounting totals from `warehouse.sql`; sums of balances are reconciliation checks, not economic portfolio capital.
- All period labels are actual fiscal end dates. Filing dates gate information availability. The cutoff is October 20, 2026; latest date-only filings on October 21 are excluded.

## Industry fields

`inventory`: ending inventory net at cost; `cost`: standalone quarterly total cost; `revenue`: standalone quarterly sales. Annual forms require Q4 = annual less nine-month total, with the nine-month operand's matching fiscal start and filing no later than the annual filing. Average daily cost uses 91.25 days for a simple comparable **endpoint inventory days proxy**, not issuer-reported DIO or daily-average turnover.

`forecast_diagnostics.csv`: original inventory balances, candidate/last-value/seasonal forecasts, target and origin filing dates, training-label latest date/count, penalty-availability date, and prequential bounds. `seasonal` is inventory at the same quarter one fiscal year before the target. Calibration outcomes are separate from test outcomes.

`latest_decisions.csv`: latest admitted period and current-data gate per issuer. COHU's 2017 and LRCX's 2025 balances are explicitly stale, not current. Only four usable rows enter current diagnostics; there is no sum of mixed-vintage balances. `assumption_scenarios.csv` explores candidate-upper-band planning balances with clearly hypothetical buffer/carrying rates; it does not override failed promotion. The UI defaults to the last-balance baseline.
