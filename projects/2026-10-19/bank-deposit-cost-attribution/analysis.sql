-- Endpoint-average balance is a proxy, NOT the regulatory daily-average denominator.
CREATE VIEW quarterly_proxy AS
SELECT c.*, (c.depdom+p.depdom)/2.0 AS average_domestic_deposits,
 ((c.depdom-c.depnidom)+(p.depdom-p.depnidom))/2.0 AS average_interest_bearing_deposits,
 ((c.depdom-c.depnidom)+(p.depdom-p.depnidom))/(c.depdom+p.depdom) AS interest_bearing_share,
 4.0*c.edepdomq/(((c.depdom-c.depnidom)+(p.depdom-p.depnidom))/2.0) AS annualized_proxy_rate
FROM bank_quarter c JOIN bank_quarter p ON c.cert=p.cert AND c.previous_date=p.report_date
WHERE c.accepted=1 AND c.depdom+p.depdom>0
AND ((c.depdom-c.depnidom)+(p.depdom-p.depnidom))/2.0 >= (SELECT minimum_ib_balance FROM thresholds);
CREATE VIEW industry_totals AS
SELECT report_date,COUNT(*) AS institutions,SUM(dep) AS total_deposits_thousand_usd,
 SUM(depdom) AS domestic_deposits_thousand_usd,SUM(edepdomq) AS quarterly_domestic_expense_thousand_usd
FROM bank_quarter GROUP BY report_date;
