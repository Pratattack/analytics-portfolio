# October 19: two empirical industry decisions

## Airline Delay Intervention Screen

The [airline project](airline-delay-intervention-screen/) asks where a constrained industry diligence team should investigate carrier-delay performance. It preserves 60,093 official monthly records, source-row lineage, 148 quarantines and a leave-one-out airport/month benchmark. A ten-site queue fixed from Jan–Aug 2024 captures 43.38% of the original eligible pool's positive peer excess in Jan–Aug 2026, compared with 33.34% for the raw-delay baseline under identical capacity limits. The exploratory difference interval is 5.94–13.07 percentage points; no later-period retuning is performed.

What I should understand: volume and relative performance answer different questions. A large operation may accumulate many delays while performing near its local peers. Excluding the focal carrier from its own benchmark avoids diluting its gap. The proposed queue is for investigation; differences in route, fleet and schedule can explain gaps, and revised historical data do not establish a true decision-date backtest. I should be able to hand-compute a source row's peer benchmark and explain why intervention ROI still needs a controlled pilot.

## Bank Deposit Cost Attribution

The [banking project](bank-deposit-cost-attribution/) asks why deposit expense changes before recommending pricing action. It uses 48,814 official bank-quarters, the 4,238-institution latest insured domestic universe, quarter/YTD reconciliation and an exact volume/mix/proxy-rate bridge. Across 4,018 screened banks covering 90.96% of latest domestic deposits, Q2 expense fell $5.012bn year-over-year. Balance volume added $5.242bn and mix added $0.057bn, while the residual proxy-rate contribution reduced expense by $10.310bn. The unscreened matched cohort has a different $3.810bn decline, making selection sensitivity material.

What I should understand: an expense change does not identify a pricing effect. The derived rate uses an average of two endpoint balances and absorbs timing and product changes. The six-order decomposition is exact accounting, independently verified by a closed-form formula; it is not causal inference. A lower deposit rate can save on retained balances and lose money when customers leave and replacement funding costs more. I should be able to calculate an attrition break-even point, discuss the cohort exclusions and name the daily/account-level evidence needed for a real treasury decision.

## Verification and scope

Both projects have three distinct documented stages: pinned-source/data contracts; hand-worked and independently reconciled analytical tests; and fresh-process, isolated-directory reproducibility plus static-output review. Original government provenance and exact observation fingerprints are preserved; collection retrieves sources and generates full exports. SQL is executable, numerical exports are auditable and scenarios are explicitly hypothetical. The main figures were visually inspected. Interactive workbenches are generated for both projects. A separate GitHub CI job records three-engine desktop/mobile acceptance, including error states; no hosted deployment is claimed.

The root README, registry and GitHub CI include both cases. See each project's `verification.json`, `test_results.txt`, `CANDID_ASSESSMENT.md`, `ISSUES.md` and `VISUAL_REVIEW.md` for actual evidence and limitations. Publication is not evidence of employment tenure, measured business savings or guaranteed recruiting outcomes.
