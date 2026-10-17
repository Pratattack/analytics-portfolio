SELECT segment, arm, COUNT(*) prospects, SUM(converted) conversions, AVG(converted) conversion_rate FROM campaign GROUP BY segment,arm ORDER BY segment,arm;
