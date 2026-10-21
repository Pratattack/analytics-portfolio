# Methodology and decision constraints

## Information timing and empirical core

The empirical base is the six issuers' 2025 annual disclosures, filed in February 2026, with an October 20, 2026 collection cutoff. Companyfacts selections require the chosen original annual accession, exact reporting interval, USD units and no conflicting values. Dimensioned facts come from original inline-XBRL contexts. Comparative CFO uses the first suitable annual accession for each year; SKT's dimensional operating-partnership history is recovered from the pinned 2021, 2024 and 2025 original filings. Subsequent corrections and differences from the original information set remain possible; this is not a trading backtest or a complete as-released database.

The six-issuer sample is a transparent coverage choice, not a random sample or the entire retail REIT industry. Each maturity bucket uses one consistent entity scope. KIM's unconsolidated-JV mortgage schedule is excluded from its consolidated unsecured ladder. SKT uses operating-partnership cash, CFO, distributions and debt consistently. REG uses CIK 910606, the listed parent. Joint-venture guarantees, unconsolidated interests and available credit facilities require further diligence.

The retained face-to-book bridge permits an absolute difference no larger than 2% of face principal, an analyst review tolerance rather than a GAAP identity or covenant. Debt discounts, issuance costs and fair-value adjustments can explain differences. All six pass this review; the differences remain visible. Restricted cash is removed for REG. Distribution measures and FRT's broader minority/redemption cash-return scope are documented rather than assumed equivalent.

## Baseline and stress model

Let F be 2025 annual operating cash flow, D the held-fixed annual distributions, C0 unrestricted opening cash, and m_j principal maturing in year j, j=1,...,5. Let r be a common refinancing share in [0,1], d the CFO level shortfall, s incremental interest spread in decimal form, f=0.01 issuance fee, M=0.10F assumed annual maintenance capex, and L=0.10F assumed cash floor. The stress persists for h years, with h=5 or h=2 followed by full recovery to the 2025 CFO level. A 20% shock means 0.8F in each stressed year; it does not compound down 20% every year.

For year t:

`C_t(r) = C0 + t(F-D-M) - min(t,h)Fd - (1-r)sum_{j<=t}(m_j) - rf sum_{j<=t}(m_j) - rs sum_{j<=t}[m_j(t-j+0.5)]`.

New refinancing incurs half a year's incremental spread in its maturity year and a full year thereafter. Existing-debt cash interest is already reflected in the CFO base; only the additional spread is deducted. Paydown interest savings are omitted, a conservative simplification. New refinancing is assumed to mature outside this horizon; no double maturity is charged. Costs or interest for a newly required liquidity facility are not modeled.

Each cash constraint is affine, `A_t + B_t r >= L`. For B_t>0 it imposes a lower bound; B_t<0 imposes an upper bound; B_t=0 either imposes no bound or makes the case infeasible. Intersect all five constraints with [0,1]. The smallest feasible r is the minimum common rollover; an empty interval returns infeasible, never a clipped 100% answer. All-year constraints matter: positive final-year cash cannot repair an earlier breach.

The baseline is d=0, s=0, r=1. The initial 72 cases use d=0/10/20/30%, s=0/200/400bp and six issuers. Another 18 cases use d=40%, prompted by the historical 38.90% annual decline. Those severe cases are a challenge rather than fitted loss probabilities. The 90-case grid holds each shock for five years. A separate 48-row analysis compares two- and five-year duration for d=20/40%, s=200/400bp across six issuers. Neither grid is an econometric forecast or causal effect estimate.

The incremental liquidity envelope is the largest annual cash-floor shortfall at full rollover, bounded below by zero. It omits the financing cost of that new liquidity and therefore is a first-pass conditional amount, not a facility commitment. The sum of issuer-specific maxima is not a jointly calibrated sector stress loss.

## Independent validation

The source contract verifies identity, exact units, entity dimensions, interval, accession and archive hashes. Every current and historical value retains its numeric source ID or companyfacts array pointer. SQL exposure sums are independently reconstructed. Hand cash examples test rollover, fees, half-year interest and recovery. For 180 combinations of six actual inputs, five shocks, three spreads and two durations, independently derived linear constraints are solved with SciPy/HiGHS and reconciled to the affine solver. Two isolated processes reproduce all non-SQLite output bytes. Browser tests reconcile JavaScript values to Python scenario outputs and test invalid input, empty selections, recovery, keyboard navigation and responsive tables.

No uncertainty probability is assigned because the stress parameters are decision assumptions and six issuers / seven annual observations do not identify a reliable joint financing distribution. Sensitivity envelopes convey conditional uncertainty. Asset-level forecasts, covenant tests, detailed capex / leasing cash requirements, REIT tax rules and actual available facilities must be reviewed before a real management decision.
