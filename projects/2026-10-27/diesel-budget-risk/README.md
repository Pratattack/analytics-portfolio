# Diesel Fuel Budget Risk: A 13-Week Reserve Test

A historical q90 reserve covered 20 of 26 holdout quarters (76.9%). A fixed 10% buffer covered 92.3%. The historical rule is retained as an honest undercoverage result, not promoted as a superior model.

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

## Reproduce

Python 3.11 or later was used. From this project directory:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python analyze.py
python -m unittest -v
node test_calculator.cjs
```

Analysis runs entirely offline against pinned CSV exports. Open `outputs/report.html` or `outputs/workbench.html` directly after extraction. No server, account, API key, package CDN or network request is needed to use the workbench. `python refresh_data.py --refresh` deliberately replaces the snapshots. Review regenerated findings and tests before publishing an update.

## Audit trail

- `data/raw/`: unmodified FRED CSV exports of government-origin series.
- `data/source_manifest.json`: exact URLs, retrieval date, units, series definitions, byte counts and SHA-256 checksums.
- `analyze.py`: analysis, numerical validation and report generation.
- `reconcile.sql`: independent SQLite arithmetic against raw observations.
- `outputs/`: charts, accessible HTML report, scenario calculator and downloadable evidence.
- `docs/executive_memo.md`: finding, decision use and limits.
- `test_analysis.py` and `test_calculator.cjs`: analytical and scenario boundary checks.

All charts are generated from the pinned observations or clearly labeled hypothetical exposures. SVG is used for crisp scaling without external scripts. Source exports are current revised history, not archived real-time vintages. Charts do not establish causation.

## Attribution and reuse

Original code and writing are MIT licensed; see LICENSE. Data originate with the U.S. Bureau of Labor Statistics or U.S. Energy Information Administration and are distributed by the Federal Reserve Bank of St. Louis FRED service. Source terms apply to the underlying data; no endorsement is implied. No FRED logo, proprietary icon pack, stock imagery or third-party font is bundled. The reports use installed system fonts. Python dependencies are installed separately under their respective licenses.
