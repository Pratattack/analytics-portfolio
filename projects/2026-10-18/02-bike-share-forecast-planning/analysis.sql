SELECT model,COUNT(*) days,
 SUM(ABS(actual-prediction))/SUM(actual) AS wape,
 AVG(actual-prediction) AS mean_underprediction,
 AVG(actual>=lower_bound AND actual<=upper_bound) AS empirical_interval_coverage,
 SUM(shortfall) AS shortfall_trip_equivalents,
 SUM(excess) AS excess_trip_equivalents,
 SUM(decision_cost) AS modeled_decision_cost_usd
FROM scored WHERE phase='test' GROUP BY model ORDER BY modeled_decision_cost_usd;
