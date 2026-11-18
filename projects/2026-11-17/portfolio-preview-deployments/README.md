# Portfolio Preview Deployments

A pull request workflow that rebuilds and tests prathameshsingh.com before a change is published. The GitHub Actions runner serves the generated static site to Chromium at desktop and mobile viewport sizes, then uploads the checked preview and build log.

See the [workflow](../../../.github/workflows/portfolio-preview.yml), [browser checks](../../../website/scripts/check_preview.cjs), and [first successful run](https://github.com/Pratattack/analytics-portfolio/actions/runs/44236283461).

To try a preview, download the preview artifact from a passing run, extract it, and start `python3 -m http.server 8000 --bind 127.0.0.1` in the extracted directory. Open http://127.0.0.1:8000/.

The first passing run built 31 case studies and checked 818 links and asset references and 31 download archives. Those figures describe the first build. Each subsequent run records its own counts and browser results. Preview ZIPs expire after seven days. Production is published separately through ChatGPT Sites.
