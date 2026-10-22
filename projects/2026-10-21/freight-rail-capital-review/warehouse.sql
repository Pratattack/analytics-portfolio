-- Annual consolidated GAAP flows. A balance sum is an audit check, not portfolio capital.
SELECT ticker, COUNT(*) AS records, MIN(end) AS first_period, MAX(end) AS last_period,
 SUM(cfo) AS cfo, SUM(capex) AS capex, SUM(dividends+buybacks) AS cash_returns,
 SUM(cfo-capex-dividends-buybacks) AS residual
FROM panel GROUP BY ticker ORDER BY ticker;
