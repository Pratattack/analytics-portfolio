# Resume evidence and interview defense

## Two measured resume bullets

- Built a reproducible Python/SQL mortgage research pipeline auditing 123,445 official 2025 Houston origination records; defined a five-lender common-support population of 3,867 loans across 18 product/risk cells.
- Implemented standardized APR-spread and gross-cost comparisons with 400 tract-cluster perturbations and six support sensitivities, plus an offline rate/fee workbench that includes exit loan balances and validates invalid-input recovery.

These describe independent portfolio implementation, not employment, borrower savings or hiring outcomes. Do not claim Power BI/Tableau, prior JavaScript tenure or credit-underwriting authority.

## Five questions and grounded answers

**1. What business decision does this support?**
It helps a research team determine which historical lender comparisons have observable overlap and what actual quotes to collect. It does not name a universally cheapest lender. Only 41.38% of the selected lenders' eligible loans enter the base common population.

**2. Why APR minus APOR rather than just interest rate?**
APR incorporates relevant pricing costs, and APOR supplies a date-matched market benchmark. Raw rates across a year mix changing market conditions. APR spread still cannot identify a causal premium because individual credit scores, exact public lock dates and incentives remain unobserved.

**3. What exactly did matching accomplish?**
Every lender is standardized to the same cell target, weighted by the minimum lender count per cell. Cells align loan amount, CLTV, broad DTI and Harris/other county within a fixed product contract. This improves observed comparability but can discard many loans and leaves within-cell and hidden differences. The spread range decreases only from 2.001 to 1.902 percentage points; no causal improvement is claimed.

**4. Are the plotted bands confidence intervals?**
No. They are 2.5th/97.5th percentiles of 400 positive tract-weight perturbations, conditional on the fixed cells and weights. Loans in a tract share a multiplier. This explores geographic composition stability; it does not quantify unobserved-confounder bias or census measurement error. Six alternative support definitions are reported separately and may refer to different targets.

**5. What would you defend in the offer calculator?**
Upfront fees, discounted payments and remaining principal at the chosen exit date are all included. Excluding the balance rewards slower amortization. The model assumes the same principal and 360-month term, no default or refinancing, and fees paid upfront. Browser tests compare it with a separately implemented schedule, exercise zero rates and reject fractional months. Actual dated Loan Estimates are required before using it for a real choice.
