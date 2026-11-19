# UPS network redesign savings hurdle

**Decision.** What steady quarterly savings would justify a network redesign if it also loses domestic package revenue?

In Q3 2026, UPS's domestic adjusted operating profit increased $129 million year over year, while consolidated adjusted operating profit fell $78 million. Nine-month consolidated adjusted operating profit fell $293 million. At an assumed 35% incremental contribution margin, losing 2.48% of the Q3 domestic revenue base would erase the domestic improvement. A hypothetical $150 million redesign with 2% recurring revenue leakage needs about $156 million of steady quarterly savings to clear an eight-quarter pre-tax break-even. The screen supports a limited lane pilot and independent verification of net savings and customer retention before a wider commitment.

## Evidence and assumptions

[UPS's October 27, 2026 earnings release filed as Exhibit 99.1](https://investors.ups.com/sec-filings/all-sec-filings/content/0001628280-26-067381/exhibit991-earningspressre.htm) reports the three- and nine-month consolidated reconciliations and the three-month U.S. Domestic Package reconciliation. `data/reported.csv` transcribes amounts in USD millions. Domestic transformation costs are preserved at the disclosed aggregate; the source does not split the domestic line across initiatives in this reconciliation. Blank revenue fields are unused; blank domestic network adjustment fields avoid duplicating those transformation costs. The signed adjustments include the gain on asset sales as a negative add-back.

The stress test uses Q3 domestic revenue as a flat scale and varies lost revenue, incremental contribution, implementation outlay and steady quarterly savings. Revenue loss starts in quarter one and persists. Savings ramp to 25%, 50%, 75%, then 100%. Cash effects are discounted at 2.5% per quarter and implementation cost is paid at time zero. The 63 threshold cases and 189 scenarios cover the specified ranges.

Adjusted profit is management’s non-GAAP measure. The reported expense bridge cannot identify savings caused by the program. The hypothetical cash case is incremental to holding the latest network in place. It excludes tax, working capital, seasonality, terminal value and any separately modeled capital spending beyond the upfront cash envelope. No assumption uses the disclosed accounting charges as a cash outlay.

## Run

From this directory, run `python3 analyze.py`, then open [the decision brief](outputs/report.html) and inspect [the savings frontier](outputs/savings_frontier.csv). Keep the parent folder with the shared helper when cloning or copying the project. Run `python3 ../verify.py` for independent fixtures, data reconciliation and clean reproduction of both cases.
