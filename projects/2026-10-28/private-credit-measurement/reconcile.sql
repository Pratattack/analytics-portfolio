SELECT vehicle, assets-liabilities-equity AS rounding_residual,
       CASE WHEN equity IS NOT NULL THEN equity/assets END AS reported_equity_share,
       bank_loans/assets AS bank_funding_share
FROM vehicles;
