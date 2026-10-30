# Workforce Replacement & Recruiting Capacity

At the trailing 12-month private-sector separation-rate average of 3.56% per month, a hypothetical employer growing from 1,000 to 1,100 staff needs 548 hires, not 100. The difference is replacement demand under the stated recurrence.

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
National industry estimates are not firm-specific turnover probabilities. Total separations include quits, layoffs and other exits. Rates use BLS employment denominators and are rounded. The recurrence instead applies the chosen rate to beginning-month modeled staff, an explicit planning approximation. Same-month hires and exits are not modeled separately. Staffing, growth, capacity and cost inputs are hypothetical. Revised and concurrently seasonally adjusted history is not a real-time vintage backtest. Overlapping three-month targets are dependent, so no significance test or forecast interval is claimed. Latest August estimates are preliminary. Current staffing decisions need company-level evidence.

Source URLs, retrieval timestamps, observation periods and complete-download hashes are retained in `data/source_manifest.json`. Some upstream files may be revised; this release pins the retrieved history rather than claiming real-time vintages. Original code is MIT licensed. Government source material is separately attributed and implies no endorsement. Browser rendering and keyboard interaction were not tested because the owner excludes browser operation.

## Verify upstream sources
Run `python fetch_sources.py --cache /path/to/separate-cache` to retrieve the original official files and compare complete-download hashes. Upstream revisions are retained separately. Never silently refresh the pinned inputs. The JOLTS project also reconstructs and compares selected observations.
