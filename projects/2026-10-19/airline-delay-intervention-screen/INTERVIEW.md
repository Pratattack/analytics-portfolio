# Airline project: explanation, resume language and interview defense

## Plain-English understanding

This project asks where an aviation diligence team should spend limited investigation time. A large airport operation can have many delay minutes simply because it handles many flights. I compare each carrier with other operating carriers at the same airport in the same month, excluding it from its own benchmark. I freeze the eligible sites and ranking using January–August 2024, then inspect 2025 and 2026 without changing the rules to make later results look better.

The ten-site peer-adjusted queue captures 43.38% of the eligible pool's positive peer excess in January–August 2026, compared with 33.34% for the raw-delay baseline. This is evidence about where gaps concentrate, not evidence that a carrier can eliminate them. Route, aircraft and schedule differences remain. I should be able to trace any input to its original row, explain the 148 quarantines, defend the capacity constraint and describe the operational pilot needed before claiming savings.

## Accurate resume bullets

- Built a Python/SQL airline operations research pipeline for 60,093 official carrier-airport-month records, preserving source lineage and quarantining 148 records that failed missing-value or reconciliation checks.
- Evaluated a fixed, capacity-constrained investigation queue across later periods; selected sites captured 43.38% of eligible positive peer excess in January–August 2026 versus 33.34% for the raw-delay baseline, a 10.04-percentage-point diagnostic difference.

The result is observational benchmark concentration, not measured operational improvement or employer work.

## Five interview questions and grounded answers

1. **Why not simply rank total delays?** Total burden is strongly affected by scale and local conditions. The SQL view calculates a flight-weighted rate among other carriers at the same airport/month. The focal carrier's excess is its actual carrier-categorized minutes minus flights times that excluded-self rate. Raw delay burden is retained as a simple baseline under identical capacity constraints.
2. **How did you avoid tuning to the final diagnostic?** Candidate membership, scores, ten slots and two-per-airport cap are fixed from January–August 2024. The 2025 checkpoint and 2026 diagnostic use the same calendar months. The interactive tool labels changes as exploratory; it does not change the published fixed-policy result. Historical source vintages are not reconstructed, so the split is retrospective stability research.
3. **Why can the policy use a greedy selector?** Every investigation consumes one equal-cost slot and each airport has a count cap. Descending positive scores solve this particular partition-cap selection problem. A small exhaustive enumeration independently checks the selector. Unequal costs, dependencies or many interacting constraints would require a different optimization formulation.
4. **What did the interval establish?** The 95% exploratory interval for the capture difference is 5.94–13.07 percentage points, using 2,000 circular two-month block draws across eight diagnostic months. It preserves common monthly shocks across sites and some local dependence. Eight months are limited; this is neither a treatment-effect interval nor guaranteed future coverage.
5. **What would make you reject a real rollout?** Unresolved source changes, incomplete comparable operating months, gaps explained by schedule/fleet composition, an unfavorable incremental-cost case, or a pilot that worsens cancellation/safety/customer outcomes. The code deliberately keeps the prospective deployment gate false. The application's invalid-input, empty-search, reset and policy-switch flows are separate browser checks, not proof of intervention effectiveness.
