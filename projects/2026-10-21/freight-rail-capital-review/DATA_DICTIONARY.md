# Rail capital evidence dictionary

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

`cfo`: consolidated annual net operating cash; `capex`: GAAP PaymentsToAcquirePropertyPlantAndEquipment (cash), not issuer-adjusted capital-investment guidance or maintenance-only capex. `dividends` and `buybacks`: explicitly reported common shareholder cash payments. PaymentsOfDividends is a fallback total cash-dividend tag; selected source tags are visible. No absent buyback fact is inferred to be zero.

`op_income`: GAAP operating income, including disclosed gains/charges; it is not normalized EBIT. `ppe_net`/`ppe_gross`: reported net/gross productive assets. The `_basis` fields identify the finance-lease-inclusive series introduced by UNP. Return comparisons require the same basis across adjacent annual ends; the transition pair is blank.

`buyback_capacity`: max(0, CFO − assumed capex − observed dividends), before other cash uses. `distribution_gap`: CFO − capex − dividends − buybacks; a residual, not a deficit forecast or identification of financing sources. `cash_return_coverage`: (CFO − capex)/(dividends + buybacks).

`net_asset_return21`/`gross_asset_return21`: operating income × (1−21% assumed tax) / average same-basis productive assets. Neither is corporate ROIC, replacement-cost return or incremental project IRR. `cfo_shock_to_zero_gap_pct`: change in CFO required for zero residual, holding other flows fixed; positive means an increase is needed. `asset_sensitivities.csv` varies tax (21/25/30%), asset basis and assumed hurdle (6/8/10/12%); these hurdles are not estimated WACC. `cash_scenarios.csv` varies CFO change and capex scaling; these grid cells have no assigned probability. `rolling_coverage.csv` sums three consecutive annual observations and omits gaps.
