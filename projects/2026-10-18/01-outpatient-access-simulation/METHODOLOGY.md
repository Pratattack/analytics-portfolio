# Decision requirements, inputs and verification

## Business decision

A hypothetical clinic operations team must choose whether to protect short-notice appointment slots, release unused capacity, or fund additional staffing. Candidate policies are selected by the lowest incremental modeled cost among policies whose development averages meet urgent-within-one-day and routine-within-seven-day booking rates of at least 90%. Holdout performance and costs are then reported without changing selection. These administrative categories and targets are case assumptions, not clinical triage standards.

## Experimental design

- Demand arrives over 220 business-day steps; calendar capacity spans 280 steps.
- The evaluation cohort comprises requests arriving on days 40 through 199, inclusive. Earlier requests warm the system; later days allow follow-up.
- Seeds 10000–10009 support development; 10010–10039 support holdout evaluation.
- Each policy sees identical requests, no-show uniforms and absence realizations for a seed. Policy comparisons are paired by seed.
- Stress seeds 20000–20009 are reused across separate demand/absence conditions. Stress is a scenario analysis, not a statistical holdout from real operations.
- Approximate 95% mean-difference intervals use 1.96 × standard error across the thirty independent holdout replications. The intervals quantify Monte Carlo noise under fixed assumptions, not parameter uncertainty or clinical effectiveness. Normal intervals can extend beyond feasible proportion-difference bounds and are not a probability guarantee.

## Booking mechanics

Bookings are considered in business-day steps, up to ten calendar steps ahead. FCFS sorts by original request day and identifier. Other policies prioritize the exogenous urgent label, then age. Urgent requests consume reserved capacity first; routine requests use public capacity and, when release rules permit, unused reserved capacity. Each slot is counted exactly once. A bookkeeping cache is audited against the full calendar after each simulation. Unbooked requests stay pending and remain in the cohort denominator at the final horizon.

No-shows consume their assigned slot. They do not alter booking access, and the model does not rebook them. All absence is assumed known at booking time, an optimistic simplification. No abandonment, cancellations, delays in learning absence, provider continuity, patient preferences or intraday waiting are modeled.

## Inputs

| Config field | Meaning |
|---|---|
| mean_daily_requests | Poisson demand rate before deterministic seasonal modulation |
| urgent_fraction | Synthetic probability of the administrative urgent-request label |
| urgent_no_show / routine_no_show | Fixed attendance assumptions independent of waiting |
| base_slots | Baseline total appointments/day before known absence |
| extra_slots | Additional staffed appointments/day for a candidate policy |
| reserved | Capacity protected for short-notice requests until release |
| release_days | Reserved slots become public when appointment day minus booking day is no greater than this; -1 means never release |
| booking_window | Number of prospective business-day steps searched each day |
| extra_slot_cost_usd | Hypothetical marginal staffing cost per offered extra slot/day |
| contribution_per_completed_visit_usd | Hypothetical contribution per eventually completed cohort visit |

## Request outcome dictionary

| Field | Definition |
|---|---|
| request_id | Synthetic identifier, unique within one replication |
| request_day | Business-day index when request entered |
| urgent | Exogenous synthetic administrative label, 0/1 |
| appointment_day | Booking's service day, or -1 if still unbooked at horizon |
| wait_days | Appointment day minus request day; -1 denotes unbooked |
| completed | 1 if attended; 0 if no-show or unbooked |
| in_cohort | Request arrived within evaluation window |
| slot_class | public, reserved or none; a capacity-accounting category |

The audit sample includes a single holdout seed for the selected policy, not all replications. `replications.csv` stores all policy-seed summaries. Service rates use all cohort requests of the relevant class in the denominator. Mean booked waiting time excludes unbooked requests and must be read beside the unbooked count. Attendance and booking access measure different events.

## Financial interpretation

Incremental modeled contribution = completed-visit difference × assumed visit contribution, minus extra offered slots × assumed slot cost × 160 evaluation days, minus one-time setup. Cohort visits can finish after the arrival evaluation window, so this is a cohort-based illustrative calculation, not period revenue recognition. No abandonment or wait-dependent attendance is assumed; the model consequently does not estimate revenue unlocked by faster access. It excludes health benefits, overtime fatigue, payer mix, capital, billing and reimbursement differences.

## Verification and adoption

Ten unit tests use hand-worked booking cases, reserved/public accounting, release behavior, absence, no-shows, censoring and invalid inputs. Integration checks reconcile SQL totals and exact access denominators, validate disjoint seeds, audit capacity and recompute economics. A clean output deletion and rerun must produce identical SHA-256 hashes. SVG markup and report structure are checked; this is not independent human or clinical review.

Actual adoption requires governed appointment and staffing data; clinical input on appropriate targets; continuity, equity and staff-workload checks; sensitivity to no-show/abandonment behavior; and a controlled operational pilot. The model itself makes no patient-level care decisions.
