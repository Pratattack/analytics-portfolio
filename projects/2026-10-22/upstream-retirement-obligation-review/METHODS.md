# Methods and decision framework

## Business question and evidence

Can a finance team use reported asset retirement obligations (ARO) to size a retirement cash budget or diligence reserve? Our answer is **not without additional timing and settlement evidence**. The workbench identifies which constraints make a hypothetical conversion possible and how wide the resulting range remains.

Six upstream exploration-and-production issuers: APA, ConocoPhillips (COP), Devon (DVN), EOG, Diamondback (FANG), Murphy (MUR). Original 10-Ks for report years 2019, 2022 and 2025 yield 17 source documents; APA's current parent has no 2019 filing in this selection. Comparable ledger years shown in those filings produce 35 retained issuer-years, not a complete continuous panel. Filed dates precede the explicit October 21, 2026 cutoff. Latest empirical book liabilities are December 31,2025 values filed February 2026. Subsequent 2026 quarterly transactions and spending are not incorporated; these are not current live debt balances.

The cohort is purposive. Consolidated international portfolios, legal regimes, asset ages and disposal activity differ. No size-adjusted performance ranking or representative industry liability total is inferred. Historical totals in `sql_history.csv` aggregate only observed panel years; never interpret them as a continuous-period cash total.

## Source lineage and original-table interpretation

`data/source_manifest.json` pins URLs, accession numbers, filing/report dates, full original HTML hashes and numerical snapshot hashes. Full numeric inline-XBRL snapshots retain context, units, dimensional scope, scale, decimals and DOM element indexes. No companyfacts fallback is mixed into original filing data. `ledger_sources.json` retains only numeric cells of the relevant original disclosure table, including separately recorded displayed signs. Older COP HTML uses positioned DIVs; the extractor supports that rendering explicitly. Original narratives are not redistributed.

Source selection requires dimensionless USD facts, a complete annual opening and closing ARO stock, and all annual numeric movement cells from that same disclosure scope. An original context with the same value is not interchangeable with a different account or dimensional scope. Display sign is obtained from the numeric table cell, not from the assumed semantic sign of its taxonomy tag. Example: COP's estimate revisions and currency effects use normalized signs that differ from displayed economic movements. Both normalized and presentation values are preserved. Devon's ARO-table accretion of $51m differs from another $49m accretion tag elsewhere in its filing; the ledger scope governs.

Each retained period must satisfy opening+sum(all displayed flows)=closing within the sum of half-unit declared rounding intervals of operands. Incomplete or unreconciled candidates go to `exclusions.csv` rather than forced balancing. This extraction has no failed candidates. If a period appears in more than one selected filing, the latest filed version wins; filing choice is retained. There is no annual interpolation.

The 257 published lineage operands reconstruct every retained ledger. An executed original-source audit independently checks 315 numerical ledger cells against complete downloaded originals. The six 2025 rollforwards are also checked against hand-transcribed presentation values, separately from the parser. Offline CI checks hashes and contracts; fresh original recollection is a separate, network-dependent audit and may be blocked by SEC access controls.

## Liability removals versus cash

Do not call a generic `AssetRetirementObligationLiabilitiesSettled` amount cash paid. COP's 2025 table labels $186m as property dispositions while separately disclosing $259m spending on existing obligations using CashPaidToSettle. Devon and Diamondback combine settlements with divestitures. Other tables can remove the book obligation, which may differ from actual settlement cost and payment date. `removed_liability` is the magnitude of that tag as presented, not a harmonized cash variable. Only an explicit CashPaidToSettle tag enters `explicit_cash_paid`; missing is null, never zero. Six issuer-year explicit cash observations are all COP. No estimate is manufactured for other firms.

## Tight conditional timing bounds

Let B be a disclosed book stock. For this **hypothetical conversion only**, impose a single nominal discount rate r and a retirement horizon of years1..30. Let w(t) be the share of total present value assigned to year t. Require:

- w(t)≥0 and sum w(t)=1.
- sum t×w(t)=μ, a user-assumed **PV-weighted** mean retirement year.
- sum(t≤5) w(t)≤c, a cap on near-term **PV share**, not a cap on undiscounted cash or a cash budget.

Then minimize/maximize B×sum w(t)(1+r)^t. These are sharp bounds over this finite feasible set: every admissible distribution lies inside, and the displayed boundary profiles attain the endpoints. SciPy HiGHS solves the production LP. Independent algebraic enumeration considers one/two-date distributions and binding-cap three-date distributions; it agrees with all 36 unique normalized grid cases. The browser uses this extreme-point formulation and reconciles against saved LP outputs. For r≥0 the objective is convex over dates. A hand-worked Jensen fixture has B=100,r=10%,μ=2,c=1: lower 121; upper 100×[(28/29)×1.1+(1/29)×1.1^30]. At r=0 both bounds equal B for any feasible timing.

The preset grid crosses r=3/6/9%, μ=5/10/15/20, c=0/25/50%, for 36 combinations per issuer, 216 overall. Eighteen issuer cases are infeasible because μ=5 with no first-five-year PV cannot be attained when the earliest remaining date is6. This is an inconsistency among **assumptions**, not a finding of issuer insolvency or insufficient funds. Preserve those rows and null bounds. Rates, means and caps are assumptions, not empirical estimates. Application domains are r∈[0,20%], μ∈[1,30], c∈[0,1].

## Economic interpretation and caveats

B already reflects the issuer's accounting estimates and historical discount layers. A common-rate conversion cannot recover those undisclosed layers. We hold B fixed and ask a conditional mathematical question; changing r does **not** remeasure GAAP ARO or isolate a change in economic risk. No extra inflation multiplier is added because that would double-count costs already embedded in a nominal PV-to-cash convention. No legal-settlement probability, salvage, insurance, tax, reimbursement or regulatory credit is estimated.

At r=6%,μ=15,c=25%, the six latest B stocks sum to $15.274867b and the same constraints imply $36.607108b–$48.513173b in aggregate conditional cash equivalents. Individual default COP range: $20.044813b–$26.564171b versus $8.364b book. Aggregation assumes identical constraints for each firm and is an illustrative conditional sum, not an industry retirement-cost forecast or reserve recommendation. It illustrates why a single book stock cannot reveal a calendar cash requirement.

## Usable diligence workflow and withheld adoption

1. Select an issuer; verify original filing, report and filing dates, scope and ledger movements.
2. Separate new obligations/acquisitions, estimate changes, accretion, divestiture transfers, cash settlement and FX. Request invoices and sale contracts for mixed categories.
3. Enter asset-team-supported timing assumptions and discount conventions; inspect feasible boundary profiles and infeasible combinations rather than substituting an arbitrary positive estimate.
4. Request asset-level remaining-life schedules, cost estimates and uncertainty, original discount layers, near-term commitments and legal recoveries. Reconcile those to book ARO before sizing a reserve.
5. Only then add a treasury liquidity model with asset-specific cash schedules and corporate constraints. This prototype deliberately withholds that adoption gate. A narrow conditional range cannot cure unreliable inputs.
