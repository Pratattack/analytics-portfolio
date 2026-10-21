# Clean-environment execution record

The source-authoring run created a fresh Python 3.12 virtual environment, installed exactly `requirements.txt`, and ran `verify_all.py` successfully. No pre-existing analysis site-packages or source-site access was required. The verifier launches two isolated fresh Python processes and compares every non-SQLite generated output byte with the checked-in outputs. Both projects passed. SQLite files are regenerated locally and excluded because binary database layout is not the scientific reproducibility target.

The separately executed original-document audit reconciled 52,127 numeric facts and contexts across 14 original SEC filings using an independent standard-library parser. Those original HTML files are not redistributed; `acquire.py --rebuild-inline --download-missing` retrieves pinned originals to rerun that audit. Normal clean CI verifies supplied numerical snapshots and the audit's source hashes, without claiming a new original-document audit.

Browser acceptance is separate. Only the actual `finance-browser-acceptance` job and its `results.json` establish whether all 24 report/application cases passed. The main-only release job validates that result before publishing screenshot evidence. Emulated viewport tests do not establish physical-device, assistive-technology, stakeholder, actuarial or lender approval.
