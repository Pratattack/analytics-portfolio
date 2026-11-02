# United Rentals: research and model notes

Research cutoff: 2 November 2026. Market price cutoff: 30 October 2026.

## Decision and business economics

Use a cash waterfall to set repurchase capacity after fleet investment, required principal funding and a cash reserve. Revisit the budget when fleet yield, used-equipment proceeds or receivable days change. The scenario is not a proposed board authorization.

United Rentals rents owned equipment and provides related services. Rental yield, average equipment cost, disposal economics and reinvestment determine cash conversion. Its annual report describes a fragmented market with local, regional and national competitors and equipment vendors that sell and rent. Scale can aid purchasing and fleet transfers, but it does not eliminate rate, utilization or resale risk. General and specialty equipment have different economics. This model separates owned rental revenue from ancillary rental and equipment sales, but does not claim a fully disclosed segment utilization model. Public evidence is adequate for a conditional capital-allocation analysis, not an exact fleet-cohort forecast.

## Historical bridge

Annual 2023, 2024 and 2025 figures are taken from the downloaded annual filings. Comparative nine-month 2025 and nine-month 2026 flows use the latest quarterly filing. LTM = annual 2025 + nine-month 2026 - nine-month 2025. Balance-sheet stocks use dated balances, never this flow formula. Restated comparative values are preferred where present. Missing data remain missing unless a zero is explicitly disclosed. Each selected numeric fact has a context, dimension, source ID and source hash in source_lineage.csv. Annual and September-ending forecast dates are deliberately different.

The workbook adds reported impairment back to historical recurring operating income where available, while showing the charge and reported operating income separately. This is an analytical reconciliation. It does not imply the loss was harmless. Crocs FY2025 reported net loss and unusual tax history remain visible. Historical EPS is omitted rather than approximated using period-end shares.

## Assumptions and conflicting evidence

The most consequential operating choice is the fleet cohort approximation: a legacy depreciation rate, half-year depreciation on new purchases and assumed disposal ages connect investment to fleet capacity and earnings. Exact asset cohorts and utilization are unavailable. Gross fleet starts at a rounded $25bn, so small changes should not be interpreted as precise capacity estimates.

Base is a modeling reference, not a probability-weighted expected outcome. Growth and contribution margins are analyst scenarios bounded by downside and upside inputs. Management guidance informed the first investment budget only and is not relabeled as guidance for a September-ending forecast year. Historical strength supports testing continued cash generation. Cyclicality, competitive pricing, investment needs and incomplete cost disclosures support the downside. The result is deliberately conditional.

- **tax**: base [0.25, 0.25, 0.25, 0.25, 0.25]; downside [0.25, 0.25, 0.25, 0.25, 0.25]; upside [0.25, 0.25, 0.25, 0.25, 0.25]. Analyst normalized cash tax rate. No immediate cash refunds for losses.
- **interest**: base [0.055, 0.055, 0.055, 0.055, 0.055]; downside [0.075, 0.075, 0.075, 0.075, 0.075]; upside [0.05, 0.05, 0.05, 0.05, 0.05]. Analyst blended financing cost. Interest uses opening debt, with year-end financing timing.
- **dso**: base [64.58847736625515, 64.58847736625515, 64.58847736625515, 64.58847736625515, 64.58847736625515]; downside [72.58847736625515, 72.58847736625515, 72.58847736625515, 72.58847736625515, 72.58847736625515]; upside [61.58847736625515, 61.58847736625515, 61.58847736625515, 61.58847736625515, 61.58847736625515]. Latest receivables / trailing revenue x 365. Scenario changes are assumptions.
- **dio**: base [10.71817243643869, 10.71817243643869, 10.71817243643869, 10.71817243643869, 10.71817243643869]; downside [25.718172436438692, 25.718172436438692, 25.718172436438692, 25.718172436438692, 25.718172436438692]; upside [7.7181724364386906, 7.7181724364386906, 7.7181724364386906, 7.7181724364386906, 7.7181724364386906]. Latest inventory / trailing reported cost of revenue x 365; forecast cost denominator excludes D&A and disposal book cost.
- **dpo**: base [57.73430903461863, 57.73430903461863, 57.73430903461863, 57.73430903461863, 57.73430903461863]; downside [52.73430903461863, 52.73430903461863, 52.73430903461863, 52.73430903461863, 52.73430903461863]; upside [60.73430903461863, 60.73430903461863, 60.73430903461863, 60.73430903461863, 60.73430903461863]. Latest payables / trailing reported cost of revenue x 365; forecast denominator follows forecast operating costs.
- **sbc**: base [0.008802011888431641, 0.008802011888431641, 0.008802011888431641, 0.008802011888431641, 0.008802011888431641]; downside [0.008802011888431641, 0.008802011888431641, 0.008802011888431641, 0.008802011888431641, 0.008802011888431641]; upside [0.008802011888431641, 0.008802011888431641, 0.008802011888431641, 0.008802011888431641, 0.008802011888431641]. Trailing reported stock compensation / revenue. Economic expense retained in DCF.
- **repurchases**: base [1500, 1500, 1500, 1500, 1500]; downside [750, 750, 750, 750, 750]; upside [2000, 2000, 2000, 2000, 2000]. Hypothetical annual repurchase ceiling, funded only after minimum cash and dividends.
- **dividends**: base [500, 500, 500, 500, 500]; downside [500, 500, 500, 500, 500]; upside [550, 550, 550, 550, 550]. Analyst distribution budget; not a future board declaration.
- **debt_sweep**: base [0.5, 0.5, 0.5, 0.5, 0.5]; downside [1, 1, 1, 1, 1]; upside [0.5, 0.5, 0.5, 0.5, 0.5]. Fraction of remaining surplus directed to debt after the repurchase ceiling.
- **refinance**: base [1, 1, 1, 1, 1]; downside [0.75, 0.75, 0.75, 0.75, 0.75]; upside [1, 1, 1, 1, 1]. Hypothetical fraction of the repayment budget refinanced. Borrowing availability is not assured.
- **principal**: base [1607.0, 800, 1500, 1500, 3000]; downside [1607.0, 800, 1500, 1500, 3000]; upside [1607.0, 800, 1500, 1500, 3000]. Repayment stress budget, not an instrument-level contractual maturity schedule. Year one uses latest current debt if disclosed; later years are analyst assumptions.
- **impairment**: base [0, 0, 0, 0, 0]; downside [0, 0, 0, 0, 0]; upside [0, 0, 0, 0, 0]. Hypothetical noncash, nondeductible brand impairment. No forecast of an actual charge.
- **productivity**: base [0.03, 0.025, 0.02, 0.02, 0.02]; downside [-0.08, -0.04, 0, 0.01, 0.02]; upside [0.06, 0.05, 0.04, 0.03, 0.025]. Assumed change in rental yield after average OEC growth. Historical company productivity includes rate, time utilization and mix, not separately identifiable.
- **fleet_capex**: base [5350, 5200, 5200, 5300, 5400]; downside [4000, 3500, 3500, 4000, 4300]; upside [6000, 6300, 6600, 6900, 7200]. Cash fleet-purchase budget. First year is calibrated to 2026 cash-purchase guidance, not management guidance for these September-ending forecast periods.
- **other_capex**: base [400, 400, 400, 400, 400]; downside [300, 300, 300, 300, 300]; upside [450, 450, 450, 450, 450]. Analyst cash investment in non-rental PPE; no future acquisition or intangible capitalization assumed.
- **disposal_book_rate**: base [0.04187768883080107, 0.04187768883080107, 0.04187768883080107, 0.04187768883080107, 0.04187768883080107]; downside [0.055, 0.055, 0.055, 0.055, 0.055]; upside [0.04, 0.04, 0.04, 0.04, 0.04]. Book value removed / opening net fleet. Base calibrated to trailing disposal proceeds less gains divided by latest net fleet.
- **disposal_accum**: base [0.75, 0.75, 0.75, 0.75, 0.75]; downside [0.75, 0.75, 0.75, 0.75, 0.75]; upside [0.75, 0.75, 0.75, 0.75, 0.75]. Analyst accumulated depreciation fraction on disposed original cost. Not disclosed by cohort.
- **sale_multiple**: base [1.8387516254876464, 1.8387516254876464, 1.8387516254876464, 1.8387516254876464, 1.8387516254876464]; downside [1.25, 1.25, 1.25, 1.25, 1.25]; upside [1.9, 1.9, 1.9, 1.9, 1.9]. Disposal proceeds / disposed net book value. Base trailing ratio, not an asset-level resale forecast.
- **legacy_dep**: base [0.1538419648205631, 0.1538419648205631, 0.1538419648205631, 0.1538419648205631, 0.1538419648205631]; downside [0.1538419648205631, 0.1538419648205631, 0.1538419648205631, 0.1538419648205631, 0.1538419648205631]; upside [0.1538419648205631, 0.1538419648205631, 0.1538419648205631, 0.1538419648205631, 0.1538419648205631]. Legacy annual depreciation rate on opening net book fleet. Cohort approximation calibrated to trailing D&A.
- **cost_inflation**: base [0.03, 0.03, 0.03, 0.03, 0.03]; downside [0.04, 0.04, 0.04, 0.04, 0.04]; upside [0.025, 0.025, 0.025, 0.025, 0.025]. Assumed inflation in the fixed 40% of rental operating costs.
- **maintenance**: base [0, 0, 0, 0, 0]; downside [0.02, 0.02, 0.02, 0.02, 0.02]; upside [0, 0, 0, 0, 0]. Additional rental operating cost as a revenue share. Scenario assumption; no estimated causal capex-to-maintenance relationship.
- **other_growth**: base [0.03, 0.03, 0.03, 0.03, 0.03]; downside [-0.05, 0, 0.02, 0.02, 0.02]; upside [0.05, 0.05, 0.05, 0.05, 0.05]. Growth in ancillary rental revenue and other non-rental revenue.
- **sga_rate**: base [0.10602423411065387, 0.10602423411065387, 0.10602423411065387, 0.10602423411065387, 0.10602423411065387]; downside [0.11602423411065386, 0.11602423411065386, 0.11602423411065386, 0.11602423411065386, 0.11602423411065386]; upside [0.10302423411065387, 0.10302423411065387, 0.10302423411065387, 0.10302423411065387, 0.10302423411065387]. Reported trailing SG&A / revenue, including stock compensation.

## Valuation and reverse valuation

DCF discounts unlevered cash flow after stock compensation expense. Terminal reinvestment = terminal growth / terminal ROIC. Base WACC is 10%, terminal growth 2.5%, and terminal ROIC 10%. These are analyst hurdle assumptions, not a precisely estimated CAPM. The workbook exposes WACC/growth sensitivity. Reverse valuation fixes the explicit cash flows and solves the terminal EBIT margin needed to reconcile enterprise value to price times cover-page shares plus September net debt. The answer is conditional on this exact setup. It does not identify a unique market forecast.

The strongest argument against the low DCF indication is that future fleet productivity, acquisition benefits or sustainable returns could be stronger than this deliberately simplified build captures. Conversely, recent cash conversion may not persist. Terminal value contributes 74.9% of base enterprise value. Changing discount rates and terminal reinvestment can dominate the apparent gap to price.

## Model mechanics and reviewer concerns

The base cash-only threshold is about $9,527m of EBITDA to fund the full $1,500m repurchase ceiling while holding working capital, asset sales and capex unchanged. This is a local cash stress calculation, not a realistic standalone operating forecast. A durable improvement in yield or a defensible reduction in investment would change the allocation conclusion.

New borrowing is an explicit funding need when cash is insufficient, not evidence that a lender will fund it. Financing interest starts in the following year. Repayment budgets after the initial current-debt amount are assumptions, not security-level maturities. The cash reserve is an analyst policy, not a covenant. Other balance-sheet items remain constant, limiting deferred-tax, lease and pension detail. Forecast FX is zero. No future acquisitions are assumed. Dividend and repurchase ceilings are illustrative. The two-input repurchase table changes only the first operating shock and capex multiplier, so it is a local sensitivity, not a full downside case. The cash-only EBITDA threshold freezes the other cash drivers. Equal-month valuation proration is a material timing simplification for seasonal businesses.

## Decision evidence to request

Asset-level depreciation and disposal cohorts, owned-fleet utilization by category, rental rate versus mix, maintenance spending and an instrument-level debt maturity schedule would most improve the model.

## Reproduction and checks

Run src/model.py, then src/validate.py. The latter tests all case balance sheets and cash closes, the cash distribution cap, impairment tax/cash behavior, a financing shortfall, later-driver propagation, valuation monotonicity and invalid discount rates. SQLite checks independently reconcile reported balance sheets and cash changes. The Excel builder tests all five forecasts against Python for each case, changes a later driver and compares native two-input Data Table cells with direct recalculation. Excel desktop and PowerPoint desktop were not available for manual application testing.

The Excel builder requires @oai/artifact-tool. Numeric model reproduction requires only Python standard library plus lxml for source re-extraction. Chart recreation additionally requires matplotlib. Selected input snapshots are distributed. Full filing HTML is not redistributed in this package. Re-download using filing_manifest.json and verify hashes before running extract.py and prepare.py. SEC may restrict automated requests, so use a descriptive user-agent and honor rate limits.

## Additional company context sources

- [Q3 2026 earnings presentation](https://s21.q4cdn.com/336331232/files/doc_earnings/2026/q3/presentation/Third-Quarter-2026-Investor-Presentation.pdf). Management presentation or release, distinct from the SEC statement facts.
- [Q3 2026 earnings release](https://investors.unitedrentals.com/press-releases/press-releases-details/2026/United-Rentals-Announces-Record-Third-Quarter-Results-and-Raises-Full-Year-2026-Guidance/default.aspx). Management presentation or release, distinct from the SEC statement facts.
