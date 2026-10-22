SELECT ticker, COUNT(*) AS total_scope_dates, MAX(end) AS latest_end,
 SUM(deposits) AS historical_deposit_sum_not_current_exposure,
 SUM(remaining_price) AS historical_remaining_price_sum_not_debt
FROM observations WHERE scope='total' GROUP BY ticker ORDER BY ticker;
