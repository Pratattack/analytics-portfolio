SELECT date, hourly_usd * weekly_hours AS nominal_weekly_usd,
       hourly_usd * weekly_hours / cpi * 100.0 AS real_weekly_1982_84_usd
FROM monthly ORDER BY date;
