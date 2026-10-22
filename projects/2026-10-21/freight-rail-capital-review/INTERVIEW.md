# Personal understanding and interview defense

I built a capital-allocation review for three US-listed freight railroads. The central question was whether operating cash covered cash capital spending and shareholder payments, before anyone argued for changing reinvestment. The coherent 2025 totals were $18.264B of operating cash, $8.897B of cash PP&E capex and $10.032B of dividends plus buybacks, leaving a −$665M specified residual. That means those uses exceeded that source; it does not prove which payments were financed with debt.

I also challenged the accounting return measure. Older depreciated assets can make returns on net book assets look stronger than returns on gross assets, and Union Pacific changed to a finance-lease-inclusive asset definition. I labeled that boundary and suppressed the cross-basis return comparison. The 72 cash stress cases and 72 asset/tax/hurdle cases are assumptions, not forecasts or probabilities. In an interview, I would emphasize that a rail company needs current treasury plans, transaction terms and safe maintenance commitments before any distribution or capex decision.

## Two measured resume bullets

- Reconciled 32 freight-rail issuer-years and 256 SEC source operands in Python/SQL, including independent matches for all 24 latest annual facts and an explicit finance-lease asset-basis transition.
- Analyzed a −$665M FY2025 cash residual after PP&E expenditure and shareholder payments; built 72 cash stress cases and 72 asset/tax/hurdle sensitivities with independent Decimal reconciliation of every cash scenario.

## Five interview questions and answers

1. **Why is the result not a current funding-deficit estimate?** It is a dated FY2025 subtotal of CFO less capex and shareholder payments. It excludes available cash, debt flows, acquisitions and other uses. It cannot identify financing sources or reflect the current 2026 plan. The application makes that limit explicit.
2. **Why did entity and period scope matter?** I require coherent annual facts from one filing accession and consolidated parent entities. The first standardized UNP asset series stopped before peers; investigation found a finance-lease-inclusive successor series. I retained the basis label, added the current comparable facts and excluded return comparisons across the transition.
3. **How is the stress threshold calculated?** Holding the other cash flows fixed, the CFO change needed for zero residual is (capex + dividends + buybacks)/CFO − 1. Positive means CFO must grow to cover the observed uses; negative means a decline would exhaust the surplus. The exact scenario grid is independently reconciled using Decimal arithmetic, including zero-floored potential buyback capacity.
4. **Why is the return proxy not ROIC?** It divides assumed after-tax GAAP operating income by average net or gross productive assets. It omits working capital, goodwill and other corporate invested-capital adjustments. Tax and hurdle rates are assumptions; asset age, leases, gains and charges affect comparisons. It cannot estimate a new project's IRR or the issuer's WACC.
5. **Would you reduce capex because of a low proxy return?** No. First obtain current treasury plans, the maintenance/growth split, safety minimums, commitments and merger terms. Review discretionary distributions within that complete plan. The model leaves the adoption gate unmet and does not interpret its 80% UI capex boundary as a safe operating budget.
