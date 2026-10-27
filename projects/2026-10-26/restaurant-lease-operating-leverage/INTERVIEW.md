# Resume evidence and interview defense

## Two accurate resume bullets

- Built a Python/SQL restaurant-finance panel of 32 issuer-years across six operators, reconciling 24 latest reported revenue, operating-earnings and lease facts to original SEC filing contexts.
- Evaluated 216 lease-aware earnings scenarios and 72 response-cap sensitivities; independently reconciled every reference case with HiGHS, retaining 32 infeasible scenarios and explicit accounting-scope limits.

## Five implementation-based questions

**1. How do you avoid double-counting rent?** Reported EBIT already includes base lease expense. I subtract only lost-sales contribution and incremental lease escalation; I do not deduct the full rent again.

**2. Why retain both lease cost and lease payments?** They measure expense and cash, with timing and scope differences. Their selected FY2025 sums are $1.089B and $1.099B, across differing fiscal ends. The difference is a diagnostic, not savings or a funding gap.

**3. What is the optimization?** Minimize assumed resource cost 0.5x + 0.15y, where x is incremental cost savings and y recovered lost sales, subject to x + margin×y covering the EBIT gap and both levers staying within caps. The objective weights and capacities are assumed, not disclosed execution costs.

**4. How did you verify it?** All 216 reference scenarios agree with an independently formulated SciPy/HiGHS LP. Two-dimensional vertex enumeration and hand examples separately check the bounded-lever logic and the accounting equation.

**5. What would prevent adoption?** Missing store-level margins, demand response, one-off costs, lease reset terms and current cash/covenant evidence. A feasible model solution can still be operationally impossible; the 32 infeasible scenarios are not proof of actual issuer distress.

Portfolio implementation only; no corporate cost savings, management mandate, lending approval or operational intervention is implied.
