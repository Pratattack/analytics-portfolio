# Who funds private credit, and which totals are comparable?

A 2026 measurement change makes private credit more visible. A scope ledger separates $1.458 trillion of broad business lending from $1.310 trillion in the nonfinancial-business debt table.

## Finding
The publication reports $1.458 trillion of private loans to U.S. businesses, while the nonfinancial-business debt table reports $1.310 trillion, or 5.62% of that debt denominator. The difference is scope. Bank funding of credit vehicles is a separate intermediation layer. Newly identifying the sector in 2026 does not mean its existing balances were newly borrowed.

## Decision use
Reconcile borrower and vehicle scope before comparing exposure totals or adding intermediation layers. Use the scenario explorer to identify what further funding, valuation and instrument-detail evidence would be needed before judging a vehicle type.

## Evidence and method
Official Federal Reserve October 16, 2026 publication, with rounded balance sheets observed at 2025 Q4. Public aggregate tables only; confidential Form PF microdata are not used. Hypothetical marks and an equity/assets screen are separate from observed balances.

Source-table extraction, units and scope reconciliation, independent SQL equity identities, and accounting mark-down scenarios on U.S. private loans and corporate equities. Reverse-solve the mark that reaches an assumed equity/assets screen. Preserve source blanks and rounding residuals; exclude CLOs from equity comparisons.

## Limits
The observations are 2025 Q4, not live 2026 holdings. Aggregate fund populations hide dispersion. CLO equity is not separately reported and is not treated as zero. Missing maturity, withdrawal and unencumbered-cash data prevent a redemption or liquidity model. No default probability, regulatory solvency finding or institution-level contagion is established.
