SELECT SUM(payments_usd_at_base_spot+receipts_usd_at_base_spot) AS gross_notional,SUM(ABS(payments_usd_at_base_spot-receipts_usd_at_base_spot)) AS net_notional FROM flows;
