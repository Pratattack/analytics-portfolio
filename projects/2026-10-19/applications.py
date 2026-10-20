"""Small offline decision workbenches built from audited pipeline outputs."""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def rows(path):
    with path.open() as source:
        return list(csv.DictReader(source))


def build_application(project, output, kind):
    metrics = json.loads((output / 'metrics.json').read_text())
    if kind == 'airline':
        history = rows(output / 'site_history.csv')
        discovery = {(r['carrier'], r['airport']): r for r in history if r['year'] == '2024' and r['discovery_eligible'] == '1'}
        diagnostic = {(r['carrier'], r['airport']): r for r in history if r['year'] == '2026'}
        sites = []
        for key, row in sorted(discovery.items()):
            later = diagnostic.get(key)
            sites.append([*key, float(row['excess_minutes']), float(row['carrier_minutes']), float(later['excess_minutes']) if later else None, float(later['flights']) if later else None, int(later['months']) if later else 0])
        data = {'kind': kind, 'metrics': metrics, 'sites': sites}
        title = 'Airline investigation workbench'
        description = 'Choose investigation priorities using 2024 evidence; inspect the unchanged 2026 diagnostic. This is an investigation queue, not evidence of avoidable delays.'
        controls = '''<label>Ranking policy<select id="policy" aria-label="Ranking policy"><option value="peer">Peer excess</option><option value="raw">Raw carrier-delay burden</option></select></label>
<label>Investigation slots (1–20)<input id="slots" type="number" value="10"></label>
<label>Maximum sites per airport (1–4)<input id="cap" type="number" value="2"></label>
<label>Carrier or airport search<input id="search" type="search" placeholder="e.g. AA or DFW"></label>
<label>Assumed cost per minute (USD)<input id="price" type="number" value="60"></label>
<label>Assumed recoverable fraction (%)<input id="fraction" type="number" value="10"></label>
<label>Assumed investigation cost per site (USD)<input id="sitecost" type="number" value="100000"></label>'''
    else:
        data = {'kind': kind, 'metrics': metrics, 'banks': rows(output / 'review_queue.csv')}
        title = 'Bank funding economics workbench'
        description = 'Explore the observed expense bridge and a separate hypothetical repricing case. Endpoint-average proxy rates do not identify causal pricing power or actual retention.'
        controls = '''<label>Modeled interest-bearing balance (USD)<input id="balance" type="number" value="1000000000"></label>
<label>Current proxy annual rate (%)<input id="rate" type="number" step="any" value="2.5"></label>
<label>Proposed cut (basis points)<input id="cut" type="number" step="any" value="25"></label>
<label>Targeted balance share (%)<input id="share" type="number" step="any" value="25"></label>
<label>Attrition on targeted balances (%)<input id="loss" type="number" step="any" value="5"></label>
<label>Replacement annual rate (%)<input id="replacement" type="number" step="any" value="4.5"></label>
<label>Annual fixed cost (USD)<input id="fixed" type="number" value="100000"></label>
<label>Review-queue asset bucket<select id="bucket" aria-label="Review-queue asset bucket"><option value="all">All review-queue banks</option><option value="under_1bn">Under $1bn</option><option value="1_to_10bn">$1bn to $10bn</option><option value="over_10bn">$10bn and above</option></select></label>'''
    payload = json.dumps(data, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>''' + title + '''</title><style>
*{box-sizing:border-box}body{font:16px/1.6 Arial,sans-serif;background:#eff4f6;color:#16313f;margin:0;padding:28px}main{max-width:1180px;margin:auto}header{background:#133b50;color:white;border-radius:14px;padding:32px}h1{font-size:32px;line-height:1.2}h2{font-size:23px}section{background:white;padding:26px;border-radius:12px;margin-top:20px}.controls{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}label{display:flex;flex-direction:column;font-size:14px;font-weight:bold}input,select,button{font:inherit;min-height:44px;padding:8px;border:1px solid #88a6b3;border-radius:5px;max-width:100%}input:focus,select:focus,button:focus,a:focus{outline:3px solid #d6a144;outline-offset:3px}button{background:#127b87;color:white;cursor:pointer;margin-top:16px}a{color:#087b83}.error{color:#9d1b26;border-left:4px solid #9d1b26;padding:12px;background:#fff2f3}.error:empty{display:none}.cards{display:flex;gap:20px;flex-wrap:wrap}.card{flex:1;min-width:190px;background:#edf6f7;padding:18px}.value{font-size:27px;font-weight:bold}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;white-space:nowrap;font-size:14px}th,td{padding:10px;text-align:left;border-bottom:1px solid #dbe6eb}th{background:#edf4f7}.note{color:#526b78;font-size:14px}footer{padding:20px 0}@media(max-width:650px){body{padding:12px}header,section{padding:20px}.controls{grid-template-columns:1fr}h1{font-size:26px}.card{min-width:100%}}
</style></head><body><main><header><p>Independent portfolio research · source cutoff October 19, 2026</p><h1>''' + title + '''</h1><p>''' + description + '''</p></header>
<section><h2>Observed research result</h2><p id="observed"></p><p class="note">These empirical findings are separate from all scenario assumptions below.</p></section>
<section><h2>Explore the decision</h2><form id="controls" novalidate><div class="controls">''' + controls + '''</div><button id="reset" type="reset">Reset assumptions</button></form><p id="error" role="alert" class="error"></p></section>
<section><h2>Decision output</h2><div id="results" aria-live="polite"></div><p id="status" role="status"></p><div class="scroll"><table><thead id="head"></thead><tbody id="body"></tbody></table></div></section>
<footer><a href="report.html">Read the evidence report</a> · <a href="executive_memo.md">Executive memo</a><p class="note">Python/SQL source and complete exports are reproduced with the documented pipeline. No live business savings, deployment approval or employer experience is claimed.</p></footer></main>
<script type="application/json" id="data">''' + payload + '''</script><script src="app.js"></script></body></html>'''
    (output / 'app.html').write_text(document)
    (output / 'app.js').write_text((BASE / 'workbench.js').read_text())
