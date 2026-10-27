# Reproducible research toolkit

## Reproduce and inspect

From repository root, Python 3.12:

```bash
python -m venv /tmp/finance-oct26
/tmp/finance-oct26/bin/python -m pip install -r projects/2026-10-26/research-toolkit/requirements.txt
/tmp/finance-oct26/bin/python projects/2026-10-26/research-toolkit/verify.py
```

On Windows use the venv's `Scripts/python.exe`. Open `outputs/report.html` or `outputs/app.html` directly. Both are self-contained offline files; GitHub source publication does not host a live service.

Actual browser acceptance (Node 22):

```bash
npm install --prefix /tmp/finance-browser playwright@1.56.1
/tmp/finance-browser/node_modules/.bin/playwright install --with-deps chromium firefox webkit
NODE_PATH=/tmp/finance-browser/node_modules node projects/2026-10-26/research-toolkit/browser_test.cjs
```

The shared toolkit is implementation infrastructure, not an additional portfolio project. CI repeats clean installation, twelve analytical/source tests, empty-output reproduction and 24 engine/viewport/surface browser cases. Tests and actual results are separate: `verification.json` certifies analytical checks; the browser evidence release certifies executed browser cases. Screenshots and browser evidence are linked from the root portfolio README after acceptance.

## Recollect official sources into a new staging directory

```bash
python projects/2026-10-26/research-toolkit/collect.py --cache /tmp/oct26-originals --output /tmp/oct26-staging
```

Output must be empty. The collector downloads official FRED and SEC companyfacts/submissions/original 10-K responses, creates scoped numerical projections and audits latest originals. Network responses can change. Compare new source hashes and findings, quarantine changed vintages, and review them rather than overwriting the pinned research. The pinned clean build needs no runtime network.

Historical companyfacts rows are source-linked selections, not a full-original historical audit. Latest-file HTML numerical projections retain contexts, dimensions, units, scale and element positions. `verification.json` states the actual independent checks and numeric tolerance. Floating-point portability uses relative tolerance 1e-7 / absolute 1e-8 for numerical outputs; code/layout reproduction is exact. Local exact-byte counts are reported separately, not promised across CPUs.
