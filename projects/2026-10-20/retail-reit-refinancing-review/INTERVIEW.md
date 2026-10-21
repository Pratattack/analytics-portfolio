# Interview explanation and measured resume bullets

I studied how six listed retail-property REITs could handle their disclosed debt maturities under different operating-cash-flow and refinancing conditions. I traced cash, debt and distributions to the original SEC filings, taking care not to mix a parent company with its operating partnership or add an unconsolidated joint-venture schedule to consolidated debt. The companies disclose $31.23 billion due over 2026–2030. The dashboard lets an analyst inspect an issuer, stress cash flow and refinancing spreads, and see the cash balance in every year.

The key result is that refinancing every maturity does not automatically solve a cash-flow problem. Thirty-seven of 90 persistent-shock scenarios still breach the assumed cash floor. These are conditional model results, not claims that the firms need funding today. I checked the minimum-rollover calculation against an independently constructed linear program in 180 cases. In an interview I would emphasize that shock duration, distributions, capex, actual credit facilities and covenants can change the recommendation; the model helps structure the next diligence questions.

## Resume bullets

- Reconciled 36 SEC debt-maturity buckets and 65 current source-linked facts for six retail REITs, mapping $53.25B of disclosed face principal and $31.23B due in 2026–2030 with explicit entity-scope and face-to-book bridges.
- Built a five-year refinancing constraint workbench covering 90 persistent-shock scenarios and 48 recovery sensitivities; independently reconciled 180 financing cases with SciPy/HiGHS and identified 37 modeled scenarios infeasible using rollover alone.

## Five interview questions and answers

**1. What was the hardest data problem?** Entity scope. SKT's operating-partnership facts are dimensioned and differ from parent cash / distributions. KIM's unconsolidated-JV mortgage schedule must not be added to the chosen consolidated unsecured ladder. I require exact dimensions and retain source IDs, dates and accession numbers.

**2. Why can 100% rollover still fail?** It removes principal paydown but not operating shortfalls, distributions, assumed capex, refinancing fees or incremental interest. If cash falls below the floor even at full rollover, the committee needs another documented lever, such as available liquidity or changed cash uses.

**3. How did you solve and verify the decision rule?** Each year's closing cash is affine in a common rollover share. I intersect all five cash-floor inequalities with the allowed 0–100% range. An independent implementation constructs linear-program constraints and solves them with SciPy/HiGHS; 180 actual-input cases reconcile. Empty feasible intervals remain infeasible.

**4. Why add a 40% CFO shock, and how likely is it?** The historical series includes one 38.90% annual decline, which challenges an initial 30% grid. I added a separate 40% case, without assigning a probability. A one-year event does not prove five-year persistence, so I also show recovery after two years; at 40% / 400bp, one of six becomes feasible, versus zero under persistence.

**5. What would you need before recommending a facility size?** Current treasury positions, actual available revolvers, covenants and borrowing-base rules, instrument-level rates / hedges, property capex and leasing needs, distribution constraints and subsequent transactions. The present incremental gap excludes financing costs of new liquidity and is only a conditional diligence envelope.
