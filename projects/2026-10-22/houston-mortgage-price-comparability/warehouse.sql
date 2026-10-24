SELECT lei,cell,COUNT(*) n,SUM(spread) spread_sum,AVG(spread) spread_mean,AVG(cost_bps) gross_cost_bps_mean FROM loans GROUP BY lei,cell ORDER BY lei,cell;
