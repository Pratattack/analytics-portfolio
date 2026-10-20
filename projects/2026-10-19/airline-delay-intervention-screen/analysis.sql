-- Operating-carrier x destination-airport x month. Never combine marketing network totals.
CREATE VIEW airport_month AS
SELECT year,month,airport,COUNT(*) AS carriers,SUM(arr_flights) AS flights,
 SUM(carrier_delay) AS minutes FROM valid GROUP BY year,month,airport;
CREATE VIEW peer_screen AS
SELECT v.*, a.carriers-1 AS peer_carriers,a.flights-v.arr_flights AS peer_flights,
 (a.minutes-v.carrier_delay)/(a.flights-v.arr_flights) AS peer_minutes_per_flight,
 v.carrier_delay-v.arr_flights*(a.minutes-v.carrier_delay)/(a.flights-v.arr_flights) AS excess_minutes
FROM valid v JOIN airport_month a USING(year,month,airport)
WHERE a.carriers-1 >= (SELECT minimum_peer_carriers FROM thresholds) AND a.flights-v.arr_flights >= (SELECT minimum_peer_flights FROM thresholds);
