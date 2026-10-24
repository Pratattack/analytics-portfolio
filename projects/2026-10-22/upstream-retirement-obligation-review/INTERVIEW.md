# Resume evidence and interview defense

## Two measured resume bullets

- Reconstructed 35 upstream retirement-obligation rollforwards from 17 original SEC filings for six issuers, retaining 257 auditable ledger operands and separating explicitly disclosed cash payments from liability removals.
- Built a constrained timing workbench with 216 conditional scenarios and 18 infeasible assumption combinations; independently reconciled LP bounds against extreme-point enumeration and documented why the model cannot yet approve a retirement reserve.

Independent portfolio work only. No measured corporate savings, actuarial qualification, employment tenure or claim of engineering cost estimation is implied.

## Five questions and grounded answers

**1. Why not use the XBRL liabilities-settled tag as cash spending?**
Because its meaning depends on the original table. COP 2025 separately reports $259m spending and $186m property dispositions; the latter uses the settled-liability tag. Devon and Diamondback combine settlements with divestitures. I retain the tag as a book-liability removal and leave cash null unless explicitly identified.

**2. What source issue did you find that a generic parser could miss?**
Normalized taxonomy signs differ from displayed economic movements in some COP/EOG revisions or currency rows. The parser preserves both signs, reconstructs the table with presentation signs, and checks closure. Devon's ARO-table accretion differs from a similarly named fact elsewhere; I keep the ledger scope. Older COP documents also use DIV-based tables rather than HTML table cells.

**3. What is optimized?**
The allocation of a fixed present-value stock across years 1–30, given a single assumed discount rate, a PV-weighted mean date and a near-term PV-share cap. The objective is undiscounted cash equivalent. With three binding constraints, boundary distributions need at most three dates. An independent enumeration agrees with the LP. Neither implementation estimates the real schedule.

**4. Why can a scenario be infeasible?**
If first-five-year PV is forbidden, the earliest permitted year is 6. A mean date 5 is then impossible. Eighteen grid rows preserve that inconsistent assumption combination with null bounds. It is not evidence that any issuer is insolvent or short of cash.

**5. What prevents you from recommending a reserve?**
Book ARO contains historical discount layers and issuer cost assumptions; asset-level timing, legal transfers and cash settlement evidence are missing. A common-rate conversion does not recover those inputs. I would request engineering schedules, discount-layer detail, invoices and sale agreements, reconcile them to the ledger, then construct a constrained treasury cash model. Reporting a mathematically tight interval does not make missing evidence disappear.
