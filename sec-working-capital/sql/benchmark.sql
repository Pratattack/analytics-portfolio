SELECT ticker, fiscal_end, ROUND(dso,2) AS dso_days, ROUND(dio,2) AS dio_days, ROUND(dpo,2) AS dpo_days, ROUND(ccc,2) AS ccc_days, ROUND(fcf,0) AS fcf_musd FROM working_capital ORDER BY ccc;
