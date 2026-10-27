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

See [SEC audit ledger](../data/xbrl_audit.csv); all **30 inputs** were checked against relevant annual 10-K accession-linked XBRL facts. Fiscal year ends and operating economics are unlike one another. **Peer CCC differences are not attainable targets**, especially for a company already exhibiting substantial negative CCC.

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
