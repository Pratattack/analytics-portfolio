# CFO Advisory Memo — Working Capital and Liquidity
**Date:** October 27, 2026 | **Decision owner:** Apple CFO, Treasury and Procurement

## Recommendation
Authorize a tightly controlled **90-day diagnostic and limited pilot**, not an enterprise-wide extension of supplier payment terms. Improve collections processes for low-dispute customers, test inventory efficiency where stockout risk is immaterial, and review negotiated supplier terms net of any forfeited discounts and supplier financing cost. Require a positive risk-adjusted multi-year NPV before expansion.

## SEC-XBRL benchmark
| Metric (USD m except days) | Apple FY2025 | Dell FY2026 | Microsoft FY2026 |
|---|---:|---:|---:|
| Revenue | 416,161 | 113,538 | 331,839 |
| Cost of sales | 220,960 | 90,831 | 106,374 |
| Operating cash flow | 111,482 | 11,185 | 182,935 |
| Cash capex | 12,715 | **2,633** | 115,948 |
| FCF | 98,767 | **8,552** | 66,987 |
| DSO (days) | 32.09 | 44.82 | 82.92 |
| DIO (days) | 10.74 | 34.46 | 4.01 |
| DPO (days) | 114.66 | 109.43 | 120.34 |
| CCC (days) | -71.82 | -30.14 | -33.40 |

See [SEC audit ledger](../data/xbrl_audit.csv); the initial **30 inputs** were checked against relevant annual 10-K accession-linked XBRL facts. Fiscal year ends and operating economics are unlike one another. **Peer CCC differences are not attainable targets**, especially for a company already exhibiting substantial negative CCC.

## Scenario and sensitivity
Working-capital cash-release estimate: realization × [(revenue/365 × days of DSO reduced) + (COGS/365 × days of DIO reduced + days of DPO extended)].
This is a **one-time potential cash balance release, not annual earnings**.

| Scenario | DSO reduction | DIO reduction | DPO extension | Realization | Gross cash release | One-time implementation | Net year-one liquidity | Annual financing rate | Year-one benefit less cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Conservative | 1 | 0.5 | 0.5 | 50% | $873m | $150m | $723m | 4% | -$115m |
| Base | 2 | 1 | 1 | 70% | $2,444m | $350m | $2,094m | 5% | -$228m |
| Stretch | 3 | 2 | 2 | 80% | $4,674m | $800m | $3,874m | 6% | -$520m |

Budget and financing rates are **illustrative**, not SEC-reported or validated forecasts. Under the base case a ~$2.44B one-time release generates ~$122M annual benefit at 5%, which does **not** recover ~$350M in first-year costs; cumulative economic payback may take years, and discount costs and cash-release persistence matter. The app's interactive sensitivity heatmap varies DSO improvements and realization percentage.

## Road map
**Days 1–30:** reconcile AR aging, collectibility and rebates; segment supply chain inventory by service level and loss exposure; benchmark customer and supplier terms and financial-concession costs. Build quarterly seasonal baselines.

**Days 31–60:** run bounded, measured receivables and inventory pilots. Negotiate payment terms only where discount forfeiture, supplier fragility and procurement price concessions are controlled. Track gross and net releases, not just reported DPO.

**Days 61–90:** construct supplier-risk-adjusted three-year NPV with program software, integration, controls, people costs, price concessions, bad-debt/stockout risk and discount rate. Require CFO and procurement stage gates before rollout.

## Key limitations
This is a descriptive three-company annual-filing comparison. Apple, Dell and Microsoft have different fiscal calendars, product versus service mixes, vendor and trade balances, payment programs and growth trajectories. None of the proposed policy impacts is causally identified; no operational feasibility has been established. Extensions of DPO may harm suppliers or sacrifice discounts, reductions in inventory may impair availability, and faster customer collections may require rebates. Derived ratios and scenarios are **analyst calculations**, not SEC-reported metrics or investment advice.

## Expanded peer universe (SEC XBRL, October 27, 2026)
Two added issuers fill gaps in the old 3-company sample. **HP Inc. (HPQ)** is a closer hardware and PC comparison to Dell and Apple's device manufacturing; **Cisco (CSCO)** adds networking equipment and enterprise-infrastructure economics. Cisco and Microsoft are *context*, not direct supplier-term or CCC targets for Apple. HPE was investigated but deliberately excluded from this scored panel until its consolidated cost-of-sales XBRL mapping can be defensibly reproduced.

| Company | Fiscal end | Revenue ($m) | COGS ($m) | DSO | DIO | DPO | CCC | FCF ($m) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| HP Inc. | 2025-10-31 | 55,295 | 43,903 | 35.67 | 67.47 | 145.30 | -42.15 | 2,800 |
| Cisco Systems | 2026-07-25 | 63,325 | 22,465 | 40.84 | 71.96 | 47.88 | 64.92 | 12,767 |

All 20 added statement inputs were checked against same-accession SEC CompanyConcept US-GAAP facts (including previous-year balances in the current annual report). The full ledger now contains **50 facts**. HP Inc.'s cash capex uses XBRL `PaymentsToAcquireProductiveAssets` (not the capex tag used by Cisco). Ranking the whole five-company universe by CCC alone is misleading: gross margins, services intensity, hardware mix, contract terms, supplier-finance programs and reporting dates differ.

**Managerial interpretation:** use HP and Dell to challenge assumptions about equipment inventory, receivable terms and component procurement; treat Cisco as infrastructure sensitivity; benchmark Microsoft as software/cloud contrast only. The Apple cash-release scenario remains an illustrative decision tool, not a prediction that peer CCC can be replicated.\n
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
