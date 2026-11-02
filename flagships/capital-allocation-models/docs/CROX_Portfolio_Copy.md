# Proposed portfolio case study: Crocs

## Can Crocs fund buybacks while reducing debt?

The base scenario funds $600m of first-period repurchases and $134m of residual debt repayment. The case depends on assumed brand contribution margins. A lower share count alone does not establish an operating recovery.

**Who it helps:** A financial analyst evaluating capital allocation, cash requirements and downside resilience.

**Evidence:** Three years of reported statements, latest quarterly comparatives, dated share count and a corroborated closing price. Five-year projections are labeled scenarios.

**What I built:** An integrated Excel model with operating drivers, three statements, a financing waterfall, DCF, reverse valuation and two-input sensitivities. Python reproduces the analysis. SQL reconciles reported financial statements.

**Finding:** Buybacks and debt reduction compete for the same cash. First-period operating cash of $801m less $80m capex leaves $721m. Opening cash above the $150m reserve adds about $13m. After $600m repurchases, $134m remains for debt repayment.

**Why it matters:** Evaluate repurchases alongside brand cash contribution and debt reduction. Treat faster EPS growth cautiously when it mainly reflects fewer shares. Keep distributions conditional on cash generation rather than assuming a fixed repurchase pace through a brand downturn.

**Limitation:** The most consequential operating choice is the contribution margin assigned to each brand before D&A and SG&A. Base Crocs contribution is 65%, with HEYDUDE at 46% rising to 48%. These are analyst assumptions, not disclosed brand cash margins. Because brand D&A allocation is unavailable, the model uses a combined PPE and finite-intangible depreciation pool. The strongest argument against the base conclusion is that assumed contribution margins and modest SG&A improvement overstate sustainable cash profitability. The DCF range spans about $71 to $213 across the three operating cases at the same WACC and growth. This is a scenario range without assigned probabilities, not a statistical confidence interval.

**Downloadable, offline project:** Excel workbook, executive memo, five-minute presentation, data, methods and code. No hosted application is claimed. Published as independent portfolio research.
