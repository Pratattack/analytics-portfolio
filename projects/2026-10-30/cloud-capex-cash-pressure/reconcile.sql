SELECT symbol,ttm_end,metric,SUM(coefficient*value) AS ttm_value FROM lineage GROUP BY symbol,ttm_end,metric;
