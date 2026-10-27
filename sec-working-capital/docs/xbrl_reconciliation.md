# SEC XBRL reconciliation — October 27, 2026

All **150 model source inputs** checked against the SEC CompanyConcept API, through Firecrawl's SEC provider, filtered by the **same annual 10-K filing accession** and fiscal reporting period. Every normalized source value is USD millions, with original USD value, CIK, accession, XBRL taxonomy tag, period, and immutable SEC reference in [xbrl_audit.csv](../data/xbrl_audit.csv).

| Company | Fiscal end | Annual report accession |
|---|---|---|
| Apple | 2025-09-27 | 0000320193-25-000079 |
| Dell | 2026-01-30 | 0001571996-26-000008 |
| Microsoft | 2026-06-30 | 0001193125-26-323660 |

**Expanded coverage:** HP Inc FY2025 (CIK 0000047217, 10-K 0000047217-25-000071) and Cisco FY2026 (CIK 0000858877, 10-K 0000858877-26-000132). HP's capex concept is `PaymentsToAcquireProductiveAssets`, unlike the other firms. Prior-balance facts are from the same 10-K comparative balance sheet. New SEC provider values were checked for reporting dates, units, form and accession.\n\n**Corrected discrepancy:** Dell FY2026 `PaymentsToAcquirePropertyPlantAndEquipment` was USD **2,633m**, not 2,630m; revised FCF = USD **8,552m**. The other modeled figures agreed with their corresponding companyconcept facts.

**Method:** Revenues, costs, CFO and capex are full-fiscal-year flow values; AR, inventory and AP are point-in-time balance sheet figures at current and previous year end. DSO = average trade AR / revenue ×365; DIO = average inventory / cost ×365; DPO = average AP / cost ×365; CCC = DSO + DIO − DPO. CFO less *cash* capex excludes noncash asset purchases. All models fail if published inputs disagree with xbrl_audit.csv.

**Interpretation:** Selecting an SEC GAAP tag confirms its value, not comparability of issuer classifications. Apple may include non-trade/vendor receivables outside trade AR; AP financing terms and services mix vary. FY calendar differences and supplier programs preclude causal inference and make peer ranking only descriptive.


## Fifteen-company SEC XBRL benchmark — ten companies added October 27, 2026
The original five companies are joined by **Nvidia, AMD, Intel, Qualcomm, Texas Instruments, IBM, Amazon, Lam Research, KLA and Analog Devices**. All 100 newly added statement inputs are verified against same-annual-accession SEC CompanyConcept XBRL records, making **150 traceable facts**. LRCX, KLAC and ADI report some values with precision finer than USD one million; source values are kept at USD 1,000 precision, and verification compares whole USD rather than truncated million-dollar integers.

**Cohorts, not one league table:**
- Devices & systems: Apple, Dell, HP Inc.
- Semiconductors: Nvidia, AMD, Intel, Qualcomm, Texas Instruments, Analog Devices.
- Semiconductor equipment: Lam Research, KLA.
- Enterprise technology: Cisco, Microsoft, IBM.
- Platform & logistics: Amazon.

**Interpretation:** Cash conversion is capital-model-dependent: chip inventories and foundry cycles, cloud infrastructure cash spending, supplier financing and product-service revenue mix change what constitutes a good cash cycle. The dashboard compares within cohorts and plots capex intensity against FCF margin to make the cross-group differences visible. Amazon is shown as a single-constituent operational reference, not a peer median or policy target. Annual results are not seasonally adjusted and should not be treated as causal effects or direct attainable targets.

**Source and methodology:** [All 150 selected XBRL facts](../data/xbrl_audit.csv) include issuer, accession, element name, original USD amount and statement end date; cash capex maps to the issuer's reported US-GAAP capital spending concept, which varies by filing. The analysis file and independent SQLite benchmark both use average beginning/end balances and a constant 365-day convention.
