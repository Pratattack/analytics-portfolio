# Plain-English understanding

An insurer pays claims over time, so a year's accidents can continue generating payments many years later. This project reads those development tables directly from six insurers' filings, preserving which business line and accident year each number describes. A chain-ladder model learns how cumulative payments have historically grown from one age to the next and uses those factors to challenge the amount still unpaid. It retains 4,046 paid/incurred cells and fits 31 of 48 disclosed triangles; the remaining 17 stay visible with their model-exclusion reasons.

The most important finding is why a finance committee should not simply release the apparent difference. The default modeled unpaid amount is $38.67bn against a comparable disclosed $59.76bn, but a 1.10 tail factor alone adds $17.12bn. The oldest observed age does not mean all claims are settled. The retrospective benchmark comparison is encouraging, but revised historical information and missing tail evidence prevent a reserve-release or validated-forecast claim. The useful recommendation is targeted actuarial diligence, not a capital action.

## Accurate resume bullets

- Built a Python/SQL insurance diligence pipeline tracing **4,046 paid/incurred disclosure cells across six insurers and 48 loss-development triangles**, preserving original filing contexts, units and model-exclusion reasons.
- Evaluated chain-ladder development on **468 masked one-step cells**, recording **14.54% WAPE versus 44.50%** for a repeat-increment baseline, and quantified **$17.12bn** of modeled sensitivity to a 1.10 tail factor without presenting it as realized savings or releasable capital.

## Five grounded interview questions

1. **Why work from original inline XBRL?** The standard companyfacts endpoint omits custom and dimensioned contexts. An apparently identical label can belong to a different segment or accident-year scope. I preserve context IDs, dimensions, scale, sign and exact source IDs.
2. **How is the development factor calculated?** For each age, divide total supported next-age cumulative paid by total current-age cumulative paid. Multiply a cohort's latest paid through the remaining factors to estimate ultimate; modeled unpaid is ultimate less what has already been paid.
3. **Why is the tail so important?** A tail factor applies to ultimate claims, not just to today's unpaid balance. The source horizon can stop before all payments finish. Assuming a tail of 1.00 therefore creates apparent headroom that cannot be interpreted as excess capital.
4. **What does the benchmark result establish?** Within the disclosed, revised cohort, the development method better matches 468 masked future cumulative movements than repeating the most recent increment. It does not establish an as-released historical strategy or future accuracy.
5. **What would you recommend to the committee?** Investigate the largest dollar tail sensitivities, reconcile excluded scopes and obtain independent actuarial selections and claims-level evidence. Keep reserve-release and predictive promotion false until those gaps are resolved.
