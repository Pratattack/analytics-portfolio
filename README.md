# Analytics Portfolio

Industry-specific economics and business analytics cases by Prathamesh Singh, using Python and SQL with Excel-compatible outputs.

## Projects

| Date | Industry | Project |
|---|---|---|
| 2026-10-17 | Specialty chemicals | [Catalyst Pricing & Contract Economics](projects/2026-10-17/01-catalyst-commercial-economics/) |
| 2026-10-17 | Consumer credit cards | [Acquisition Economics & Experiment Measurement](projects/2026-10-17/02-card-acquisition-economics/) |
| 2026-10-17 | Electric utilities | [Grid Resilience Capital Allocation](projects/2026-10-17/03-grid-resilience-capital-allocation/) |

Read the [daily explanation](projects/2026-10-17/DAILY_BRIEF.md) and [verification evidence](projects/2026-10-17/verification.json).

Each case includes documented assumptions, Python pipeline, SQL analysis, clearly labeled inputs, CSV results, HTML report and tests. The first two cases use synthetic operational data. The grid-resilience case uses public EIA benchmarks with hypothetical investments and modeled outcomes; observed inputs and assumptions are separated. These are independent portfolio cases, not employer work or claims of professional tenure. Source publication is complete; reports are not hosted applications.

## Reproduce

Python 3.10+, standard library only. From `projects/2026-10-17`, run `python verify.py` for hand-worked tests, independent reconciliation and byte-identical clean regeneration. Each project's README includes individual run instructions.

For the grid-resilience case, run `python verify.py` from `projects/2026-10-17/03-grid-resilience-capital-allocation`. Its independent checks and explanations are in that project's directory.
