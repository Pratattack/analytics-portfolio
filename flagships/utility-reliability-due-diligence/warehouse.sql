-- Customer-weighted normal-day IEEE SAIDI; never pool reporting standards.
SELECT year,state,COUNT(*) reporting_utility_state_rows,
 SUM(customers) reported_customers,
 SUM(saidi_normal*customers)/SUM(customers) weighted_normal_saidi_minutes,
 SUM(saidi_normal*customers)/60.0 normal_customer_hours
FROM reliability
WHERE standard='IEEE' AND customers>0 AND saidi_normal IS NOT NULL
GROUP BY year,state ORDER BY year,state;
