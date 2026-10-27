# SEC XBRL reconciliation — October 27, 2026

All **50 model source inputs** checked against the SEC CompanyConcept API, through Firecrawl's SEC provider, filtered by the **same annual 10-K filing accession** and fiscal reporting period. Every normalized source value is USD millions, with original USD value, CIK, accession, XBRL taxonomy tag, period, and immutable SEC reference in [xbrl_audit.csv](../data/xbrl_audit.csv).

| Company | Fiscal end | Annual report accession |
|---|---|---|
| Apple | 2025-09-27 | 0000320193-25-000079 |
| Dell | 2026-01-30 | 0001571996-26-000008 |
| Microsoft | 2026-06-30 | 0001193125-26-323660 |

**Expanded coverage:** HP Inc FY2025 (CIK 0000047217, 10-K 0000047217-25-000071) and Cisco FY2026 (CIK 0000858877, 10-K 0000858877-26-000132). HP's capex concept is `PaymentsToAcquireProductiveAssets`, unlike the other firms. Prior-balance facts are from the same 10-K comparative balance sheet. New SEC provider values were checked for reporting dates, units, form and accession.\n\n**Corrected discrepancy:** Dell FY2026 `PaymentsToAcquirePropertyPlantAndEquipment` was USD **2,633m**, not 2,630m; revised FCF = USD **8,552m**. The other modeled figures agreed with their corresponding companyconcept facts.

**Method:** Revenues, costs, CFO and capex are full-fiscal-year flow values; AR, inventory and AP are point-in-time balance sheet figures at current and previous year end. DSO = average trade AR / revenue ×365; DIO = average inventory / cost ×365; DPO = average AP / cost ×365; CCC = DSO + DIO − DPO. CFO less *cash* capex excludes noncash asset purchases. All models fail if published inputs disagree with xbrl_audit.csv.

**Interpretation:** Selecting an SEC GAAP tag confirms its value, not comparability of issuer classifications. Apple may include non-trade/vendor receivables outside trade AR; AP financing terms and services mix vary. FY calendar differences and supplier programs preclude causal inference and make peer ranking only descriptive.
