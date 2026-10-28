# Prathamesh Singh — portfolio website

Public portfolio for prathameshsingh.com. Buildless HTML/CSS/JavaScript; self-hosted Inter and Instrument Serif fonts. No framework, package installation or runtime database is needed. The analytics projects remain separate and unchanged.

## Build

From the analytics-portfolio repository root, with this source in `website/`:

```sh
python3 website/scripts/fetch_assets.py
python3 website/scripts/build.py --projects-source .
python3 website/scripts/verify.py
```

Publish `website/dist/` with any static host. The managed Sites checkout uses the same files at its root.

## Add a future project

1. Review its README, implementation, source evidence and limitations.
2. Add one entry to `website/content/projects.json` with a unique slug, source path, date, category, data type, question, audience, data, methods, findings, implications, limitations and tools.
3. For an existing external application, set `externalDemo`; otherwise put self-contained reports/apps in its `outputs/` folder. Keep shared reproduction toolkits in the parent repository.
4. Run the build and verification commands. Check the new case, filter behavior and demo in a browser, then redeploy.

The generator creates the library, case pages, sitemap, offline ZIP packages and hosted copies of static reports/workbenches. Homepage feature links are curated separately in `dist/index.html`; new projects are not automatically featured.

## Edit the design and personal details

Homepage: `dist/index.html`. Shared styling: `dist/assets/site.css`. Search/filter behavior: `dist/assets/library.js`. Resume: `dist/assets/prathamesh-singh-resume.pdf`. Font license and credits: `dist/assets/Inter-LICENSE.txt`, `dist/assets/credits.txt`.

## Scope and verification

19 case studies, 13 locally hosted interactive workbenches, one external Streamlit dashboard, five report-only projects. Actual results are separated from hypothetical scenarios. Source projects are pinned to commit 734d84e3ce8e4ad187b4319d205dec3e461f370f for this release.

Browser QA was blocked by automatic approval review because the user previously prohibited browser operation. Static link, JavaScript, filter logic, content/asset and download-package checks are recorded in verification.json. This does not certify mobile rendering or interactive workbench recalculation.

## Hosting

The current host is ChatGPT Sites. No paid hosting service or subscription was purchased in this task. GoDaddy remains the registrar. Apex and www custom domains have been registered with the host and await user DNS configuration; see LAUNCH.md. Both are intended to serve the same website, with the apex declared canonical.

The approved public resume is included. The asset helper downloads the licensed Inter and Instrument Serif fonts from their upstream GitHub distributions with pinned SHA-256 checks. Source licenses are bundled. See live-verification-summary.json for live-check limitations.

## Editorial refinement

The approved homepage introduces Prathamesh by name and uses actual mortgage, bank and rental evidence. Case pages lead with a short finding and decision relevance, with methods in an accessible disclosure. The library displays concise evidence summaries. All site-controlled HTML, JS, SVG, Markdown and text copy is checked for em dashes. Hosted report copies receive explicitly reviewed presentation-only rewrites through scripts/copy_refinement.py; source data files are copied unchanged. The static verifier now also checks CSS asset paths to prevent missing fonts and background files.


October 2026 update: the library now includes 21 projects. New projects live under `projects/2026-10-27/`. To add another, reproduce and verify its outputs, append `portfolio_registry.json`, add a reviewed case record to `website/content/projects.json`, run the site builder with the full repository as `--projects-source`, and run the website verifier. Retain existing slugs and keep observations separate from scenario assumptions.
