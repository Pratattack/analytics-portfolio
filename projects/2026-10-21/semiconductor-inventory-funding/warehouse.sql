-- Entity scope is consolidated issuer; quarter flows in USD, not YTD.
SELECT ticker, COUNT(*) AS records, MIN(end) AS first_period, MAX(end) AS last_period,
 SUM(inventory) AS balance_sum_for_reconciliation, SUM(cost) AS quarterly_cost_sum
FROM panel GROUP BY ticker ORDER BY ticker;
