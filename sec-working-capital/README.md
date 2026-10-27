# SEC Working Capital Optimization | CFO Advisory

**SEC XBRL-reconciled analytics and business decision case** using Apple FY2025, Dell FY2026, HP Inc FY2025, Cisco FY2026 and Microsoft FY2026 annual reports.

[Live Streamlit dashboard](https://sec-working-capital-advisory.onrender.com) · [CFO executive memo](docs/executive_memo.md) · [SEC XBRL source validation](docs/xbrl_reconciliation.md) · [Audit ledger: 50 facts](data/xbrl_audit.csv)

## Model
Analyze working-capital days (DSO, DIO, DPO), cash conversion, cash capex and FCF. Test hypothetical one-time liquidity release versus implementation costs, financing benefit, and realization uncertainty. Heatmap sensitivity and risk-aware peer benchmarking are included.

**Correction:** The Dell FY2026 cash-capex fact is **USD 2,633 million**, correcting the original extracted USD 2,630 million; Dell FCF is USD **8,552 million**. All **50** modeled source facts were separately reconciled to accession-linked SEC XBRL companyconcept values. See `data/xbrl_audit.csv` for CIK, GAAP tag, accession, exact USD value, and source URL. The dashboard offers peer filters and a margin-vs-CCC operating model visualization; it checks the audit ledger before calculating ratios.

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
