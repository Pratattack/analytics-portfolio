-- SQL independently aggregates the selected portfolio's scenario accounting.
SELECT scenario,
       SUM(capex_musd) AS capex_musd,
       SUM(annual_customer_hours_avoided) AS annual_customer_hours_avoided,
       SUM(annual_benefit_musd) AS annual_social_benefit_musd,
       SUM(annual_opex_musd) AS annual_opex_musd,
       SUM(npv_musd) AS social_npv_musd
FROM selected
GROUP BY scenario ORDER BY scenario;
