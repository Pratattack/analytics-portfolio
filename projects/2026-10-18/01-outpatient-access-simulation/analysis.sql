SELECT urgent, COUNT(*) requests,
       SUM(appointment_day>=0) booked, SUM(appointment_day<0) unbooked,
       SUM(completed) completed,
       SUM(appointment_day>=0 AND completed=0) no_shows,
       AVG(CASE WHEN wait_days>=0 THEN wait_days END) mean_booked_wait
FROM outcomes WHERE in_cohort=1 GROUP BY urgent ORDER BY urgent;
