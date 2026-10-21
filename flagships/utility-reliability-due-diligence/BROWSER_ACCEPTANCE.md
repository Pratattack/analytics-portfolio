# Reproducible browser acceptance

The `flagship-browser-acceptance` GitHub Actions job is the execution record. A passing run must produce `browser_evidence/results.json` with **12 passing cases**: Chromium, Firefox and WebKit × desktop (1440 × 1000) and mobile (390 × 844) × local API and self-contained offline delivery. Failed runs cannot produce a PASS report. Screenshots are captured from the actual tested pages, not mocked UI.

## Acceptance flows

- Show the reconciled 2024 decision view, 2025 quarantine and failed predictive promotion gate.
- Reconcile the full utility count to the exported CSV; combine state and ownership filters.
- Select a utility using keyboard Enter; inspect source lineage and historical quarantine labels.
- Independently reconcile displayed scenario values to a closed-form annuity calculation at zero and positive discount rates; preserve negative outcomes.
- Exercise invalid native inputs, the $1 trillion capex boundary, recovery and five API/offline rejection cases.
- Search to an empty result, verify stale evidence/selection is removed, and recover.
- Simulate a temporary API outage and recover; delay an old response to verify rapid filter changes keep the newest result.
- Confirm offline delivery requests no external data, no uncaught page errors, no root overflow, and contained table scrolling.

To run locally after installing dependencies and regenerating outputs:

```bash
npm install --prefix .browser-runner playwright@1.56.1
./.browser-runner/node_modules/.bin/playwright install --with-deps chromium firefox webkit
NODE_PATH="$PWD/.browser-runner/node_modules" node flagships/utility-reliability-due-diligence/browser_test.cjs
```

Run those commands from the repository root. CI uses the same commands and an isolated localhost HTTP server for each delivery. Offline behavior is tested with its self-contained HTML served over localhost while detecting unexpected network requests; local `file://` execution is not separately claimed.

The main-only `flagship-browser-snapshot` job publishes the passing JSON and screenshots in an immutable commit-specific GitHub release. It requires both analytical and browser jobs to pass and verifies all 12 case statuses before packaging. Actions artifacts are temporary; the release ZIP is the durable evidence copy.

This is browser-engine and viewport acceptance, not a physical-device, assistive-technology, security certification or engineering-effectiveness review. Source discrepancies and failed model-promotion gates remain unresolved.
