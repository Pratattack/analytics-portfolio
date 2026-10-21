# Finance diligence research — October 20, 2026

Two complementary, original-source finance projects by Prathamesh Singh:

1. [Insurance Reserve Challenge Lab](insurance-reserve-capital-review/) — original paid/incurred loss-development triangles, model exclusions, masked-diagonal diagnostics and tail-sensitive actuarial diligence.
2. [Retail REIT Refinancing Resilience](retail-reit-refinancing-review/) — consolidated debt-maturity mapping, entity-scope reconciliation and a five-year constrained refinancing / cash-floor frontier.

These are independent research prototypes, not commissioned consulting work, actuarial opinions, lender approvals or claims of employment tenure. Both retain unfavorable results and distinguish observed disclosures from scenario assumptions.

## Reproduce

From the repository root, using Python 3.12:

```bash
python -m venv .venv-finance
.venv-finance/bin/python -m pip install -r projects/2026-10-20/requirements.txt
.venv-finance/bin/python projects/2026-10-20/verify_all.py
```

On Windows use `.venv-finance\Scripts\python.exe` instead. The numeric SEC snapshots are included and pinned; analysis and tests require no source-site connection. Shared Python, JavaScript and serving code is in this parent folder. Keep it with both project folders.

To regenerate only the reports/workbenches:

```bash
python projects/2026-10-20/presentation.py
```

Open an `outputs/app.html` file with its sibling `workbench.js`, or serve one project:

```bash
python projects/2026-10-20/serve.py --project insurance-reserve-capital-review
```

Visit `http://127.0.0.1:8767/app.html`; substitute `retail-reit-refinancing-review` for the other project. No hosted live service is implied.

## Source collection and independent audit

The source inventory records original SEC URLs, CIKs, accession numbers, filing dates and full-document hashes. Versioned gzip JSON files contain public numerical company facts, filing metadata and extracted numeric inline-XBRL facts with their original context, entity, dimensions, scale, sign and source IDs. Full issuer narrative HTML is not redistributed.

```bash
python projects/2026-10-20/acquire.py
python projects/2026-10-20/acquire.py --rebuild-inline --download-missing
python projects/2026-10-20/audit_html.py
```

The first command verifies the bundled numeric archives. The second retrieves the pinned original filings when necessary, re-extracts their numeric observations and reconciles them to the frozen snapshots. Live API snapshots can change; a changed source fails closed and must be reviewed rather than silently repinned. The repository's supplied snapshots remain the reproduction source for this version.

The third command independently parses the original documents with Python's standard-library HTML parser, rather than the production lxml parser. The recorded audit reconciles **52,127 numeric values and contexts in 14 original filings**, including nested inline facts. Original HTML is needed to rerun that audit; clean CI checks the frozen numeric snapshots and recorded source hashes instead of claiming a fresh HTML audit.

## Verification evidence

- Stage 1: 38 pinned archives; original-document audit; entity/unit/date/dimension contracts; complete source-pointer lineage and explicit model exclusions.
- Stage 2: 14 meaningful source/model tests, hand-worked development and cash cases, independent NumPy development reconciliation, 180 SciPy/HiGHS financing reconciliations and SQL balance checks.
- Stage 3: fresh virtual environment; two isolated fresh-process builds; byte-identical non-SQLite artifacts; HTML asset/link and SVG checks. Browser execution is a separate `finance-browser-acceptance` CI job.

The browser job must produce **24 passing cases**: two projects × report/workbench × Chromium/Firefox/WebKit × desktop/mobile. Only its actual result establishes browser acceptance. A main-only release job publishes actual screenshots and `results.json` after analytical and browser jobs pass.

Read [research sources and role alignment](RESEARCH.md), each project's methodology, data dictionary, issue register, candid assessment and interview defense. Browser acceptance does not approve financial, actuarial or credit decisions.
