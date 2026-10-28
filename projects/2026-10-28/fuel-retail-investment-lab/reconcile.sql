-- SQLite arithmetic independent of the Python calculation.
SELECT r."case", r.store_sales+r.lottery_ticket_sales+r.deli_sales+r.pizza_sales AS report_receipts,
       r.store_sales+r.deli_sales+r.pizza_sales+r.lottery_ticket_sales*a.lottery_commission AS retained_nonfuel_receipts,
       r.store_sales*a.store_margin + r.deli_sales*a.deli_margin + r.pizza_sales*a.pizza_margin
       + r.lottery_ticket_sales*a.lottery_commission + r.fuel_gallons*a.net_fuel_margin
       - (r.store_sales+r.deli_sales+r.pizza_sales)*a.nonfuel_card_fee AS net_contribution
FROM report_sales r CROSS JOIN assumptions a;
