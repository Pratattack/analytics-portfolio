# Costco membership pricing and retention

**Decision.** What level of incremental paid-member attrition would erase the operating benefit of a fee increase?

Costco's FY2026 operating income rose $1,302 million. Merchandise gross profit contributed $2,942 million, membership fee revenue added $584 million, and higher SG&A absorbed $2,224 million. Under a modeled 5% fee increase, 80% realization, representative baskets and 25% avoidable SG&A, incremental attrition breaks even at 0.731%. At 1% attrition, the scenario is about $87 million below baseline operating income. A pricing pilot should measure paid renewal and merchandise contribution by cohort before a broad rollout.

## Evidence and assumptions

The two 52-week fiscal years ended August 31, 2025 and August 30, 2026. [Costco's FY2026 results](https://investor.costco.com/news/news-details/2026/Costco-Wholesale-Corporation-Reports-Fourth-Quarter-and-Fiscal-Year-2026-Operating-Results/) report both fiscal years in the consolidated statements of income. The six figures per year in `data/reported.csv` are manually transcribed in USD millions. The SQL checks independently reconcile sales and fees to total revenue and revenue less expenses to operating income.

The scenario applies an effective increase equal to the nominal price increase times assumed realization. Lost members reduce the fee base and merchandise contribution. Basket exposure scales the merchandise loss per point of attrition relative to the companywide baseline. We deduct the modeled avoidable portion of baseline SG&A from gross profit before converting merchant exposure into lost contribution. The 81 break-even cases and 486 stress cases cover three fee changes, three realization rates, three basket exposures, three SG&A flexibility assumptions and, for stress cases, six attrition rates.

The price and cost ranges are proposed pilot stresses. Aggregate public data cannot identify incremental churn, household spend, market or tier differences, cost allocation to the membership activity or demand elasticity. The historical bridge is an accounting identity. The threshold is a one-year static operating profit screen.

## Run

From this directory, run `python3 analyze.py`, then open [the decision brief](outputs/report.html) and inspect [the threshold table](outputs/frontier.csv). Keep the parent folder with the shared helper when cloning or copying the project. Run `python3 ../verify.py` for independent fixtures, data reconciliation and clean reproduction of both cases.
