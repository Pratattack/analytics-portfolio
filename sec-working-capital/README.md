# SEC Working Capital | CFO Advisory

A reproducible, exploratory finance consulting case using Apple FY2025, Dell FY2026 and Microsoft FY2026 SEC 10-K data. **Preliminary Firecrawl-extracted values, not independently reconciled to XBRL.** Different fiscal calendars and business models limit comparability.

## Run
```bash
pip install -r requirements.txt
python scripts/analysis.py
python scripts/load_sqlite.py
python -m pytest -q
streamlit run app.py
```

## Decision question
What hypothetical gross liquidity could Apple release by reducing DSO/DIO or extending DPO? These scenarios are **not profit, cash-flow forecasts, or recommended supplier actions**.

DSO = average AR / revenue * 365; DIO = average inventory / COGS * 365; DPO = average AP / COGS * 365; CCC = DSO + DIO - DPO. FCF = CFO - capex.

## Source filings
- [Apple FY2025](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm)
- [Dell FY2026](https://www.sec.gov/Archives/edgar/data/1571996/000157199626000008/dell-20260130.htm)
- [Microsoft FY2026](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm)

## Limitations
Dell and Microsoft HTML inputs were truncated during Firecrawl extraction. The figures have not been independently reconciled against individual SEC XBRL facts. Annual average balances mask seasonality. Receivables and payables classifications differ. Do not use for investment decisions or claim audited analysis of these derived metrics. A separate SEC CompanyFacts refresh script is supplied for raw-data retrieval with a compliant user agent.

## Verification
Unit tests pass locally (2/2). Browser-based Streamlit smoke testing was attempted but the execution environment blocked localhost navigation; no claim of browser verification is made.
