# SEC Working Capital Optimization | CFO Advisory

**SEC XBRL-reconciled analytics and business decision case** using 15 publicly traded technology, device, semiconductor, and infrastructure companies, FY2025–FY2026 annual reports.

[Live Streamlit dashboard](https://sec-working-capital-advisory.onrender.com) · [CFO executive memo](docs/executive_memo.md) · [SEC XBRL source validation](docs/xbrl_reconciliation.md) · [Audit ledger: 150 facts](data/xbrl_audit.csv)

## Model
Analyze working-capital days (DSO, DIO, DPO), cash conversion, cash capex and FCF. Test hypothetical one-time liquidity release versus implementation costs, financing benefit, and realization uncertainty. Heatmap sensitivity and risk-aware peer benchmarking are included.

**Correction:** The Dell FY2026 cash-capex fact is **USD 2,633 million**, correcting the original extracted USD 2,630 million; Dell FCF is USD **8,552 million**. All **150** modeled source facts were separately reconciled to accession-linked SEC XBRL companyconcept values. See `data/xbrl_audit.csv` for CIK, GAAP tag, accession, exact USD value, and source URL. The dashboard offers peer filters and a margin-vs-CCC operating model visualization; it checks the audit ledger before calculating ratios.

## Reproduce
```bash
pip install -r requirements.txt
python scripts/analysis.py
python scripts/load_sqlite.py
python -m pytest -q
streamlit run app.py
```
All repository paths above are relative to this project folder. GitHub Actions is configured to rerun project tests on commits.

## Sources
- [Apple 2025 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm)
- [Dell 2026 10-K](https://www.sec.gov/Archives/edgar/data/1571996/000157199626000008/dell-20260130.htm)
- [Microsoft 2026 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm)

## Interpretation and limits
Company financial values are linked to US-GAAP XBRL facts, but cross-company operating metrics are **not** like-for-like targets. Business models and fiscal year ends vary. Scenario gross cash release is a **one-time** theoretical balance-sheet movement, **not** profit, cash-flow guidance, or a causal estimate. Implementation costs, supplier discounts and risks may destroy economic value. Free Render hosting can cold-start.


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
