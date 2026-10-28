SELECT b.origin, AVG(p.price) AS sql_mean, COUNT(*) AS weeks
FROM blocks b JOIN prices p ON substr(p.date,1,10) BETWEEN b.origin AND b.end
GROUP BY b.origin ORDER BY b.origin;
-- NEXT QUERY --
SELECT MAX(0, actual_mean-budget_per_gallon) AS sql_shortfall
FROM evaluation ORDER BY rowid;
