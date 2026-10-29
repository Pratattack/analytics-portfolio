# Import Duties and Sourcing Tradeoffs

Which electrical-equipment categories warrant a sourcing review, and how much of a historical duty-ratio change survives a comparable-product screen? The project uses actual Census imports for consumption and calculated duties for **January-August 2025 versus January-August 2026**, with August-only sensitivity.

## Data and selection

Three HS4 groups were selected before examining outcomes: 8504 electrical transformers/static converters/inductors, 8507 electric accumulators and 8541 semiconductor devices. These categories are relevant to equipment supply chains; the project does not claim all shipments serve AI infrastructure or identify tariff-policy causation.

Whitelisted text files from the two complete official monthly bulk archives are read as fixed-width records. Executables, DLLs and bundled installers are never extracted or run. Records are aggregated once across district, country subcode and rate provision into HTS10/origin cells. Both monthly and YTD selected totals must match independently published IMP_COMM commodity totals exactly. The checked-in extracts reproduce the analysis without re-downloading nearly half a gigabyte of compressed archives.

`data/source_manifest.json` records archive URLs, SHA-256 hashes, retrieval times, row counts and extraction scope. Layout and selected code descriptions are retained. `fetch_extract.py` can reproduce the extracts from downloaded archives; see its help. Historical source files can be revised, so this is not a point-in-time policy backtest.

## Decomposition and its limits

The historical duty ratio is calculated duties divided by customs value for imports for consumption, not general imports or only dutiable value. It is not a current statutory tariff, final duty cash collection, supplier quote or causal incidence estimate.

Comparable cells require positive values in both years and identical HTS10 descriptions. The starting-basket component is sum(w2025 * (rate2026-rate2025)). The composition component is sum((w2026-w2025) * rate2026). They sum exactly to the balanced-panel rate change. The order is explicit and descriptive. New/exited, zero-value and changed-description cells are excluded, with value coverage published for both years. The semiconductor and accumulator panels have materially incomplete 2026 coverage, so their decompositions must not be generalized to all imports. Low coverage is a finding, not a reason to silently relax the match.

Identical descriptions are not a legal concordance, and hidden quality, timing and supplier composition can remain even within HTS10/origin cells. Rates and country concentration do not establish supplier availability or switching feasibility.

## Sourcing tool

The five largest origins in each 2026 YTD category are chosen by customs value before inspecting duty ratios. A pair is eligible only if shared identical-description HTS10 items cover at least 80% of source-origin value. Both historical rates are standardized to that same source product basket. This cross-origin comparison uses 2026 products; it is separate from the cross-year decomposition panel.

The scenario applies a hypothetical annual customs-value budget, share shifted, replacement supplier-price premium and one-off switching cost. A premium scales both the shifted base value and the alternative duty allowance. The tool derives a break-even premium and charges no fixed switching fee if no volume is moved. Its cost difference is conditional arithmetic, not observed savings. Equal freight, quality, delivery and other costs are assumptions. Current legal origin/classification requirements, rates, capacity and actual quotes require separate diligence before any transaction.

## Source

U.S. Census Bureau merchandise imports bulk files IMDB2508.ZIP and IMDB2608.ZIP, plus official fixed-width layout. No API key or paid integration is required for bulk reproduction. Selected raw numerical extracts, full archive hashes and exact source URLs are retained. Files are current retrieved historical snapshots, not proof of what a decision-maker knew in real time.

## Reproduce

Python 3.11 or later and Node.js 18 or later were used. From this project directory:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python analyze.py
python -m unittest discover -s tests -v
node tests/parity.cjs
python verify.py
```

Open `outputs/report.html` or `outputs/workbench.html` directly after extracting the project package. Both are self-contained HTML with no remote fonts, account, server, API key, telemetry or automatic browser storage. Supporting CSV links require keeping the extracted folder structure. The tool lets you download its current scenario. Browser interaction was not tested because the owner prohibited browser operation.

Original code and analytical writing are MIT licensed. NumPy, pandas, lxml and Matplotlib are installed separately under their own licenses. Charts are code-generated from source data or explicitly labeled scenarios. No generated artwork is presented as evidence.

## Project files

- `data/`: pinned source snapshots/extracts, source dates, URLs and hashes.
- `analyze.py`: parsing, analytical checks, SQL reconciliation, scenario outputs, charts and HTML generation.
- `reconcile.sql`: independent aggregate arithmetic.
- `outputs/`: analytical report, browser-local scenario tool and downloadable evidence.
- `docs/executive_memo.md`: finding, decision use and limitations.
- `tests/` and `verify.py`: analytical, cross-language and static checks.

No GitHub push or website deployment is performed by these scripts. Source figures are historical observations, not forecasts. Scenario parameters are not probabilities.
