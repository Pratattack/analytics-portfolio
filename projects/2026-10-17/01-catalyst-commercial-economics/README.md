# Catalyst Commercial Economics

Independent portfolio simulation for Prathamesh Singh. Not employer work or evidence of professional tenure. All operational data and outcomes are synthetic.

## Run

Python 3.10+ with standard library only. No API keys, packages or network required.

```bash
python pipeline.py
python -m unittest -v
```

Run from this directory. Review `outputs/report.html` in a browser, `outputs/decision_memo.md`, and Excel-compatible CSV outputs. `analysis.sql` contains the analytical SQL used by the pipeline. Monetary values are USD. See the memo for definitions, assumptions, decision rationale and limitations. Outputs are deterministic with fixed seeds.

## Review and transfer

See root `verification.json` for three separate automated verification stages, including artifact reproducibility. These are automated checks, not three independent human reviews. Published as source code in this public portfolio; no hosted application deployment is claimed. Publish this directory under its own public repository, or as a distinct folder in a public portfolio repo. Keep the raw resume and personal contact details out of public repositories.

## Role mapping

Ketjen: pricing/margin/mix, contract scenarios, customer profitability, documented repeatable analysis.

## Next steps for real adoption

Replace synthetic inputs with licensed, governed data; obtain domain validation; reconcile to source systems; extend scenario assumptions; add deployment-specific CI and access governance. This is a reproducible analytical case, not a production-integrated company platform.
