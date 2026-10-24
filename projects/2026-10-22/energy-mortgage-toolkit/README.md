# Mortgage pricing and upstream liability research toolkit

Two independent finance research prototypes by Prathamesh Singh. The shared infrastructure is not a third portfolio project.

- [Houston mortgage price comparability](../houston-mortgage-price-comparability/): public loan-level risk/product overlap, target-population standardization, tract-cluster perturbation and holding-period offer comparison.
- [Upstream retirement obligation review](../upstream-retirement-obligation-review/): original financial-disclosure reconstruction and constrained moment bounds on hypothetical cash equivalents.

From repository root, Python 3.12:

```bash
python -m venv /tmp/portfolio-finance-venv
/tmp/portfolio-finance-venv/bin/python -m pip install -r projects/2026-10-22/energy-mortgage-toolkit/requirements.txt
/tmp/portfolio-finance-venv/bin/python projects/2026-10-22/energy-mortgage-toolkit/verify.py
```

Windows: use the equivalent venv `Scripts/python.exe`. `verify.py` checks input/method contracts, independent analytical reconciliation, and a clean, empty-output deterministic rebuild. It does not claim to execute a browser.

Actual browser checks (Node 22, internet required only to install software):

```bash
npm install --prefix /tmp/portfolio-browser playwright@1.56.1
/tmp/portfolio-browser/node_modules/.bin/playwright install --with-deps chromium firefox webkit
NODE_PATH=/tmp/portfolio-browser/node_modules node projects/2026-10-22/energy-mortgage-toolkit/browser_test.cjs
```

Set `BROWSER_ENGINE=chromium` to run only Chromium. Full CI requires all three engines, both applications and reports, desktop 1440×1000 and mobile 390×844: 24 surface/engine/viewport cases. Each application case executes main flows, blank/out-of-domain inputs, missing-source fixtures, empty search and recovery, keyboard selection/submission, reset/focus and horizontal scroll; additional tests cover infeasible timing, zero rates and fractional month rejection. Mortgage present costs and liability bounds reconcile against independent numerical references. Evidence is emitted under `browser_evidence/` and archived by `.github/workflows/mortgage-energy.yml`. Main creates a permanent commit-specific release only after both verification jobs pass.

Open either project's `outputs/app.html` or `outputs/report.html` directly in a browser. They require no server, account, API key or runtime network. They are **offline applications, not live hosted services**.

## Source maintenance

Pinned numerical projections and hashes are included. A clean build does not depend on an SEC endpoint or a moving HMDA release. `source_audit.json` records an executed comparison against complete originals, not a fresh-source claim by CI.

```bash
python projects/2026-10-22/energy-mortgage-toolkit/recollect_originals.py --directory /tmp/finance-originals
python projects/2026-10-22/energy-mortgage-toolkit/audit_sources.py --cache /tmp/finance-originals
python projects/2026-10-22/energy-mortgage-toolkit/pin_aro_tables.py --cache /tmp/finance-originals
```

Recollection deliberately fails on original-byte drift. A revised HMDA response must be quarantined and researched as a new vintage; do not replace pinned parts to get a passing check. `acquire.py` is an intentional ingestion/projection tool, not part of offline verification. It can rebuild inputs from cached originals or official endpoints; audit before accepting changes. No private resume, contact details, credentials or borrower demographic fields are included.
