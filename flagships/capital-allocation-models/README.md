# Financial decisions behind capital allocation

Two financial modeling projects by Prathamesh Singh. Research cutoff: 2 November 2026. Quote date: 30 October 2026. Latest balance sheets: 30 September 2026.

## Start here

Open `outputs/fm-20261101/URI_Executive_Memo.html` or `CROX_Executive_Memo.html`. Each is a self-contained memo with embedded evidence charts and sources. The two Excel files contain editable integrated models. The two PowerPoint files contain five editable slides with timed speaker notes and native charts.

- **United Rentals:** How much can it return after funding its fleet? Base first-period repurchases are $597m against a hypothetical $1,500m ceiling. Higher investment lowers initial upside-case distributions despite stronger operating cash.
- **Crocs:** Can it fund buybacks while reducing debt? Base first-period cash supports $600m repurchases and $134m residual debt reduction. The result depends on assumed contribution margins. Buyback-driven EPS is separated from operating performance.

All future amounts are scenarios. No probabilities or stock recommendations are assigned. These are analytical models, not company forecasts or investment price targets. The research notes explain weaknesses and arguments against the conclusions.

## Use the workbooks

1. On **Assumptions**, edit E4: 1 = Base, 2 = Downside, 3 = Upside. All forecast schedules use that one selector. Historical actuals stay unchanged.
2. Blue figures are inputs. Green figures link to another sheet. Black formulas calculate within the sheet. Each driver has an active row and three editable case rows.
3. Forecast columns I:M are twelve-month periods ending September 2027–2031. History contains calendar 2023–2025 plus LTM September 2026. Balance-sheet stocks use the stated date, not a trailing-year sum.
4. On **Valuation**, E5/E6 control WACC and terminal growth. E8 is the dated quote. E9/E10 change a first-period operating shock and capex multiplier for local stress testing. Reset E9 to zero and E10 to one after experimenting.
5. **Valuation** contains two native two-input Excel What-If Data Tables. Excel may require automatic calculation and recalculation of data tables. Other spreadsheet applications may handle these differently.
6. **Checks** should show zero accounting differences. Funding requirements are economic outputs, not balance-sheet plugs or commitments from lenders.
7. Sources and nearby assumption notes distinguish reported facts, calculated calibrations and analyst scenarios. The full numeric context and source hashes are in `data/source_lineage.csv`.

## Reproduce the numeric analysis

From the extracted project directory:

```bash
python src/model.py
python src/validate.py
python src/build_reports.py
```

The first two commands require only Python's standard library and the included input and numeric-fact snapshots. The third requires matplotlib. `src/reconcile.sql` runs against the SQLite database created by validation. CSV exports contain all scenarios and DCF sensitivities. The independent numeric calculation has no spreadsheet runtime dependency.

To repeat source extraction, install lxml, re-download the six filings using `data/filing_manifest.json`, and place HTML files at `data/raw/ID.html`. Verify hashes, then run `src/extract.py` and `src/prepare.py`. SEC requests require a descriptive user-agent and rate-limit compliance. Included companyfacts JSON supplies an explicitly disclosed comparative zero where no inline cell was tagged. An absent current-debt tag is not represented as a disclosed zero.

Spreadsheet and presentation authoring sources use `@oai/artifact-tool`, which must be available in the authoring environment. They are included for review and regeneration in a compatible licensed environment. The decks' chart workbooks contain rounded display-data snapshots, not the full financial model. They are intentionally distinct from the formula-driven Excel workbooks.

## What was checked

- Seven Python tests cover accounting and cash roll-forwards, cash-capped distributions, impairment treatment, explicit funding needs, later-driver propagation, buyback versus cash-flow effects, and valuation rules.
- Eighteen SQL reconciliations check reported balance sheets and changes in cash.
- The Excel authoring calculation matches Python across three cases and five forecast periods. Later input propagation and native sensitivity cells are checked.
- Workbook packages contain nine uniquely identified sheets, two native data tables each and no cached formula errors.
- Presentation packages pass structural, font, layout and editable-chart checks. All ten final slides were rendered and visually inspected. All workbook sheets were rendered and reviewed.

Manual desktop Excel and PowerPoint testing was unavailable. Browser rendering of the HTML memos was not tested. Publication checks are recorded separately from model validation.

## Limitations that matter

The operating builds are simplified rather than complete corporate planning systems. URI uses approximate fleet cohorts and a rounded opening gross fleet amount. Crocs' brand contribution margins are assumptions, and finite intangibles share a depreciation pool with PPE. Other assets and non-payable liabilities remain constant. No future M&A is assumed. Refinancing fractions and principal stress budgets after the initial period are hypothetical, not contractual maturity schedules or secured funding. Interest uses opening debt. Cash reserve assumptions do not replicate covenants. No tax refunds on losses are assumed. Terminal value is a large share of DCF enterprise value. The reverse margin is conditional on frozen explicit cash flows and chosen terminal reinvestment. Equal-month proration to the quote date ignores seasonality. Share settlements use stock compensation divided by a fixed quote as an illustrative proxy.

For detailed assumptions, source links, competing evidence and interview discussion, read `docs/*_Research_Methodology.md` and `docs/*_Interview_Notes.md`. Proposed website copy is in `docs/*_Portfolio_Copy.md`. Both projects are published as independent portfolio research.

## Rights and attribution

Original project code and writing are offered under the included MIT license. Source facts retain their provenance. Company filings, investor materials and trademarks remain subject to their owners' rights. No company sponsorship is implied. Full company filings and third-party software or fonts are not redistributed. Charts are original renderings of sourced facts or explicitly labeled model scenarios. matplotlib and lxml retain their own licenses.
