# Proposed portfolio case study: United Rentals

## How much can United Rentals return after funding its fleet?

The base scenario supports $597m of first-period repurchases against an illustrative $1,500m ceiling. Equipment investment and working capital absorb cash even as modeled revenue grows.

**Who it helps:** A financial analyst evaluating capital allocation, cash requirements and downside resilience.

**Evidence:** Three years of reported statements, latest quarterly comparatives, dated share count and a corroborated closing price. Five-year projections are labeled scenarios.

**What I built:** An integrated Excel model with operating drivers, three statements, a financing waterfall, DCF, reverse valuation and two-input sensitivities. Python reproduces the analysis. SQL reconciles reported financial statements.

**Finding:** Investment determines the distribution budget. Operating cash of $5,430m less net investing outflow of $4,336m leaves $1,094m. With opening cash of $153m, a $150m reserve and a $500m dividend budget, repurchases fall to $597m.

**Why it matters:** Use a cash waterfall to set repurchase capacity after fleet investment, required principal funding and a cash reserve. Revisit the budget when fleet yield, used-equipment proceeds or receivable days change. The scenario is not a proposed board authorization.

**Limitation:** The most consequential operating choice is the fleet cohort approximation: a legacy depreciation rate, half-year depreciation on new purchases and assumed disposal ages connect investment to fleet capacity and earnings. Exact asset cohorts and utilization are unavailable. Gross fleet starts at a rounded $25bn, so small changes should not be interpreted as precise capacity estimates. The strongest argument against the low DCF indication is that future fleet productivity, acquisition benefits or sustainable returns could be stronger than this deliberately simplified build captures. Conversely, recent cash conversion may not persist. Terminal value contributes 74.9% of base enterprise value. Changing discount rates and terminal reinvestment can dominate the apparent gap to price.

**Downloadable, offline project:** Excel workbook, executive memo, five-minute presentation, data, methods and code. No hosted application is claimed. Published as independent portfolio research.
