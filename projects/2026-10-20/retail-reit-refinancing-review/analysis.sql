CREATE VIEW maturity_exposure AS
SELECT ticker,
       SUM(CASE WHEN ordinal=1 THEN principal ELSE 0 END) AS next_twelve_months,
       SUM(CASE WHEN ordinal<=5 THEN principal ELSE 0 END) AS five_year_principal,
       SUM(principal) AS total_disclosed_principal,
       SUM(CASE WHEN ordinal<=2 THEN principal ELSE 0 END)/SUM(principal) AS first_two_year_concentration
FROM maturity
GROUP BY ticker;
