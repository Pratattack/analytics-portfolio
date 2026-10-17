# Decision design and implementation

## Business question

Which reliability upgrades should a hypothetical multi-district utility fund when capital, implementation resources and service commitments constrain the portfolio? The decision owner is an investment committee; finance, operations, engineering and customer-service teams validate assumptions before implementation.

## Requirements and acceptance criteria

| Requirement | Acceptance evidence |
|---|---|
| Budget cannot exceed $20m including 20% project reserve | Selected reserved cost and scenario capex checks |
| At most one intervention in each district | Multiple-choice search structure and uniqueness test |
| Delivery demand cannot exceed 14 crew units | Portfolio feasibility check |
| At least two critical-service districts receive upgrades | Explicit floor in config and feasibility checks |
| Candidate economics are traceable | Frozen source rows, config, detail CSV, SQL reconciliation |
| Recommendation addresses uncertainty | Maximin objective, policy comparison, valuation and coverage sensitivity |
| Analysis is repeatable | Standard-library pipeline and byte-identical clean rerun |
| Downside is visible | Outside-set joint stress and break-even outage valuation |

All budget, crew, critical-service and valuation requirements are invented case assumptions, not employer policies.

## Mathematical formulation

For district i and intervention j, x(i,j) is binary. Option 0 is no action. Every district selects exactly one option. In scenario s, let v(i,j,s) be social NPV. Choose the allocation that maximizes t, subject to:

- t <= sum_i,j v(i,j,s) × x(i,j), for every modeled scenario s;
- sum_i,j reserved_cost(i,j) × x(i,j) <= budget;
- sum_i,j crew(i,j) × x(i,j) <= crew_limit;
- sum_i,j critical(i) × x(i,j) for nonzero interventions >= 2;
- sum_j x(i,j) = 1, for every district i.

No probabilities are assigned to the maximin scenario set. The equal-weight comparator uses an illustrative arithmetic mean across scenarios, not an empirical forecast.

## Benefit accounting

1. Take normal-day SAIDI from the selected historical benchmark year.
2. Define an event-sensitive proxy as max(all-event SAIDI minus no-major-event SAIDI, 0). This is an analytical contrast between indices, not a causal storm attribution.
3. Apply scenario multipliers and assumed intervention-specific reductions.
4. Multiply minutes avoided per customer by hypothetical customers, divided by 60, to obtain avoided customer-hours/year.
5. Multiply by the assumed USD/customer-hour to value social benefits; subtract annual project O&M.
6. Discount annual net social benefits during years after commissioning through year ten. Subtract actual scenario capex at time zero.

Customer counts are illustrative; state SAIDI is used as a hypothetical benchmark and is not multiplied by an actual state population. There is no claim of observed avoided outages. Value of lost load varies substantially by customer and event; the $12 assumption is deliberately exposed and stress-tested, not sourced from EIA.

## Public data provenance

`data/eia_source_snapshot.json` preserves ten selected rows of the source table, with table title, URL and retrieval date. `data/reliability_benchmarks.csv` is generated from its explicit fields. Verification re-parses each preserved row with inspected column indices: coverage 2024/2023 at columns 1/2, all-event SAIDI at 3/4 and no-major-event SAIDI at 9/10. It compares all 60 numerical fields to the generated CSV. This validates extraction consistency; it is not a second independent measurement of EIA data.

This intentionally selected sample is not representative of every U.S. utility or state. Coverage differences and reporting-method consistency matter. Do not mix IEEE and any-method values. Texas and Louisiana have below-80% IEEE reporting coverage; the separate coverage-sensitivity case excludes them without claiming 80% is an official quality cutoff.

## Policies and sensitivity

- **Robust:** maximize minimum NPV across all four modeled scenarios.
- **Equal-weight:** maximize arithmetic-mean scenario NPV.
- **Greedy:** satisfy the critical floor first, then rank choices by equal-weight NPV per reserved dollar, respecting capacity and one-choice constraints; it never replaces an earlier choice.
- **Scenario oracle:** optimize knowing one scenario in advance; compare the difference as hindsight regret, not achievable foresight.
- **Outside-set stress:** evaluate the fixed robust allocation at a lower outage valuation, lower effectiveness and longer delay; no reoptimization.
- **Budget frontier:** reoptimize at $8m, $12m, $16m, $20m, $24m and $28m.
- **Valuation sensitivity:** reoptimize at $6, $9, $12, $15 and $18 per customer-hour.

## Validation strategy

Twelve unit tests include hand-calculated social-value and delay cases, a known robust optimum, an equal-weight dynamic-programming oracle, zero budgets, infeasible requirements, no double purchases, reserve limits and monotonicity. Integration checks independently reconstruct discounted flows from scenario detail and reconcile SQL totals, verify feasibility, compare all decision policies and rebuild cleared outputs. Source and output hashes provide tamper-evident fingerprints, not a signature of correctness.

## Limits and implementation gates

The largest limitation is extrapolating aggregate historical state metrics to hypothetical districts. Neither costs nor intervention effectiveness are estimated from data. Uncertainty scenarios do not span every possible future. Benefits are additive, exclude spillovers and intervention overlap, and do not model grid topology, load flow, climate hazard distributions or regulatory cost recovery.

For actual deployment: obtain feeder-level asset, outage and customer data; define governance and access controls; commission engineering estimates; estimate or validate treatment effects; review valuation with finance/regulatory teams; integrate approval gates and cost controls; pilot interventions; and measure weather-adjusted outcomes. Avoid attributing before/after differences to the intervention without a defensible counterfactual.
