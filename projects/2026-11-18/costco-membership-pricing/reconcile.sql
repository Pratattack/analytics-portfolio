SELECT period,
       net_sales + fees - revenue AS revenue_residual,
       revenue - merchandise_cost - sg_and_a - operating_income AS operating_income_residual
FROM reported ORDER BY period;
