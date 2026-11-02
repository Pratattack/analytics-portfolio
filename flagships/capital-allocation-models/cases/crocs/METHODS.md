# Crocs: research and model notes

Research cutoff: 2 November 2026. Market price cutoff: 30 October 2026.

## Decision and business economics

Evaluate repurchases alongside brand cash contribution and debt reduction. Treat faster EPS growth cautiously when it mainly reflects fewer shares. Keep distributions conditional on cash generation rather than assuming a fixed repurchase pace through a brand downturn.

Crocs sells through wholesale and direct channels under Crocs and HEYDUDE. The model preserves four disclosed brand-channel revenue streams. Channel growth alone does not identify price, volume, returns or promotion. The annual report names Nike, adidas, Deckers, Birkenstock, Steven Madden, Wolverine and VF among competitors. Their brand and channel mixes differ, so no peer multiple or peer-derived WACC is imposed. Public evidence supports a brand and cash-allocation stress model, but does not identify brand cash contribution precisely.

## Historical bridge

Annual 2023, 2024 and 2025 figures are taken from the downloaded annual filings. Comparative nine-month 2025 and nine-month 2026 flows use the latest quarterly filing. LTM = annual 2025 + nine-month 2026 - nine-month 2025. Balance-sheet stocks use dated balances, never this flow formula. Restated comparative values are preferred where present. Missing data remain missing unless a zero is explicitly disclosed. Each selected numeric fact has a context, dimension, source ID and source hash in source_lineage.csv. Annual and September-ending forecast dates are deliberately different.

The workbook adds reported impairment back to historical recurring operating income where available, while showing the charge and reported operating income separately. This is an analytical reconciliation. It does not imply the loss was harmless. Crocs FY2025 reported net loss and unusual tax history remain visible. Historical EPS is omitted rather than approximated using period-end shares.

## Assumptions and conflicting evidence

The most consequential operating choice is the contribution margin assigned to each brand before D&A and SG&A. Base Crocs contribution is 65%, with HEYDUDE at 46% rising to 48%. These are analyst assumptions, not disclosed brand cash margins. Because brand D&A allocation is unavailable, the model uses a combined PPE and finite-intangible depreciation pool.

Base is a modeling reference, not a probability-weighted expected outcome. Growth and contribution margins are analyst scenarios bounded by downside and upside inputs. Management guidance informed the first investment budget only and is not relabeled as guidance for a September-ending forecast year. Historical strength supports testing continued cash generation. Cyclicality, competitive pricing, investment needs and incomplete cost disclosures support the downside. The result is deliberately conditional.

- **tax**: base [0.2, 0.2, 0.2, 0.2, 0.2]; downside [0.22, 0.22, 0.22, 0.22, 0.22]; upside [0.18, 0.18, 0.18, 0.18, 0.18]. Analyst normalized cash tax rate. No immediate cash refunds for losses.
- **interest**: base [0.065, 0.065, 0.065, 0.065, 0.065]; downside [0.085, 0.085, 0.085, 0.085, 0.085]; upside [0.06, 0.06, 0.06, 0.06, 0.06]. Analyst blended financing cost. Interest uses opening debt, with year-end financing timing.
- **dso**: base [31.596769977577015, 31.596769977577015, 31.596769977577015, 31.596769977577015, 31.596769977577015]; downside [39.59676997757701, 39.59676997757701, 39.59676997757701, 39.59676997757701, 39.59676997757701]; upside [28.596769977577015, 28.596769977577015, 28.596769977577015, 28.596769977577015, 28.596769977577015]. Latest receivables / trailing revenue x 365. Scenario changes are assumptions.
- **dio**: base [90.59308334835646, 90.59308334835646, 90.59308334835646, 90.59308334835646, 90.59308334835646]; downside [105.59308334835646, 105.59308334835646, 105.59308334835646, 105.59308334835646, 105.59308334835646]; upside [87.59308334835646, 87.59308334835646, 87.59308334835646, 87.59308334835646, 87.59308334835646]. Latest inventory / trailing reported cost of revenue x 365; forecast cost denominator excludes D&A and disposal book cost.
- **dpo**: base [59.77086112613424, 59.77086112613424, 59.77086112613424, 59.77086112613424, 59.77086112613424]; downside [54.77086112613424, 54.77086112613424, 54.77086112613424, 54.77086112613424, 54.77086112613424]; upside [62.77086112613424, 62.77086112613424, 62.77086112613424, 62.77086112613424, 62.77086112613424]. Latest payables / trailing reported cost of revenue x 365; forecast denominator follows forecast operating costs.
- **sbc**: base [0.010895729683493503, 0.010895729683493503, 0.010895729683493503, 0.010895729683493503, 0.010895729683493503]; downside [0.010895729683493503, 0.010895729683493503, 0.010895729683493503, 0.010895729683493503, 0.010895729683493503]; upside [0.010895729683493503, 0.010895729683493503, 0.010895729683493503, 0.010895729683493503, 0.010895729683493503]. Trailing reported stock compensation / revenue. Economic expense retained in DCF.
- **repurchases**: base [600, 600, 600, 600, 600]; downside [300, 300, 300, 300, 300]; upside [800, 800, 800, 800, 800]. Hypothetical annual repurchase ceiling, funded only after minimum cash and dividends.
- **dividends**: base [0, 0, 0, 0, 0]; downside [0, 0, 0, 0, 0]; upside [0, 0, 0, 0, 0]. Analyst distribution budget; not a future board declaration.
- **debt_sweep**: base [1, 1, 1, 1, 1]; downside [1, 1, 1, 1, 1]; upside [1, 1, 1, 1, 1]. Fraction of remaining surplus directed to debt after the repurchase ceiling.
- **refinance**: base [1, 1, 1, 1, 1]; downside [0.75, 0.75, 0.75, 0.75, 0.75]; upside [1, 1, 1, 1, 1]. Hypothetical fraction of the repayment budget refinanced. Borrowing availability is not assured.
- **principal**: base [0, 100, 850, 0, 350]; downside [0, 100, 850, 0, 350]; upside [0, 100, 850, 0, 350]. Repayment stress budget, not an instrument-level contractual maturity schedule. Year one uses latest current debt if disclosed; later years are analyst assumptions.
- **impairment**: base [0, 0, 0, 0, 0]; downside [200, 0, 0, 0, 0]; upside [0, 0, 0, 0, 0]. Hypothetical noncash, nondeductible brand impairment. No forecast of an actual charge.
- **crocs_dtc_growth**: base [0.07, 0.06, 0.05, 0.04, 0.04]; downside [-0.08, -0.03, 0.01, 0.02, 0.03]; upside [0.12, 0.1, 0.08, 0.06, 0.05]. Analyst growth path informed by disclosed DTC/channel trends; no customer-level conversion forecast.
- **crocs_wholesale_growth**: base [0.02, 0.03, 0.03, 0.03, 0.03]; downside [-0.1, -0.05, 0, 0.02, 0.02]; upside [0.05, 0.05, 0.04, 0.04, 0.03]. Analyst wholesale revenue growth. Distributor inventory and consumer sell-through are not observed.
- **hey_dtc_growth**: base [0.04, 0.05, 0.05, 0.04, 0.04]; downside [-0.15, -0.1, 0, 0.02, 0.03]; upside [0.1, 0.1, 0.08, 0.06, 0.05]. Analyst HEYDUDE DTC recovery scenario; growth is not assumed from one quarter alone.
- **hey_wholesale_growth**: base [0.04, 0.05, 0.05, 0.04, 0.04]; downside [-0.2, -0.1, 0, 0.02, 0.03]; upside [0.12, 0.1, 0.08, 0.06, 0.05]. Analyst HEYDUDE wholesale scenario; no invented order-book data.
- **crocs_contribution**: base [0.65, 0.65, 0.65, 0.65, 0.65]; downside [0.61, 0.61, 0.61, 0.61, 0.61]; upside [0.665, 0.665, 0.665, 0.665, 0.665]. Analyst contribution margin before allocated D&A and SG&A. Calibrated to published brand gross margins plus aggregate D&A allocation, not a reported brand cash margin.
- **hey_contribution**: base [0.46, 0.47, 0.48, 0.48, 0.48]; downside [0.4, 0.4, 0.42, 0.43, 0.44]; upside [0.49, 0.5, 0.51, 0.51, 0.51]. Analyst contribution margin before allocated D&A and SG&A; brand-level D&A is not separately disclosed.
- **sga_rate**: base [0.38, 0.378, 0.375, 0.375, 0.375]; downside [0.4, 0.4, 0.4, 0.4, 0.4]; upside [0.375, 0.37, 0.365, 0.36, 0.36]. Analyst recurring SG&A excluding modeled D&A under the analytical expense-allocation convention. Stock compensation remains expensed.
- **other_capex**: base [80, 80, 80, 80, 80]; downside [65, 65, 65, 65, 65]; upside [100, 100, 100, 100, 100]. Hypothetical annual PPE/software cash budget calibrated to management 2026 capex guidance, not future company guidance.
- **legacy_dep**: base [0.20109518472640042, 0.20109518472640042, 0.20109518472640042, 0.20109518472640042, 0.20109518472640042]; downside [0.20109518472640042, 0.20109518472640042, 0.20109518472640042, 0.20109518472640042, 0.20109518472640042]; upside [0.20109518472640042, 0.20109518472640042, 0.20109518472640042, 0.20109518472640042, 0.20109518472640042]. Trailing total D&A / latest PPE plus finite intangible asset pool. Avoids inventing an undisclosed D&A allocation.

## Valuation and reverse valuation

DCF discounts unlevered cash flow after stock compensation expense. Terminal reinvestment = terminal growth / terminal ROIC. Base WACC is 11%, terminal growth 2.0%, and terminal ROIC 15%. These are analyst hurdle assumptions, not a precisely estimated CAPM. The workbook exposes WACC/growth sensitivity. Reverse valuation fixes the explicit cash flows and solves the terminal EBIT margin needed to reconcile enterprise value to price times cover-page shares plus September net debt. The answer is conditional on this exact setup. It does not identify a unique market forecast.

The strongest argument against the base conclusion is that assumed contribution margins and modest SG&A improvement overstate sustainable cash profitability. The DCF range spans about $71 to $213 across the three operating cases at the same WACC and growth. This is a scenario range without assigned probabilities, not a statistical confidence interval.

## Model mechanics and reviewer concerns

A cash-only first-period EBITDA threshold of about $854m funds the $600m ceiling with other cash drivers unchanged. Base EBITDA is $1,022m. A persistent contribution-margin decline, slower inventory conversion or refinancing shortfall would support reducing the ceiling. Evidence of brand recovery that survives these tests would strengthen it.

New borrowing is an explicit funding need when cash is insufficient, not evidence that a lender will fund it. Financing interest starts in the following year. Repayment budgets after the initial current-debt amount are assumptions, not security-level maturities. The cash reserve is an analyst policy, not a covenant. Other balance-sheet items remain constant, limiting deferred-tax, lease and pension detail. Forecast FX is zero. No future acquisitions are assumed. Dividend and repurchase ceilings are illustrative. The two-input repurchase table changes only the first operating shock and capex multiplier, so it is a local sensitivity, not a full downside case. The cash-only EBITDA threshold freezes the other cash drivers. Equal-month valuation proration is a material timing simplification for seasonal businesses.

## Decision evidence to request

Brand and channel contribution margins, promotion intensity, returns, unit volumes and prices, geographic tariff exposure and financing terms would most improve the analysis. Sell-in revenue is not proof of consumer sell-through.

## Reproduction and checks

Run src/model.py, then src/validate.py. The latter tests all case balance sheets and cash closes, the cash distribution cap, impairment tax/cash behavior, a financing shortfall, later-driver propagation, valuation monotonicity and invalid discount rates. SQLite checks independently reconcile reported balance sheets and cash changes. The Excel builder tests all five forecasts against Python for each case, changes a later driver and compares native two-input Data Table cells with direct recalculation. Excel desktop and PowerPoint desktop were not available for manual application testing.

The Excel builder requires @oai/artifact-tool. Numeric model reproduction requires only Python standard library plus lxml for source re-extraction. Chart recreation additionally requires matplotlib. Selected input snapshots are distributed. Full filing HTML is not redistributed in this package. Re-download using filing_manifest.json and verify hashes before running extract.py and prepare.py. SEC may restrict automated requests, so use a descriptive user-agent and honor rate limits.

## Additional company context sources

- [Q3 2026 earnings presentation](https://s22.q4cdn.com/133460125/files/content_files/Q3-2026-Earnings-Presentation-vF.pdf). Management presentation or release, distinct from the SEC statement facts.
- [Q3 2026 earnings release](https://investors.crocs.com/news-and-events/press-releases/press-release-details/2026/Crocs-Inc--Reports-Strong-Third-Quarter-2026-Results-Raises-Full-Year-2026-Outlook/). Management presentation or release, distinct from the SEC statement facts.
