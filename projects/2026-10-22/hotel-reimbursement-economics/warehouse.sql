SELECT ticker, COUNT(*) AS annual_records,
 SUM(revenue) AS annual_revenue, SUM(reimb_revenue) AS annual_reimbursement_revenue,
 SUM(reimb_revenue-reimb_expense) AS annual_recovery_balance,
 SUM(op_income-reimb_revenue+reimb_expense) AS annual_profit_ex_recovery
FROM observations WHERE period='annual' GROUP BY ticker ORDER BY ticker;
