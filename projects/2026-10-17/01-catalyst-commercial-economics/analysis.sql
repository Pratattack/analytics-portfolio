CREATE TABLE commercial(customer TEXT, product TEXT, period INTEGER CHECK(period IN(0,1)), quantity REAL CHECK(quantity>=0), price REAL CHECK(price>0), unit_cost REAL CHECK(unit_cost>=0), service_cost REAL CHECK(service_cost>=0), PRIMARY KEY(customer,product,period));
-- ANALYSIS
SELECT customer, SUM(quantity*price) revenue, SUM(quantity*(price-unit_cost)) variable_contribution, SUM(service_cost) service_cost, SUM(quantity*(price-unit_cost)-service_cost) contribution_after_service FROM commercial WHERE period=1 GROUP BY customer ORDER BY contribution_after_service ASC;
