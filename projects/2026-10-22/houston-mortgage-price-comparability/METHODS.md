# Methods, target population and assumptions

## Business question and observation contract

Can a mortgage research team compare historical lender pricing on a common set of public product/risk characteristics before deciding which contemporaneous quotes to collect? This is a descriptive common-support analysis, not a credit decision, discrimination test or causal lender-effect estimator.

The official HMDA Data Browser query restricts MSA/MD 26420 (Houston area), activity year 2025 and action taken 1 (originated). It returned 123,445 rows. A separately requested API aggregation reconciles both row count and total loan amount. Source identity is the original response's CSV row number; repeated public rows are retained because public rounding does not justify deduplication. A lossless 31-field financial/product projection omits borrower demographics. Original and projected hashes, compressed part hashes, query and retrieval date are pinned. The as-served October 22, 2026 response is not claimed to be available on a particular date in 2025 or identical to the initial June release. Recollection fails on vintage drift.

## Fixed eligibility and exclusions

The sequence is product → numeric completeness → plausible analytical domain. `exclusion_flow.csv` records passed and first-excluded counts so every source row is accounted for once.

Require conventional, first lien, home purchase, owner occupied, site built, exactly one unit, conforming limit flag C, 360-month term, intro-rate period NA; no reverse mortgage, open credit line, business purpose, negative amortization, interest-only, balloon or other nonamortizing feature (all no flags are code 2). This is a fixed-rate-like product restriction based on public fields, not an independent contract audit.

Require numeric rounded loan amount, API `loan_to_value_ratio` (the combined debt-to-property ratio), note rate, APR spread and gross total loan costs; known DTI band; tract available. Restrict loan amount to $8 0,000–$1,0 00,000, CLTV to (0,110], note rate to (0,20] percent, APR spread to [−5,10] percentage points and gross loan costs to [0,1 00,000] dollars. These are transparent research bounds, not lender underwriting rules. Do not impute missing/exempt pricing as zero. DTI above 60%, missing/exempt DTI and incomplete pricing are excluded. Domain restrictions may remove legitimate loans and constrain generalizability.

## Outcome and exact overlap target

Primary outcome is `rate_spread`, APR minus the applicable APOR. Its benchmark incorporates pricing-date market conditions; the public file does not reveal the exact lock date, and the benchmark cannot resolve intra-product selection or concessions. Secondary outcome is gross total loan costs divided by rounded loan amount, in basis points. Gross costs exclude any assumed credit offset. Discount points and lender credits are preserved in source data but missing fields are never interpreted as zero. APR already reflects relevant charges; gross costs are a separate diagnostic, not added again to APR.

Freeze the five largest eligible lenders by counts, with LEI tie-break, without inspecting pricing outcomes. All five use the same target. Base cells cross:

- Loan amount: <250k, [250k,400k), [400k,600k), ≥600k.
- CLTV: ≤80, (80,90], (90,95], >95.
- DTI: reported below 36%; exact 36–42; exact 43–49; reported 50–60%.
- County: Harris FIPS48201 versus other Houston-area counties.

Retain a cell only if every selected lender has at least ten eligible loans. Let n(l,c) be counts, m(c)=min_l n(l,c), and target w(c)=m(c)/sum_c m(c). The standardized lender mean is sum_c w(c)×mean(y|l,c). This fixes a common overlap population; it does not reweight to all Houston borrowers. We publish every lender-cell operand, target weight, count, sum and mean. `eligible.csv` provides row-level source lineage and derived cells. SQL independently computes cell statistics. Independent verification joins those records to target weights and reconciles published standardized means.

At the base contract, 18 shared cells retain 3,867 of 9,344 selected-lender eligible loans (41.38%). The remaining 2 2,751 eligible loans are from lenders outside the fixed five. No estimates are reported for an empty intersection. The application exposes a recoverable empty search state and missing-record fixture; no synthetic loans are inserted into the empirical results.

## Stability and sensitivity

The 400-replicate seeded analysis draws one positive Exp(1) multiplier per census tract and replicate. All loans in that tract share it, across lenders and cells. Each lender-cell outcome is recomputed using those multipliers; **cell support and target weights remain fixed**. The 2.5th/97.5th percentiles describe sensitivity to geographic cluster reweighting. They are not causal confidence intervals, uncertainty over the complete origination population, model-risk bounds or an estimate of measurement-error coverage. Positive weights avoid empty-cell bootstrap artifacts, but ignore uncertainty in selecting support. Seed=20261022; cluster universe=1,044. Pairwise differences use the same draws, not independent lender bands; `pair_stability.csv` records them.

A frozen six-case design crosses minimum cell counts 5/10/20 and base/finer grids. The finer grid adds loan-amount cutoffs 200k/300k/400k/600k and CLTV cutoffs 70/80/90/95. Lenders remain fixed. These variants change the target population and cannot be treated as repeated estimates of an identical causal parameter. Base shared-cell counts change 35→18→5 as minimum counts rise. CMG versus Rocket ordering is sensitive at the strict threshold; do not overstate a stable overall ranking. No tuning chooses the most favorable lender result.

## Separate hypothetical offer workflow

Controls are assumptions: common principal P, annual nominal note rates rA/rB, upfront fee totals FA/FB, whole holding months H≤360, annual nominal discount rate d. No control is populated from lender outcomes. Monthly rate i=r/12; payment M=P i/[1−(1+i)^−360], or P/360 at zero. End balance B(H)=P(1+i)^H−M[(1+i)^H−1]/i (implemented as a monthly ledger). Present cost is F+sum(t=1..H) M/(1+d/12)^t+B(H)/(1+d/12)^H. Common initial proceeds cancel in A−B. Including the exit balance prevents a lower-payment, slower-amortizing loan from looking artificially cheap.

Fee assumptions are paid upfront, not financed. Excludes taxes, insurance, escrow timing, points tax treatment, prepayment penalties, refinancing options, default and different product terms. The comparison is only meaningful for actual offers with aligned principal and term. It is not APR computation. Browser tests reconcile against a separately implemented payment/balance schedule, including a zero-rate case and invalid fractional months.

## Adoption gate and decision constraints

The adoption gate is false for automatic lender recommendations. Missing credit scores, channels, exact dates, relationships, seller incentives and shopping alternatives can explain the large gaps; matching does not solve unobserved confounding. A builder-affiliated lender's incentives may change the total home-plus-mortgage transaction. Obtain comparable dated Loan Estimates, documented points/credits and channel information before recommending a financing choice. For a fair-lending study, commission an appropriate protected-class, underwriting and legal review; this financial projection is not designed for it.
