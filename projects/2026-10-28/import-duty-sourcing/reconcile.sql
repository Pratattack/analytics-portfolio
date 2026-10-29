SELECT year,hs4,SUM(value_ytd) AS customs_value,SUM(duty_ytd) AS calculated_duty,
       CAST(SUM(duty_ytd) AS REAL)/NULLIF(SUM(value_ytd),0) AS historical_duty_ratio
FROM trade GROUP BY year,hs4;
