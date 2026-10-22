# Data dictionary and lineage

| File/field | Meaning |
|---|---|
| data/source_manifest.json | Ticker, CIK, original URL/accession/filed/report date, original HTML hash, numerical snapshot and archive hashes, original sizes and cell counts. |
| data/raw/*.json.gz | All parseable original inline numerical cells, retaining tag, context, dimensions, dates, unit, decimals, scale and document element index; not the complete narrative filing. |
| outputs/panel.csv | Chosen source observations. Amounts are USD, not millions; missing optional values are blank. |
| ticker, end, filed, accession | Entity, actual period/observation end, disclosure date and original filing identity. |
| outputs/source_lineage.csv | Record, metric/derived component, exact source file/URL, source node index, context, dimensions, value and source disclosure date. |
| outputs/rounded_duplicates.csv | Highest-precision source selection when declared rounding intervals overlap. Other same-scope conflicts stop the pipeline. |
| outputs/disclosure_revisions.csv | Different values for a historical observation between available originals; an empty table means none detected within the selected mappings, not no revisions anywhere. |
| outputs/exclusions.csv | Incomplete comparable source pairs/metrics. This is not evidence that a filing is wrong. |
| data/original_html_audit.json | Recorded independent Decimal/sign/scale audit of selected actual original HTML nodes. Recollect originals explicitly to repeat it. |
| outputs/latest_decisions.csv | Latest empirical inputs plus explicitly conditional scenario outputs. |
| outputs/sql_summary.csv | Meaningful grouped source totals; historical sums are not current exposure, and overlapping period types are separated. |

| Additional field | Meaning |
|---|---|
| scope | VIE/other, committed/uncommitted, or overlapping total. |
| deposits | PHM deposits plus pre-acquisition cost; MTH/KBH cash deposits. |
| disclosed_price, price_basis | Source remaining or aggregate purchase price. |
| remaining_price | PHM reported remaining price; MTH/KBH aggregate less credited cash deposit. No deposit is deducted twice. |
| additional_preacquisition | Separately disclosed KBH pre-acquisition cost, not credited against price. Missing outside that scope. |
| disclosed_at_risk_cost | Disclosed deposit basis plus separately available pre-acquisition cost; heterogeneous basis, not guaranteed maximum loss. |
| outputs/scope_reconciliation.csv | 48 exact component-to-total dollar identities. |
| outputs/conditional_option_grid.csv | 243 hypothetical aggregate state/extension comparisons with the immediate baseline. |
| outputs/refund_sensitivity.csv | 27 refund/value challenges; refundability is assumed, never inferred from legacy tags. |
