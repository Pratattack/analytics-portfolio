# Finance evidence and capital decisions — October 21, 2026

Two complementary industry cases: [semiconductor equipment inventory funding](semiconductor-inventory-funding/) and [freight rail capital review](freight-rail-capital-review/). These are independent research prototypes, not issuer recommendations or employment experience. The forecast model fails promotion; the rail screen does not authorize capital cuts or buybacks.

## Reproduce from repository root

```bash
python3.12 -m venv .venv-capital
. .venv-capital/bin/activate
python -m pip install -r projects/2026-10-21/requirements.txt
python projects/2026-10-21/verify.py
```

Reproduction is offline once dependencies are installed. It checks pinned official source snapshots, normalized source operands, original disclosure cells, hand-worked scenarios, an independent SVD forecast solution, Decimal cash-flow reconciliation, SQL totals and byte-identical clean regeneration. No API keys, private data or downloads are required in CI. `verification.json` records analytical checks; browser results are separate.

To intentionally refresh sources: set an identifying `SEC_USER_AGENT` in your own environment, then run `acquire.py` and `acquire_filings.py`, review the new manifests, run `verify.py`, and reassess coverage and source boundaries. A refresh changes the pinned version and is not necessary for reproduction. Access follows the SEC fair-access policy; acquisition uses at most two concurrent requests, retries interrupted transfers, and excludes date-only filings after October 20, 2026.

## Run the local applications

Each `outputs/app.html` is self-contained; download it and open it locally. For reports and linked audit files, serve this directory:

```bash
python projects/2026-10-21/serve.py --port 8765
```

Open `http://127.0.0.1:8765/semiconductor-inventory-funding/outputs/app.html` or `/freight-rail-capital-review/outputs/app.html`. This binds to loopback. It is not a hosted public service. The chart and brief are in `outputs/report.html`.

## Actual browser acceptance

```bash
npm install --prefix .capital-browser playwright@1.56.1
.capital-browser/node_modules/.bin/playwright install --with-deps chromium firefox webkit
NODE_PATH="$PWD/.capital-browser/node_modules" node projects/2026-10-21/browser_test.cjs
```

The 24-case matrix exercises two reports and two apps, desktop/mobile, in three real engines. Application cases reconcile baseline and changed calculations; test invalid and blank inputs, recovery, empty search, keyboard selection and Enter activation, mobile table scrolling, navigation, browser errors and desktop/tablet metric sizing. Report cases check images and linked evidence. CI publishes actual results and screenshots as an artifact. Source inspection or a test plan is not a passed browser test. Physical devices and assistive technologies remain unverified.

## What is shared

`extract.py` implements coherent accession selection, alias boundaries, source-pointer lineage and quarter-four arithmetic; `models.py` contains isolated numerical kernels; `analyze.py` implements the research; `audit_filings.py` checks independent original-filing numeric snapshots; `presentation.py` builds the reports and workbenches. Each project has its own industry data, SQL, outputs, methods, assessment, issue register and interview defense. Both require these shared parent files.
