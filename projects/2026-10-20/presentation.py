"""Decision briefs, self-contained data workbenches and deterministic financial figures."""
import html
import json
from pathlib import Path
import shutil
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sec_sources import BASE

STYLE = '''*{box-sizing:border-box}body{margin:0;background:#eef3f6;color:#183548;font:16px/1.55 system-ui,sans-serif}header{background:#102f43;color:white;padding:38px max(22px,calc((100vw - 1320px)/2))}header small{color:#a0d9d8;letter-spacing:.11em;text-transform:uppercase;font-size:12px}h1{font-size:clamp(28px,4vw,40px);line-height:1.15;margin:12px 0}header p{max-width:950px;color:#d1e4ed}main{max-width:1364px;margin:auto;padding:24px 22px}.card{background:white;border:1px solid #dde7ec;border-radius:12px;padding:24px;margin:0 0 20px;min-width:0}.notice{border-left:5px solid #c98727;background:#fff6e8;padding:16px 20px;border-radius:6px;margin-bottom:20px}.grid{display:grid;grid-template-columns:minmax(260px,.8fr) minmax(0,1.8fr);gap:22px}.grid>*{min-width:0}.controls{display:grid;grid-template-columns:minmax(0,1fr);gap:14px}.controls>label{min-width:0;max-width:100%}label{display:block;font-size:14px;font-weight:600;color:#3a5363}input,select,button{font:inherit;padding:11px;border-radius:6px;border:1px solid #b7cbd6;width:100%;min-width:0;max-width:100%;color:#183548;background:white}input[type=checkbox]{width:auto;margin-right:9px}button{background:#007f86;color:white;border:0;font-weight:650;cursor:pointer}button:hover{background:#00646b}:focus-visible{outline:3px solid #d39136;outline-offset:3px}h2{font-size:22px;line-height:1.25;margin:0 0 16px}h3{font-size:17px}.muted{font-size:14px;color:#5d7483}.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:18px 0}.stat{padding:16px;background:#eaf5f4;border-radius:8px;overflow-wrap:anywhere}.stat strong{display:block;font-size:clamp(21px,2.1vw,30px);line-height:1.3;margin-top:8px}.stat span{font-size:13px}.scroll{overflow:auto;width:100%;max-width:100%;min-width:0;contain:layout paint;margin:16px 0}table{border-collapse:collapse;font-size:13px;min-width:100%;white-space:nowrap}th,td{text-align:right;padding:11px 12px;border-bottom:1px solid #deeaee}th{background:#eaf2f5}th:first-child,td:first-child{text-align:left;max-width:420px;white-space:normal}img{max-width:100%;height:auto}a{color:#007c84}.links{display:flex;gap:14px;flex-wrap:wrap}.error{background:#fff0ec;color:#8a2f1f;border-left:5px solid #b94f35;padding:16px;border-radius:6px}footer{max-width:1364px;margin:auto;padding:15px 22px 32px;color:#5d7483;font-size:13px}#source-scope{overflow-wrap:anywhere}#status{margin-bottom:0}code{overflow-wrap:anywhere}@media(max-width:900px){.grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr}.card{padding:20px}main{padding:18px 14px}header{padding:28px 20px}}'''


def money(value): return f'${value:,.0f}'
def billion(value): return f'${value/1e9:,.2f}bn'
def escape(value): return html.escape(str(value))


def shell(title, subtitle, body):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+STYLE+'</style></head><body><header><small>Prathamesh Singh · independent finance diligence</small><h1>'+escape(title)+'</h1><p>'+escape(subtitle)+'</p></header><main>'+body+'</main><footer>Source snapshot: October 20, 2026. Independent research prototype. No employer engagement, actuarial opinion, credit commitment or realized business saving is claimed.</footer></body></html>'


def select(identifier, label, options, extra=''):
    return '<label>'+escape(label)+'<select id="'+identifier+'" aria-label="'+escape(label)+'" '+extra+'>'+''.join('<option value="'+escape(value)+'">'+escape(title)+'</option>' for value,title in options)+'</select></label>'


def input_field(identifier, label, value, low, high, step=1):
    return f'<label>{escape(label)}<input data-scenario id="{identifier}" aria-label="{escape(label)}" type="number" value="{value}" min="{low}" max="{high}" step="{step}" required></label>'


def make_app(payload, destination):
    insurance = payload['kind']=='insurance'
    title='Insurance reserve challenge workbench' if insurance else 'Retail REIT refinancing workbench'
    subtitle='Inspect disclosed loss-development triangles, model gates and tail sensitivity before commissioning actuarial diligence.' if insurance else 'Explore a five-year refinancing envelope using disclosed maturities, audited cash flows and explicit policy assumptions.'
    common='<label>Search '+('issuer or line' if insurance else 'issuer')+'<input id="search" aria-label="Search '+('issuer or line' if insurance else 'issuer')+'" placeholder="'+('e.g. WRB or liability' if insurance else 'e.g. KIM or Regency')+'"></label>'+select('selection','Choose '+('triangle' if insurance else 'issuer'),[])
    if insurance:
        controls=common+'<label><input id="show-excluded" type="checkbox">Include excluded triangles</label>'+select('method','Development method',[('volume','Volume-weighted chain ladder'),('median','Median individual development factors')],'data-scenario')+input_field('tail','Assumed tail factor',1,1,1.5,.01)+select('triangle-metric','Observed triangle measure',[('paid','Cumulative paid'),('incurred','Cumulative incurred')],'data-scenario')
        labels=['Modeled comparable unpaid','Disclosed comparable unpaid','Modeled less disclosed']
        observation=f"{payload['metrics']['numeric_triangle_cells']:,} numeric triangle cells · {payload['metrics']['eligible_triangles']} accepted models of {payload['metrics']['candidate_triangles']} disclosed triangles. Excluded lines remain inspectable."
    else:
        controls=common+input_field('decline','CFO level shortfall vs 2025 (%)',20,0,60)+input_field('spread','Incremental refinancing spread (bp)',200,0,1000)+input_field('rollover','Planned maturity rollover (%)',100,0,100)+input_field('capex','Assumed recurring capex (% of base CFO)',10,0,50)+input_field('fee','Assumed issuance fee (%)',1,0,10,.1)+input_field('floor','Required cash floor (% of base CFO)',10,0,100)+select('duration','Cash-flow recovery assumption',[('5','Five-year persistent level shortfall'),('2','Two-year shortfall; restore 2025 CFO in 2028')],'data-scenario')
        labels=['Minimum common rollover','New liquidity needed at planned rollover','Lowest projected closing cash']
        observation=f"Six issuers · {payload['metrics']['source_maturity_buckets']} disclosed maturity buckets · {billion(payload['metrics']['five_year_maturities'])} due in 2026–2030. The audited base is December 2025, not today's treasury position."
    body='<div class="notice">'+escape(observation)+'</div><div id="error" role="alert" class="error" hidden></div><div class="grid"><section class="card"><h2>Set the review scope</h2><div class="controls">'+controls+'<button id="reset" type="button">Reset review</button></div><p id="status" role="status" class="muted"></p><p class="muted">'+('Tail factors are assumptions. Method and tail envelopes are not confidence intervals.' if insurance else 'Scenario values are assumptions. New liquidity is a modeled requirement, not an observed financing gap. No asset sales, equity issuance or committed facility availability is assumed.')+'</p></section><div><section class="card"><h2>Decision screen</h2><p id="source-scope" class="muted"></p><div class="stats">'+''.join('<div class="stat"><span>'+label+'</span><strong id="result'+str(i)+'">—</strong></div>' for i,label in enumerate(labels,1))+'</div><p id="decision" role="status"></p><p class="muted">Tables scroll horizontally on narrow screens.</p><div id="details" class="scroll"></div></section><section class="card"><h2>Observed source evidence</h2><p id="evidence-caption" class="muted"></p><div id="evidence-table" class="scroll"></div></section></div></div><section class="card"><h2>Review the complete evidence</h2><div class="links"><a href="report.html">Executive evidence report</a><a href="executive_brief.md">Executive brief</a><a href="'+('reserve_review.csv' if insurance else 'financing_review.csv')+'">Decision table CSV</a><a href="source_lineage.csv">Source lineage CSV</a></div></section>'
    page=shell(title,subtitle,body)
    embedded=json.dumps(payload,ensure_ascii=True,separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    page=page.replace('</body>','<script id="research-data" type="application/json">'+embedded+'</script><script src="workbench.js"></script></body>')
    (destination/'app.html').write_text(page)
    shutil.copyfile(BASE/'workbench.js',destination/'workbench.js')


def figure(payload, destination):
    plt.rcParams.update({'svg.hashsalt':'finance-diligence-20261020','font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(11,5.8),layout='constrained')
    if payload['kind']=='insurance':
        m=payload['metrics'];values=[m['reported_comparable_unpaid'],m['model_unpaid'],m['model_unpaid']+m['one_tenth_tail_increment']]
        bars=ax.barh(['Disclosed comparable unpaid','Volume development / tail 1.00','Volume development / tail 1.10'],[v/1e9 for v in values],color=['#173e51','#00858d','#c1883d'])
        ax.set_xlabel('USD billions · same 31 accepted line/accident-year scopes')
        ax.set_title('Apparent reserve headroom depends on the unobserved tail',fontweight='bold',pad=15)
        for bar,value in zip(bars,values):ax.text(bar.get_width()+.4,bar.get_y()+bar.get_height()/2,f'{value/1e9:.2f}',va='center')
        ax.set_xlim(0,max(values)/1e9*1.17);ax.invert_yaxis()
        caption='No release authorization: different methods, development horizons, economic conditions and unallocated/older claims can change the interpretation.'
    else:
        rows=payload['rows'];labels=[r['ticker'] for r in rows];values=[r['maximum_scenario_liquidity_shortfall']/1e9 for r in rows]
        bars=ax.bar(labels,values,color=['#c1883d' if v>0 else '#00858d' for v in values])
        ax.set_ylabel('USD billions · modeled incremental liquidity')
        ax.set_title('Full refinancing alone can fail the cash-floor constraint',fontweight='bold',pad=15)
        ax.set_ylim(0,max(values)*1.2)
        for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+.03,f'{value:.2f}',ha='center')
        caption='Each issuer’s worst scenario in the disclosed grid. This is a conditional stress result, not its current financing requirement or a credit rating.'
    ax.grid(axis='x' if payload['kind']=='insurance' else 'y',alpha=.15);ax.set_axisbelow(True)
    fig.savefig(destination/'decision_evidence.svg',metadata={'Date':None,'Creator':'Independent finance diligence portfolio'});plt.close(fig)
    return caption


def report(payload,destination):
    m=payload['metrics'];insurance=payload['kind']=='insurance'
    caption=figure(payload,destination)
    if insurance:
        title='Insurance loss-reserve challenge'
        subtitle='Finance and actuarial diligence committee · decision: where to investigate, not how much reserve to release.'
        lead=f"The source audit retains {m['numeric_triangle_cells']:,} paid/incurred cells from six 2025 insurer filings. Of {m['candidate_triangles']} disclosed triangles, {m['eligible_triangles']} meet the selected development gates."
        finding=f"The default modeled comparable unpaid balance is {billion(m['model_unpaid'])}, versus {billion(m['reported_comparable_unpaid'])} disclosed for the same accepted scopes. A 1.10 tail factor adds {billion(m['one_tenth_tail_increment'])}. Treat the gap as model-risk evidence, not excess capital."
        validation=f"Across {m['diagnostic_cells']} masked one-step cells, development WAPE is {100*m['model_wape']:.2f}% versus {100*m['baseline_wape']:.2f}% for repeating the latest increment. The current-disclosure cohort and revised historical values prevent an as-released forecasting claim."
        limits='Net allocated-claim scope; different line/accident-year horizons; omitted older claims and unallocated expenses; sparse oldest development factors; potential inflation, settlement and reinsurance changes; no independent actuarial review. Historical triangle columns may be unaudited supplemental disclosure. Predictive and capital-release promotion remain false.'
        headers=['Issuer / line','Disclosed unpaid','Volume model','Tail 1.10 increment']
        table_rows=[[r['ticker']+' / '+r['line'],money(r['reported_unpaid']),money(r['chain_ladder_unpaid']),money(r['tail_10pct_increment'])] for r in payload['rows'][:12]]
        action='Review the largest dollar tail sensitivities first. Obtain original actuarial selections, claims handling changes, reinsurance detail, segment reconciliation and an independent reserve opinion before discussing capital returns.'
    else:
        title='Retail REIT refinancing resilience'
        subtitle='Treasury and finance committee · decision: conditional rollover and liquidity envelope for a five-year annual-base plan.'
        lead=f"Six original 2025 filings disclose {billion(m['disclosed_face_principal'])} of face principal; {billion(m['five_year_maturities'])} falls in 2026–2030. Parent, operating-partnership and unconsolidated-JV scopes are handled explicitly."
        finding=f"All six pass the unchanged-CFO/full-rollover baseline. {m['infeasible_scenarios']} of {m['scenario_count']} issuer/scenario combinations cannot satisfy all five cash floors using rollover alone. Only {m['robust_feasible_issuers']} issuers remain feasible across the expanded grid."
        validation=f"The {m['comparative_cfo_observations']} observed CFO values produce {m['historical_cfo_changes']} annual changes. The worst decline is {100*m['worst_observed_annual_cfo_change']:.2f}%, so the original 30% grid is supplemented by a 40% challenge. These shocks have no assigned probabilities. Analytical rollover bounds are independently reconciled to a linear-programming solver."
        limits='Frozen December 2025 annual base, not current liquidity. CFO shocks are fixed level shortfalls, not compounded annual declines; the main grid holds them for five years, while a separate two-year/recovery case tests that conservatism. Historical severity does not establish persistence or probability. Constant cash distributions; assumed recurring capex, fees, cash floor and refinancing spreads; no new acquisitions, asset sales or equity issuance; no assumed available facilities; consolidated schedules exclude unconsolidated JV debt. Debt beyond 2030 is outside the runoff horizon. Real covenants, tax distributions and market access require additional diligence.'
        headers=['Issuer','2026–2030 principal','Baseline passes','Expanded grid passes','Worst modeled liquidity']
        table_rows=[[r['ticker'],money(r['five_year_maturities']),str(r['baseline_feasible']),str(r['robust_feasible_without_new_liquidity']),money(r['maximum_scenario_liquidity_shortfall'])] for r in payload['rows']]
        action='Validate undrawn committed facilities, extension rights, covenant headroom, recurring property capex and legally permissible distributions. Use the cash-floor frontier to size a funding discussion; do not infer refinancing approval from a favorable ratio.'
    table_html='<div class="scroll"><table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in table_rows)+'</tbody></table></div>'
    body='<div class="notice">'+escape(action)+'</div>'+''.join('<section class="card"><h2>'+h+'</h2><p>'+escape(p)+'</p></section>' for h,p in [('Observed evidence',lead),('Decision implication',finding),('Validation and uncertainty',validation)])+'<section class="card"><h2>Financial evidence</h2><img src="decision_evidence.svg" alt="'+escape(caption)+'"><p class="muted">'+escape(caption)+'</p>'+table_html+'</section><section class="card"><h2>Limits and adoption gates</h2><p>'+escape(limits)+'</p></section><section class="card"><div class="links"><a href="app.html">Interactive workbench</a><a href="executive_brief.md">Executive brief</a><a href="source_lineage.csv">Source lineage CSV</a><a href="'+('triangle_inventory.csv' if insurance else 'debt_basis_bridge.csv')+'">'+('Model exclusions CSV' if insurance else 'Debt basis bridge CSV')+'</a></div></section>'
    (destination/'report.html').write_text(shell(title,subtitle,body))
    brief=f'# {title}\n\n## Decision and owner\n\n{subtitle}\n\n## Evidence\n\n{lead}\n\n{finding}\n\n## Validation\n\n{validation}\n\n## Recommended diligence\n\n{action}\n\n## Limits\n\n{limits}\n\nAll scenarios and model estimates are separated from observations. No realized saving, employer work, regulatory capital approval or investment recommendation is claimed.\n'
    (destination/'executive_brief.md').write_text(brief)
    make_app(payload,destination)


if __name__=='__main__':
    from insurance_pipeline import build as insurance
    from reit_pipeline import build as reit
    for slug,builder in [('insurance-reserve-capital-review',insurance),('retail-reit-refinancing-review',reit)]:
        out=BASE/slug/'outputs';report(builder(out),out)
        print(slug,'decision outputs and workbench generated')
