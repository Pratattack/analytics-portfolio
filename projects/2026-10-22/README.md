# October 22 finance research

Two complementary industry-specific cases: [homebuilder land-contract diligence](homebuilder-land-option-diligence/) and [hotel reimbursement economics](hotel-reimbursement-economics/). Both use confirmed Python/SQL skills and primary SEC observations with explicit scope and information timing. Neither claims employment, calibrated probabilities or investment authorization.

Install `requirements.txt`, run `python projects/2026-10-22/verify.py` from repository root, and open either `outputs/app.html` offline. Shared scripts stay in this parent folder. No network is needed for ordinary verification.

To intentionally recollect exactly the original source list and re-extract numerical cells, run `python projects/2026-10-22/acquire.py`, rebuild with `analyze.py`, then run `audit_original_html.py --live`. Review all changed hashes, mappings and evidence. Do not silently treat a source refresh as a new release acceptance. Initial collection used a scratch HTML cache; only numerical snapshots are published.

Three gates are documented in each project. Original-HTML audits were executed before publication; offline CI checks the pinned snapshots and recorded original-source audits. `verify.py` runs hand cases, independent method/source/SQL reconciliations and deletes outputs before a byte-identical clean rebuild. A fresh virtual environment separately confirms the pinned installation.

Actual browser acceptance:

```bash
npm install --prefix .oct22-browser playwright@1.56.1
.oct22-browser/node_modules/.bin/playwright install --with-deps chromium firefox webkit
NODE_PATH="$PWD/.oct22-browser/node_modules" node projects/2026-10-22/browser_test.cjs
```

The default run must produce 24 passing report/application entries (two projects × three engines × two viewports × two surfaces), with screenshots. `BROWSER_ENGINE=chromium` limits a local diagnostic only; it is not full acceptance. CI artifacts and main-commit evidence release are the publication record. Screenshots in each project are reviewed samples, not proof of physical-device or screen-reader coverage.

Publication is source-code/offline delivery, not live application hosting. [Primary-source and role research](RESEARCH.md), [verification record](verification.json).
