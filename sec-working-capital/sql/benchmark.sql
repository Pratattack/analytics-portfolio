-- Independent SQL financial ratio calculations directly from raw annual 10-K inputs.
-- USD millions, 365-day convention; keep 'working_capital' raw fields intact.
SELECT ticker, company, fiscal_end,
 ROUND(365.0*(ar+prior_ar)/2/revenue,2) AS dso_days,
 ROUND(365.0*(inventory+prior_inventory)/2/cogs,2) AS dio_days,
 ROUND(365.0*(ap+prior_ap)/2/cogs,2) AS dpo_days,
 ROUND(365.0*((ar+prior_ar)/2.0/revenue+(inventory+prior_inventory)/2.0/cogs-(ap+prior_ap)/2.0/cogs),2) AS ccc_days,
 cfo-capex AS fcf_musd,
 ROUND((cfo-capex)*1.0/revenue,4) AS fcf_margin
FROM working_capital ORDER BY ticker;