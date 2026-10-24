SELECT ticker,COUNT(*) observations,SUM(accretion) accretion_sum,SUM(revisions) revision_sum,COUNT(cash) explicit_cash_observations FROM ledger GROUP BY ticker ORDER BY ticker;
