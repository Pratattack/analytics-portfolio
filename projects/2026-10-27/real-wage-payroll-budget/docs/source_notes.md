## Question and intended reader

When pay rises, how much purchasing power remains after inflation and changing hours? For economic research and workforce-finance readers, the project separates three observable ingredients before turning them into explicit payroll assumptions.

## Data and method

237 monthly calendar rows from January 2007 through September 2026. BLS total private average hourly earnings (CES0500000003), total private average weekly hours (AWHAETP) and CPI-U all items (CPIAUCSL) are seasonally adjusted. 236 rows support real-pay calculations. CPI is missing for October 2025, which remains missing rather than interpolated. BLS documents the missing CPI collection during the federal lapse in appropriations: https://www.bls.gov/cpi/additional-resources/2025-federal-government-shutdown-impact-cpi-faq.htm

Real hourly pay = nominal hourly pay / CPI × 100. Real weekly pay adds the hours term. Exact log decomposition uses 100 × log changes, which are explicitly distinct from ordinary percentage changes. Three prespecified anchors (January 2007, January 2019, February 2020) expose baseline sensitivity. A full monthly calendar is retained and year-over-year change disables forward filling. Independent SQL reconciles every monthly result, including the missing observation.

The scenario calculator solves required hourly change = (1 + assumed inflation) × (1 + target real weekly change) / (1 + assumed hours change) − 1. It is an identity rather than a statistical forecast. Company-level assumptions are hypothetical.

## Limits and decision use

National averages are composition sensitive. A higher average is not proof that an individual worker received a raise. This is not a Houston wage estimate. Gross earnings exclude employee benefits, irregular bonuses and employer payroll taxes. CPI-U is an aggregate consumption measure. The source history can be revised, and missing collection also affects adjacent CPI estimates. This project does not recommend compensation for real employees, estimate causal effects or claim business savings.

Sources and definitions: https://fred.stlouisfed.org/series/CES0500000003 , https://fred.stlouisfed.org/series/AWHAETP , https://fred.stlouisfed.org/series/CPIAUCSL , https://www.bls.gov/news.release/realer.htm , https://www.bls.gov/web/empsit/cesfaq.htm

