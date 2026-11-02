WITH p AS (
 SELECT company,period,
 MAX(CASE WHEN metric='assets' THEN value END) assets,
 MAX(CASE WHEN metric='liabilities' THEN value END) liabilities,
 MAX(CASE WHEN metric='equity' THEN value END) equity,
 MAX(CASE WHEN metric='cfo' THEN value END) cfo,
 MAX(CASE WHEN metric='cfi' THEN value END) cfi,
 MAX(CASE WHEN metric='cff' THEN value END) cff,
 MAX(CASE WHEN metric='fx_cash' THEN value END) fx,
 MAX(CASE WHEN metric='cash_change' THEN value END) cash_change
 FROM actuals GROUP BY company,period
)
SELECT company,period,'Balance sheet' AS check_name,assets-liabilities-equity AS difference_usd_m
FROM p WHERE assets IS NOT NULL
UNION ALL
SELECT company,period,'Cash flow',cfo+cfi+cff+fx-cash_change FROM p
WHERE cfo IS NOT NULL AND fx IS NOT NULL
ORDER BY company,period,check_name;
