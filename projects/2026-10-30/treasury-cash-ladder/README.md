# Treasury Cash Ladder & Liquidity Constraints

Using 2026-10-29 quotations, the illustrative $1 million plan earns $6,279 above zero-yield cash while preserving a $100,000 reserve after $700,000 of scheduled and stress payments. This is a modeled bill return, not an executed trade.

## Start here
Open `outputs/report.html` for findings, evidence and limitations. Open `outputs/workbench.html` for a self-contained interactive scenario tool. No account, server, remote font, API key or analytics is required. Keep the extracted folder structure for CSV links.

## Reproduce
Python 3.11 or newer and Node.js 18 or newer are required for full verification.

```bash
python -m pip install -r requirements.txt
python analyze.py
python verify.py
```

`data/` contains pinned official-source inputs and extraction metadata. `data_hashes.json` identifies exact input bytes. `reconcile.sql` independently checks selected results. `outputs/` contains verified SVG charts, CSV evidence and the offline tool. `tests/` includes model boundaries and independently implemented JavaScript/Python parity cases. `docs/executive_memo.md` explains decision use.

## Data and interpretation
Indicative secondary-market bid quotations are not executable offers. Fixed 28-, 56- and 91-day tenors stand in for actual security settlement and maturity dates. No reinvestment, early sale, bid-ask spread, taxes, lot sizes, holiday adjustment or credit facility is modeled. Cash earns zero in the baseline. Actual cash forecasts, offers and security identifiers are required before implementation. Reserve and payments are hypothetical; this is not a forecast of a real company’s cash.

Source URLs, retrieval timestamps, observation periods and complete-download hashes are retained in `data/source_manifest.json`. Some upstream files may be revised; this release pins the retrieved history rather than claiming real-time vintages. Original code is MIT licensed. Government source material is separately attributed and implies no endorsement. Browser rendering and keyboard interaction were not tested because the owner excludes browser operation.

## Verify upstream sources
Run `python fetch_sources.py --cache /path/to/separate-cache` to retrieve the original official files and compare complete-download hashes. Upstream revisions are retained separately. Never silently refresh the pinned inputs. The JOLTS project also reconstructs and compares selected observations.
