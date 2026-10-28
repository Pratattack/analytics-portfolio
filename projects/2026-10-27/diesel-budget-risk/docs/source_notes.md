## Question and intended reader

How much diesel-price risk should an operations budget carry for thirteen weeks? A procurement or FP&A reader can compare budget adequacy, unused capacity and residual shortfalls rather than looking at coverage alone.

## Data and method

1,035 weekly U.S. EIA diesel retail prices through October 26, 2026, retrieved via FRED GASDESW on October 28, 2026. Prices include taxes and are not seasonally adjusted. This is the national all-types series; historical fuel-specification changes limit comparability. The actual export is pinned because cached metadata was one release behind its latest row.

79 non-overlapping complete thirteen-week blocks are constructed, anchored to the second Monday in the export. All rules use the preceding Monday quote. Training targets must have ended at least seven days before the next origin, allowing for EIA publication. At least twenty completed historical blocks are required. The reserve is the higher empirical 90th quantile of quarter mean / lagged quote, with a minimum multiplier of one.

The 2016 to 2019 validation period selects among 20-quarter, 40-quarter and all-history windows using dollar-per-gallon quantile loss. The selected all-history window is frozen before evaluating 2020 onward. Newly completed targets can enter later training sets; this is sequential evaluation, not a single static fit. Baselines are no buffer and a fixed 10% buffer. Only fully completed quarters are scored. EIA's contemporary and historical release schedules differ, so a conservative prior-week quote is used across the entire sample.

Mean and worst dollar shortfalls and unused reserve assume 100,000 gallons per quarter evenly spread over thirteen weeks. This hypothetical exposure is clearly separate from observed prices. Alternative quantiles/windows are reported only as current scenario sensitivity, not used to retune holdout results.

## Limits and decision use

Historical 76.9% coverage missed a nominal 90% target. No future coverage guarantee is implied. The sample contains 26 holdout quarters, and non-overlap does not remove serial dependence. Current revised history is not a real-time vintage backtest. National retail prices are not fleet invoices, local route costs, wholesale contracts or hedge prices. Fuel volume, tax treatment, delivery fees and changing purchase schedules are excluded. An unused reserve is not savings. No company impact is claimed.

Source definitions: https://fred.stlouisfed.org/series/GASDESW , https://www.eia.gov/petroleum/gasdiesel/diesel_proc-methods.php , https://www.eia.gov/dnav/pet/PET_PRI_GND_A_EPD2D_PTE_DPGAL_W.htm

