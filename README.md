# Analytics Portfolio

## Featured research prototype

**[Utility Reliability Due Diligence Lab](flagships/utility-reliability-due-diligence/)** upgrades the earlier resilience exercise with six official utility-level workbooks, source-cell lineage, report-year validation, utility-cluster uncertainty, release quarantine and an offline analyst workbench. It is a research prototype with explicit open evidence issues, not a production or employment-experience claim. Start with its README and CANDID_ASSESSMENT.md.

[Portfolio quality standard](QUALITY_STANDARD.md)

October 20 update: the featured utility workbench now has keyboard utility selection, consistent API/offline scenario boundaries, stale-response protection and visible recoverable API errors. A dedicated browser acceptance job checks both deliveries across three engines and desktop/mobile viewports; its actual CI result and commit-specific evidence release are the verification record. This is an upgrade to the featured research prototype, not a new research project.

The October 19 projects' CI restores their immutable original official-data snapshot and rechecks archive, member and observation fingerprints. This keeps the published research reproducible when an official source URL is unavailable; it does not claim a fresh data vintage. See [data restoration instructions](projects/2026-10-19/DATA_REPRODUCTION.md).


Industry-specific economics and business analytics cases by Prathamesh Singh, using Python and SQL with Excel-compatible outputs.

## Projects

| Date | Industry | Project |
|---|---|---|
| 2026-10-17 | Specialty chemicals | [Catalyst Pricing & Contract Economics](projects/2026-10-17/01-catalyst-commercial-economics/) |
| 2026-10-17 | Consumer credit cards | [Acquisition Economics & Experiment Measurement](projects/2026-10-17/02-card-acquisition-economics/) |
| 2026-10-17 | Electric utilities | [Grid Resilience Capital Allocation](projects/2026-10-17/03-grid-resilience-capital-allocation/) |
| 2026-10-18 | Healthcare operations | [Outpatient Access & Capacity Simulation](projects/2026-10-18/01-outpatient-access-simulation/) |
| 2026-10-18 | Urban mobility | [Demand Forecasting & Capacity Economics](projects/2026-10-18/02-bike-share-forecast-planning/) |
| 2026-10-19 | US passenger airlines | [Airline Delay Intervention Screen](projects/2026-10-19/airline-delay-intervention-screen/) |
| 2026-10-19 | Insured domestic banking | [Bank Deposit Cost Attribution](projects/2026-10-19/bank-deposit-cost-attribution/) |
| 2026-10-20 | Property/casualty insurance | [Insurance Reserve Challenge Lab](projects/2026-10-20/insurance-reserve-capital-review/) |
| 2026-10-20 | Listed retail-property REITs | [Retail REIT Refinancing Resilience](projects/2026-10-20/retail-reit-refinancing-review/) |
| 2026-10-21 | Semiconductor manufacturing equipment | [Inventory Funding & Forecast Governance](projects/2026-10-21/semiconductor-inventory-funding/) |
| 2026-10-21 | US listed freight railroads | [Reinvestment & Cash Return Review](projects/2026-10-21/freight-rail-capital-review/) |
| 2026-10-22 | Residential homebuilding | [Homebuilder Land Option Diligence](projects/2026-10-22/homebuilder-land-option-diligence/) |
| 2026-10-22 | Hotel management and franchising | [Hotel Reimbursement Economics](projects/2026-10-22/hotel-reimbursement-economics/) |
| 2026-10-22 | Residential mortgage origination | [Houston Mortgage Price Comparability](projects/2026-10-22/houston-mortgage-price-comparability/) |
| 2026-10-22 | Upstream oil and gas | [Retirement Obligation Review](projects/2026-10-22/upstream-retirement-obligation-review/) |

Read the [October 19 research brief](projects/2026-10-19/DAILY_BRIEF.md), [October 19 role/source research](projects/2026-10-19/RESEARCH.md), [October 18 explanation](projects/2026-10-18/DAILY_BRIEF.md), [October 18 verification](projects/2026-10-18/verification.json), or [October 17 explanation](projects/2026-10-17/DAILY_BRIEF.md).

Each case includes documented assumptions, Python pipeline, SQL analysis, clearly labeled inputs, CSV results, HTML report and tests. Chemicals, credit cards and outpatient operations use synthetic operational data. Grid resilience uses EIA benchmarks with hypothetical investments. Mobility forecasting uses public historical UCI rental observations with hypothetical capacity costs. Observed inputs, assumptions and modeled outcomes are explicitly separated. These are independent portfolio cases, not employer work or claims of professional tenure. Source publication is complete; reports are not hosted applications.

## Reproduce

For the October 17 cases: Python 3.10+, standard library only. From `projects/2026-10-17`, run `python verify.py` for hand-worked tests, independent reconciliation and byte-identical clean regeneration. Each project's README includes individual run instructions.

For the grid-resilience case, run `python verify.py` from `projects/2026-10-17/03-grid-resilience-capital-allocation`. Its independent checks and explanations are in that project's directory.

For both October 18 cases, run `python verify_all.py` from `projects/2026-10-18`.

## October 19 empirical research

The airline case audits 60,093 official carrier-airport-month rows and tests a fixed, constrained investigation queue across later periods. The bank case audits 48,814 FDIC bank-quarters and decomposes a fixed cohort’s deposit-expense change into volume, mix and proxy-rate effects. Both preserve source provenance and observation fingerprints, exclusions, independent reconciliations, interactive workbenches and static reports. They are research prototypes; the airline screen is not a causal intervention estimate, and the banking rate is an endpoint-average proxy. Static figures were visually inspected; a separate CI job records three-engine desktop/mobile report and application acceptance.

For these cases, Python 3.12 is recommended. Install `projects/2026-10-19/requirements.txt` and run `python projects/2026-10-19/verify_all.py`. Each project’s README documents shared parent files and exact run instructions.

## October 20 finance diligence research

The [insurance reserve case](projects/2026-10-20/insurance-reserve-capital-review/) extracts 4,046 paid/incurred accident-year cells from original SEC inline-XBRL and retains 31 of 48 triangles for transparent development diagnostics. Masked-diagonal WAPE is 14.54% versus 44.50% for a simple baseline, but the historical cells are from current disclosures and tail sensitivity prevents reserve-release authorization. The [retail REIT case](projects/2026-10-20/retail-reit-refinancing-review/) reconciles $53.25B of disclosed face principal, solves five-year cash-floor / rollover constraints, and retains 37 infeasible cases in a 90-scenario persistent-shock grid. Those are conditional modeled gaps, not current financing needs.

Both use original-source numerical snapshots with pinned provenance, source-pointer audits, SQL reconciliations, independent analytical checks, deterministic rebuilds, executive briefs and offline interactive workbenches. Read the [shared reproduction and verification guide](projects/2026-10-20/), [primary-source / role research](projects/2026-10-20/RESEARCH.md), and each project's candid assessment. Actual browser evidence comes from the separate 24-case CI job and commit-specific release. These are independent research prototypes, not actuarial opinions, lender approvals or claims of professional tenure.

## October 21 finance evidence and capital decisions

The [semiconductor-equipment inventory case](projects/2026-10-21/semiconductor-inventory-funding/) reconstructs 332 issuer-quarters and uses actual filing-label timing for 47 later forecast outcomes. The candidate loses to the last-balance baseline (3.03% vs 2.62% WAPE); model promotion fails, and two of six issuers have stale/gapped current inputs. The [freight rail capital review](projects/2026-10-21/freight-rail-capital-review/) reconciles 32 issuer-years, with a coherent FY2025 CFO/capex/cash-return residual of −$665M, reverse cash-flow stress, three-year coverage and explicit finance-lease asset scope. It does not identify the financing of repurchases or authorize capex cuts.

Both pin SEC numerical observations and original-filing numeric cells, retain source pointers and exclusions, independently reconcile methods, and provide visual reports, offline analyst workbenches, executive briefs, measured resume bullets and five answered interview questions. Read the [shared setup and verification guide](projects/2026-10-21/), [source/role research](projects/2026-10-21/RESEARCH.md) and project assessments. The dedicated capital-research workflow records analytical/reproducibility checks and actual 24-case three-engine desktop/mobile browser acceptance. Source publication is not hosted application delivery; procurement, treasury, safety and physical-device validation remain unavailable.

## October 22 industry finance decisions

The [homebuilder land-contract case](projects/2026-10-22/homebuilder-land-option-diligence/) reconciles 74 scoped observations from 24 original filings and distinguishes $1.613B in disclosed mixed-basis costs from $13.711B in conditional remaining purchase prices. It exposes a balance-sheet scope trap and legacy-tag reuse, then compares immediate acquisition/abandonment with explicitly assumed extension scenarios. No land option appraisal or issuer-specific acquisition recommendation is claimed.

The [hotel reimbursement case](projects/2026-10-22/hotel-reimbursement-economics/) reconciles 34 periods from 12 original filings, with exact reported-income and year-over-year bridges. H1 2026 includes $13.926B reimbursement revenue and a −$326.224M accrual reimbursement balance. Its program-budget frontier is conditional, not a cash forecast or pure-fee profitability estimate.

Both include original numerical source snapshots, exact lineage, source precision/scope audits, meaningful SQL, independent analytical reconciliation, clean deterministic reproduction, executive briefs, self-contained offline applications, measured resume bullets and five answered interview questions. The dedicated industry-finance workflow runs actual three-engine desktop/mobile acceptance and publishes exact-commit screenshot evidence. Read the [setup and verification guide](projects/2026-10-22/), [primary-source/role research](projects/2026-10-22/RESEARCH.md) and each candid assessment. Their mathematical decision layers are deliberately transparent; source volume and test counts do not claim equivalence to a professional engagement.

## Mortgage pricing and upstream liability research

The [Houston mortgage case](projects/2026-10-22/houston-mortgage-price-comparability/) audits123,445 official 2025 originations and defines a fixed five-lender common-support population. Its3,867 matched loans expose limited overlap; APR-spread comparisons are descriptive and do not identify causal lender effects. The separate offline offer calculator includes fees, amortization and exit balances.

The [upstream retirement case](projects/2026-10-22/upstream-retirement-obligation-review/) reconstructs35 liability ledgers from17 original SEC filings and separates cash spending from liability removals. Constrained timing bounds show what additional assumptions are needed to translate book values into hypothetical cash equivalents; reserve approval remains withheld. Both cases include original-source audits, independent reconciliations, pinned dependencies, clean reproduction, executive briefs, measured resume bullets and interview defenses. These research prototypes do not imply employer work, guaranteed outcomes or years of tenure.

Install `projects/2026-10-22/energy-mortgage-toolkit/requirements.txt` under Python3.12 and run that directory's `verify.py`. [Setup, actual browser testing and source recollection](projects/2026-10-22/energy-mortgage-toolkit/) explain the three gates and commit-specific CI screenshot evidence. Reports/workbenches run locally/offline; source publication does not host a live application.


## October 26: credit model governance and restaurant operating leverage

- [Credit Spread Recession Signal Audit](projects/2026-10-26/credit-spread-recession-audit/): 648 research-panel months and 192 held-out origins. The credit model beats the curve model but loses to the unconditional baseline; model promotion is withheld. Includes prior-month features, label embargoes, paired block sensitivity, model-review workbench and interview materials.
- [Restaurant Lease & Operating Leverage Review](projects/2026-10-26/restaurant-lease-operating-leverage/): 32 issuer-years, 24 original-source cells, 216 independently reconciled stress cases and 72 sensitivities. Thirty-two conditional cases remain infeasible. Earnings stress avoids double-counting base rent; assumptions do not establish savings or liquidity needs.

Both include offline applications, executive briefs, source lineage, setup instructions and executed Chromium screenshots. Full three-engine desktop/mobile acceptance is tracked by [the finance workflow](.github/workflows/oct26-finance.yml); successful main runs publish a commit-specific `finance-2026-10-26-<commit>` evidence release. Applications are local research prototypes, not hosted services.


## New research, October 27, 2026

- [Real Wages & Payroll Budget Tradeoffs](projects/2026-10-27/real-wage-payroll-budget): BLS pay, hours and CPI with explicit missing-data treatment.
- [Diesel Fuel Budget Risk](projects/2026-10-27/diesel-budget-risk): EIA prices and an honest holdout comparison of quarterly reserve rules.

Each project includes pinned raw data, source hashes, reproducible Python, SQL reconciliation, SVG charts, a report and a browser-local scenario workbench.


## Fuel Retail Investment Decision Lab

[Anonymized scenario underwriting](projects/2026-10-28/fuel-retail-investment-lab) reconciles report estimates, models staged construction funding, and separates debt coverage from unresolved site evidence. Original private attachments and identifying details are excluded.
