# Methods and data dictionary

## Decision and intended user

A restaurant corporate-finance committee needs to distinguish lease accounting from cash spending and identify earnings stresses that exceed assumed management-response capacity. The objective is to quantify the gap to a stated EBIT floor, then find the least assumed response-resource requirement within two bounded levers. This is a conditional diligence model, not a recommendation to cut staff, close restaurants, renegotiate rent or return capital.

## Public source and observation contract

Six listed operators: Darden (DRI), Texas Roadhouse (TXRH), Brinker (EAT), Bloomin' Brands (BLMN), Cheesecake Factory (CAKE), BJ's Restaurants (BJRI). Companyfacts sources and complete-original filing URLs, accessions, filing dates, hashes and source element positions are in `data/source_manifest.json`, `lineage.json` and `original_audit.json`.

The four USD measures must share issuer, annual start/end, 10-K accession and filing cutoff October 26, 2026. Annual durations must be 330–380 days. No value is carried forward. For each end date, choose the earliest eligible common accession present in the downloaded companyfacts response, with a documented revenue-tag preference. This is **earliest available selected disclosure**, not proof of the true original vintage for every historical year. Companyfacts is an as-served dataset; a comparison may first appear in a later filing. Numeric projections of the latest six complete original filings independently reconcile all 24 latest source values. Historical observations are source-linked companyfacts projections, not a complete-original historical audit.

Retained coverage is 32 issuer-years with ten missing issuer/calendar-end-year combinations in 2019–2025. `data/exclusions.json` lists them. The latest base is each issuer's FY ending in calendar 2025. DRI ends in May and EAT in June; the other selected issuers end in December. Summing them does not create a calendar-year portfolio statement. Period dates, consolidation, acquisitions, impairments, franchise shares and lease scopes constrain comparisons.

| Field | Definition and source |
|---|---|
| revenue | ASC 606 revenue excluding assessed tax, otherwise Revenues, otherwise SalesRevenueNet; actual tag retained |
| ebit | `OperatingIncomeLoss`; reported operating earnings, including D&A, leases and other operating items |
| lease_cost | `OperatingLeaseCost`; operating lease expense, not all occupancy costs or necessarily variable/short-term lease cost |
| lease_cash | `OperatingLeasePayments`; reported operating lease payments, not an expense substitute |
| rent_only_earnings_cover | (EBIT + operating lease expense) / operating lease expense; diagnostic only, not EBITDA, EBITDAR or a contractual fixed-charge ratio |
| lease_cash_minus_cost | Payments less expense; timing/scope diagnostic, not incremental cash savings |

Companyfacts entity-wide values are used; the latest filing check requires dimensionless USD contexts. Actual report end dates are used instead of trusting inconsistent `fy` labels. No all-store unit economics or maintenance-capex split is observed.

## Earnings stress and no double counting

Let R be reported revenue, E reported EBIT, L operating lease expense, s assumed lost-sales fraction, m lost-sales contribution margin **after avoided variable costs**, e incremental lease escalation, and f the target EBIT/base-revenue floor.

E_stress = E − R × s × m − L × e.
Gap = max(0, f × R − E_stress).

E already includes base rent. Deducting L again would double count it. The model subtracts only incremental escalation. The contribution margin is an assumption, not estimated causal cost flexibility. There is no claim that 35% is an issuer's actual marginal margin. Historical adjacent-year revenue/EBIT changes are exposed as challenges; accounting changes, acquisitions and pandemic restrictions prevent treating their ratio as an identified elasticity.

## Conditional response frontier

x denotes incremental cost savings (EBIT benefit dollar-for-dollar). y denotes recovered lost sales (EBIT benefit m×y). Caps are x ≤ c×R and y ≤ a×s×R. The reference settings are c=2% and a=50%; neither is an observed execution capacity. Minimize 0.5×x + 0.15×y subject to x+m×y ≥ Gap and nonnegative bounded levers. The objective weights are assumed one-period implementation resources, not disclosed corporate costs. They are not deducted again from the earnings equation: net-of-one-off-cost approval would require another model.

The exact solver fills the lever with lower resource cost per EBIT dollar first. A separate SciPy/HiGHS LP independently checks every scenario; explicit 2D vertex enumeration and hand calculations check the method. Feasibility depends on the caps and floor, not numerical optimism. Infeasible rows retain null plan values and the remaining gap rather than inventing more capacity.

The 216 reference cases span sales declines 5/10/20%, margins 20/35/50%, lease escalation 0/10%, and EBIT floors 0/3% across six issuers. Seventy-two additional cap/recovery sensitivities challenge a 20% decline, 35% margin, 10% escalation and 3% floor. These are a scenario grid, not a probability distribution or expected loss. The observed EBIT and lease facts are dated; no current treasury gap, liquidity cushion, covenant headroom or achieved savings is estimated.

## Required diligence before adoption

Obtain store-level contribution margins, lease renewal/reset terms, implementation costs, service/safety constraints, sales-recovery evidence, current cash forecasts and lender definitions. Reconcile scope changes and assess whether assumed savings can be executed without reducing sales or quality. External operator, lender and accounting-policy validation remain outstanding.
