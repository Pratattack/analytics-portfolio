# Personal understanding and interview defense

I built a register to distinguish money already exposed in land options from much larger purchase prices that depend on exercising them. The difficult part was identifying what each disclosure includes. Pulte includes pre-acquisition costs with deposits; KB Home separates them; Meritage's historical committed subtotal can include contracts already on the balance sheet. I can trace each retained amount to its original filing cell and explain the specific corrections without saying the source filing was wrong.

The decision model teaches a marginal-value question: paying a deposit in the past does not make spending more money worthwhile today. Waiting can preserve flexibility, but only under assumed land values, probabilities and enforceable extension rights. None of those was estimated from the filings. The practical recommendation is better contract diligence, not that these companies should exercise, wait or abandon their portfolios.

## Two measured resume bullets

- Built a Python/SQL land-contract register from 24 original SEC filings, tracing 185 operands into 74 scoped observations and reconciling 48 category-total identities.
- Implemented 243 conditional exercise/wait/abandonment cases and 27 refund sensitivities, independently reconciling state policies while separating $1.613B in disclosed costs from $13.711B in conditional purchase prices.

## Five grounded interview questions

1. **What did the source work change?** Meritage's 2021 committed subtotal included a recorded contract; summing its three off-balance-sheet committed categories removed that scope. Its 2026 reused tag did not establish refundability.
2. **Why does a large deposit not justify exercise?** If nonrefundable it is sunk. Compare future net land value with remaining payment; a refundable amount instead creates an abandonment opportunity cost.
3. **Where did the probabilities come from?** They are stated challenge assumptions, not estimated transition probabilities. The output is a conditional illustration rather than an appraisal.
4. **How did you independently verify the model?** Separate Decimal calculations enumerate all four future-state exercise/abandon policies, while hand cases test sunk deposits and refundable alternatives; source and SQL reconciliation are separate.
5. **What would be needed before a real decision?** Individual contract expiry/minimum-take/refund/extension rights, tract-level net development values, available capital, taxes and legal/finance review. Aggregate convex option payoffs cannot replace individual project analysis.
