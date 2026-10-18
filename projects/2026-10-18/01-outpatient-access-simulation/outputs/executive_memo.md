# Outpatient Access & Capacity: Test the Policy Before the Pilot

SYNTHETIC OPERATIONS CASE · PAIRED SIMULATION · NO PATIENT DATA

## Decision

Development-selected policy: flex_plus_capacity. Holdout target pass: True. Diagnostic candidate: flex_plus_capacity. Choose the least-cost policy meeting both 90% booking targets in development, then inspect separate holdout performance before a pilot. Do not deploy a failing policy simply because it ranks best.

## Holdout outcomes

Across 30 independent holdout replications: urgent within one business day 100.0%; routine within seven business days 100.0%; mean booked wait 0.18 business days. Average unbooked cohort requests at the horizon: 0.00. Booked-wait averages exclude unbooked requests, so access rates retain all cohort requests in their denominators.

## Financial tradeoff

Paired mean incremental modeled contribution versus FCFS: $-53,600; approximate 95% Monte Carlo interval [$-53,600, $-53,600]. Assumptions: $75 contribution per completed visit, $65 per extra staffed slot per evaluation business day, and one-time setup. This is not observed revenue, clinical benefit or a complete provider P&L. Access improvement may justify a cost even without positive modeled contribution.

## Experiment and measurement design

Ten development replications select a policy; thirty disjoint holdout replications evaluate it. Common random request and absence streams make comparisons paired. Intervals describe simulation uncertainty conditional on invented parameters, not causal clinical effectiveness. A request is counted as timely access when booked within its target, regardless of attendance; completed visits and no-shows are reported separately.

## Stress and capacity

Three stress cases test 20% higher arrivals, more frequent absence and both together, each with ten replications. A booking-calendar audit enforces physical capacity. Business-day steps represent booking access; there is no intraday queue, patient acuity prediction, treatment allocation, emergency workflow, clinician continuity or downstream referral model.

## Data and assumptions

All requests, urgency labels, no-show probabilities and staffing assumptions are synthetic. Urgency is an exogenous administrative request label, not a clinical classification inferred by the model. A 40-day warmup precedes the 160-business-day evaluation cohort, followed by a drain period. Every request has one outcome; unbooked requests are explicitly censored, not erased. Capacity lost to absence is assumed known when booking, an optimistic limitation requiring prospective real-world testing.

## Personal understanding

I can explain why protecting same-day slots can improve urgent access while unintentionally worsening routine access or leaving capacity unused. Releasing unused reserved slots and adding capacity address different causes. I would examine both patient groups, no-shows, unbooked requests and staffing costs rather than presenting a single average wait as success.

## Implementation gates

Validate arrival, cancellation, no-show and staffing distributions using governed operational data; engage scheduling and clinical leaders to define appropriate service targets; test continuity and patient preferences; then run a time-limited operational pilot with predefined access, staff workload and equity guardrails. The simulation provides a planning case, not a clinical scheduling instruction.

## Source context

AHRQ, Open Access Scheduling for Routine and Urgent Appointments: https://www.ahrq.gov/cahps/quality-improvement/improvement-guide/6-strategies-for-improving/access/strategy6a-openaccess.html (reviewed 2026-10-18). It motivates measuring demand and available appointment slots; none of its reported case-study outcomes calibrate this simulation.

