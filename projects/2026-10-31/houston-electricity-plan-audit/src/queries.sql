-- Source-price reconciliation, without discarding failed checks.
SELECT p.name, p.source_id, a.kwh, a.published_cents,
       ROUND(a.rebuilt_cents,6) AS rebuilt_cents, a.within_rounding
FROM price_audit a JOIN plans p ON p.id=a.plan_id
ORDER BY p.name, a.kwh;

-- Equal-total usage comparison. Dollar differences are scenario results.
SELECT p.name, a.total_kwh,
       ROUND(a.cost_dollars,2) AS steady_cost,
       ROUND(b.cost_dollars,2) AS uneven_cost,
       ROUND(b.cost_dollars-a.cost_dollars,2) AS difference,
       a.credit_cycles AS steady_credit_cycles,
       b.credit_cycles AS uneven_credit_cycles
FROM scenarios a JOIN scenarios b ON a.plan_id=b.plan_id
JOIN plans p ON p.id=a.plan_id
WHERE a.profile_id='steady' AND b.profile_id='seasonal'
  AND a.total_kwh=b.total_kwh;

-- Term and document-vintage checks precede any ranking.
SELECT id, name, term_months, efl_date,
       CASE WHEN term_months<12 THEN 'shorter than horizon'
            WHEN efl_date<'2026-10-01' THEN 'historical label'
            ELSE 'October document; enrollment not verified' END AS status
FROM plans;
