# Data dictionary and provenance

## Original disclosures and pinned numerical snapshots

| File / field | Meaning |
|---|---|
| data/source_manifest.json |17 original filings: ticker,CIK,report_end,filed,accession,originalURL,fullHTMLSHA256,numericalsnapshotSHA256,gziparchiveSHA256,numeric-cell count |
| data/raw/*.json.gz | All numeric inline facts from that original filing; not a companyfacts summary or a new reporting vintage |
| tag,context,dimensions,unit | Exact XBRL qualified tag and context/dimensional scope, USD unit; different contexts not silently combined |
| start,end | Annual duration or instant date; null start denotes stock |
| value,decimals,scale | Normalized numeric value, declared rounding precision and power-of-ten display scale |
| element_index | DOM traversal index in original HTML, enabling exact-source recollection checks |
| data/ledger_sources.json | Relevant original disclosure numeric cells; display_value and display_negative preserve original table's economic movement sign separately from normalized value |

Original HTML URLs/hashes permit source reconstruction, but complete copyrighted issuer narratives are not republished. Only numerical facts and source metadata are retained. `../energy-mortgage-toolkit/source_audit.json` records executed full-original comparisons. A fresh source response is not required or claimed by offline CI. Source data are public SEC issuer disclosures; extracted financial facts are attributed, and no blanket license for issuer narrative or SEC-site third-party content is asserted.

## Observations and source lineage

| Output / field | Units / interpretation |
|---|---|
| panel.csv | One retained ticker/year, latest selected filed version;35 rows, irregular sampled history |
| opening,closing | USD consolidated book retirement-liability stocks, not cash balances |
| accretion | USD displayed annual discount-unwind movement from same ARO table |
| revisions | USD displayed changes in estimates; signed; not a cash payment |
| explicit_cash_paid | USD, only explicit CashPaidToSettle tag; null if not separately identified; not zero |
| removed_liability | USD magnitude of LiabilitiesSettled tag, may include divestitures; never harmonized as cash |
| ledger_residual,rounding_tolerance | USD opening+all annual movements−closing; sum of declared half-rounding intervals plus0.01 |
| filed,accession | Information timing and immutable original filing identity |
| source_lineage.csv | Every retained operand: opening/closing/flow role, sourcefile,URL,accession,DOMindex,context,tag,normalized and presentation values,dates |
| exclusions.csv | Incomplete/unreconciled candidate periods; header-only means none failed, not that no selection restrictions apply |
| latest.csv | One latest 2025 empirical book ledger per issuer |
| sql_history.csv | Counts and sums for observed panel years; not a complete annual cash history |

## Modeled assumptions and outputs

| Output / field | Units / interpretation |
|---|---|
| timing_bounds.csv |216 issuer/scenario combinations; preserves 18 infeasible assumption rows |
| discount_rate_assumed | Annual nominal fraction, assumed common rate; not an observed issuer discount curve |
| pv_weighted_mean_year_assumed | Years1..30; assumed mean weighted by PV shares, not cash shares |
| first5_pv_share_cap_assumed | Fraction0..1, upper bound on first-five-yearPV share; not a nominalcash budget |
| book_pv | Fixed observed closing bookUSDstock used in conditional model |
| lower_cash_equivalent,upper_cash_equivalent | USD, min/max sum of hypothetical nominal retirementcash under constraints; null for infeasible assumptions |
| status | feasible or infeasible assumptions; not issuer solvency label |
| scenario_key | Ticker/rate/mean/cap join identity |
| extremal_profiles.csv | Scenario/bound/year,positivePV share; boundary distributions attaining reported bounds |
| metrics.json | Measured source/panel/scenario counts, aggregatebookPV,false adoption gate and interpretation |
| chart.svg,report.html,app.html | Observed book chart, executive report, offline scenario workbench |

All source financial facts are empirical observations as of specified reporting/filing dates. Discount rates, PV-share caps, mean dates and the 30-year horizon are assumptions. Cash-equivalent intervals and profiles are modeled outputs; they are neither reported cash forecasts nor GAAP remeasurements. No synthetic operational observations are inserted.

Published derived CSV/JSON floating values use12 significant digits for cross-platform reproducibility; pinned source snapshots retain their original values. This formatting precision is not a claim of economic accuracy.
