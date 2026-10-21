-- Reconcile the matched 2025 paid/incurred scope without summing overlapping aggregate lines.
CREATE VIEW current_balances AS
SELECT paid.group_id,
       COUNT(*) AS matched_accident_years,
       SUM(incurred.value - paid.value) AS reported_comparable_unpaid,
       SUM(paid.value) AS cumulative_paid
FROM cells paid
JOIN cells incurred
  ON incurred.group_id=paid.group_id
 AND incurred.accident_year=paid.accident_year
 AND incurred.valuation_year=paid.valuation_year
 AND incurred.metric='incurred'
WHERE paid.metric='paid' AND paid.valuation_year=2025
GROUP BY paid.group_id;
