# Methodology and pre-specified decision boundary

## Sample and information timing

MAR, HLT and CHH disclose separable reimbursement revenue and expense categories. This is a purposive sample of managed/franchised operators; WH and H were examined during source discovery but are not forced into the same definition. WH marketing/reservation/loyalty categories and H's ownership/distribution scope need separate mapping. This sample is not representative of all lodging companies. Original annual 2019/2022/2025 filings supply disclosed 2018–2025 comparatives, with a 2026 Q2 original supplying period-matched 2025/2026 quarter/half-year facts. The cutoff is 2026-10-21. The oldest CHH comparable reimbursement observations begin in 2020; missing earlier mappings remain excluded, not zero.

Select latest available disclosure of each period within the cutoff. This includes current-disclosure historical comparatives, not real-time vintages. There are 22 annual records and 12 Q2/half-year records. Period types are retained. Annual summaries exclude halves/quarters, and current summaries use only H1 2026. Q1 = H1−Q2 is a same-filing derived diagnostic, not a separate direct disclosure. Reclassifications and acquisition/business-mix changes prevent a clean causal panel interpretation.

Every selected value retains original filing URL, accession, element index, context, dimensions and unit. Revenue and cost selectors match exact product dimensions. Hilton's negated EBITDA-bridge revenue cell is not used as positive revenue. Old expense captions require explicit versioned aliases. Reported revenue less operating costs plus separately tagged gains less separately tagged impairment must reconcile to operating income. Do not assume every CostsAndExpenses subtotal has the same boundary.

## Exact accounting bridge and baseline

R = reported revenue; RR = reimbursement revenue; RE = reimbursement expense; O = operating income. B = R−RR is revenue excluding reimbursements; P = O−RR+RE is operating income excluding the net reimbursement balance. Baseline GAAP margin = O/R; bridge margin = P/B. The bridge is exact; it is not issuer adjusted EBITDA, free cash or pure fee profitability. Owned hotels, co-brand fees, depreciation, overhead, impairment and other retained accounting items can remain in P.

Within an identical quarter or half-year definition, ΔO = ΔP + Δ(RR−RE). Report that dollar identity rather than attributing change to an unobserved cause. Matched margin ranks demonstrate the sensitivity of comparability to denominator/numerator choices; they are not investment rankings. No hypothesis test or predictive confidence interval is justified by this small selected accounting panel.

## Conditional program-budget frontier

Hold P and B fixed. Let c be assumed reimbursable expense growth, g assumed reimbursement revenue growth, I incremental new program spend, and m the assumed operating-income floor as a fraction of B. Scenario O' = P + RR(1+g)−RE(1+c)−I. To meet O' >= mB, require g >= [mB+I−P+RE(1+c)]/RR−1. Required growth can be negative; that is headroom under the assumed floor, not an instruction to cut billings. Growth outside UI bounds remains displayed analytically but must not be clamped to a feasible-looking solution.

The 216 cases span c in {0,.05,.1}, g in {−.05,0,.05,.1}, I/B in {0,.02,.05}, m in {.15,.3}. The application extends each range within documented boundaries. The scenario grid is not a likelihood distribution. Recovery is not presumed billable and accrual income is not presumed collected cash. Contract recovery rights, service-level obligations, budget timing, core growth, taxes and working capital are absent. The recommendation is a source-audited budgeting workflow plus contractual diligence, not an earnings or cash forecast.

Independent Decimal accounting and bisection of the inequality reconcile all 216 cases. Source, SQL, reproducibility and actual browser tests are separate from the real-world adoption gate, which stays false.
