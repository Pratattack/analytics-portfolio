"""Create review memos, evidence charts, result exports and interview notes."""
import base64,csv,html,io,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ROOT,inputs,simulate,valuation
OUT=ROOT/'outputs/fm-20261101';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#234057','text.color':'#17334c'})
CSS='''body{margin:0;background:#101923;color:#e8eff5;font:17px/1.65 Arial,sans-serif}main{max-width:960px;margin:auto;padding:64px 28px}h1{font-size:clamp(32px,5vw,54px);line-height:1.1;letter-spacing:-1.4px;max-width:860px}h2{font-size:24px;margin-top:42px}p{max-width:84ch}a{color:#7cc8ff}small,.muted{color:#b1c2cf}strong{color:white}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:right;border-bottom:1px solid #3c4d5c;padding:10px}th:first-child,td:first-child{text-align:left}figure{margin:30px 0;background:white;padding:16px;color:#17334c}figure svg{width:100%;height:auto}figcaption{font-size:13px;line-height:1.5}li{margin:10px 0}.lead{font-size:22px;color:#b8daf1}.stamp{font-size:13px;letter-spacing:1px;text-transform:uppercase;color:#7cc8ff}.scroll{overflow-x:auto}@media print{body{background:white;color:#172b3a;font-size:10pt}main{padding:0}h1{font-size:28pt}h2{font-size:15pt;margin-top:16px}strong,a{color:#172b3a}figure{break-inside:avoid}table{font-size:9pt}.muted,small{color:#445} }'''
def page(title,body):return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style><main>'+body+'</main></html>'
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+html.escape(str(x))+'</th>'for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>'for x in row)+'</tr>'for row in rows)+'</tbody></table></div>'
def money(x):return f'${x:,.0f}m'
def chart(sym,results):
 rows=results['base']['forecast'];fig,ax=plt.subplots(figsize=(9,3.4),layout='constrained');xx=range(5)
 for offset,key,label,col in [(-.24,'cfo','Operating cash flow','#235c83'),(0,'capital','Cash capital investment','#9fb1c1'),(.24,'buybacks','Repurchases','#cd9535')]:
  vals=[r['fleet_capex']+inputs(sym)['drivers']['other_capex']['base'][i] if key=='capital'and sym=='URI' else inputs(sym)['drivers']['other_capex']['base'][i]if key=='capital'else r[key] for i,r in enumerate(rows)]
  ax.bar([x+offset for x in xx],vals,.23,label=label,color=col)
 ax.set_xticks(list(xx),[str(2027+x)for x in xx]);ax.set_ylabel('USD millions');ax.set_xlabel('Hypothetical 12-month periods ending 30 September');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.legend(frameon=False,ncol=3,loc='upper left',fontsize=9)
 b=io.StringIO();fig.savefig(b,format='svg');fig.savefig(OUT/f'{sym}_Cash_Allocation.png',dpi=160);plt.close(fig)
 return '<figure role="img" aria-label="Base scenario operating cash, capital spending and repurchases for five forecast periods">'+b.getvalue()+'<figcaption>Model calculations, base scenario. All future amounts are assumptions-based, not observed outcomes or company guidance. Source inputs: SEC filings listed below.</figcaption></figure>'

def main():
 manifest=json.loads((ROOT/'data/filing_manifest.json').read_text())
 for sym in ['URI','CROX']:
  d=inputs(sym);res=json.loads((ROOT/f'outputs/{sym}_reference.json').read_text());b=res['base']['forecast'][0];v=res['base']['valuation'];last=res['base']['forecast'][-1];name=d['company']
  if sym=='URI':
   title='How much can United Rentals return after funding its fleet?'
   opening=f'The base scenario supports {money(b["buybacks"])} of first-period repurchases against an illustrative $1,500m ceiling. Equipment investment and working capital absorb cash even as modeled revenue grows.'
   findings=[f'<strong>Investment determines the distribution budget.</strong> Operating cash of {money(b["cfo"])} less net investing outflow of {money(-b["cfi"])} leaves {money(b["cfo"]+b["cfi"])}. With opening cash of $153m, a $150m reserve and a $500m dividend budget, repurchases fall to {money(b["buybacks"])}.',
    '<strong>Stronger demand can still reduce buybacks.</strong> The upside case spends $6,000m on fleet versus $5,350m in base. First-period repurchases are $448m, below base, despite higher operating cash. This is a choice between reinvestment and distributions, not evidence that growth destroys value.',
    f'<strong>The price requires assumptions this model does not establish.</strong> Holding five explicit cash flows fixed, the $1,170.05 quote implies a {v["implied_terminal_ebit_margin"]:.1%} terminal operating margin at 10% WACC, 2.5% growth and 10% terminal ROIC. That unusually demanding conditional result may reflect an incomplete operating or terminal model. It does not prove mispricing.']
   decision='Use a cash waterfall to set repurchase capacity after fleet investment, required principal funding and a cash reserve. Revisit the budget when fleet yield, used-equipment proceeds or receivable days change. The scenario is not a proposed board authorization.'
   choice='The most consequential operating choice is the fleet cohort approximation: a legacy depreciation rate, half-year depreciation on new purchases and assumed disposal ages connect investment to fleet capacity and earnings. Exact asset cohorts and utilization are unavailable. Gross fleet starts at a rounded $25bn, so small changes should not be interpreted as precise capacity estimates.'
   against='The strongest argument against the low DCF indication is that future fleet productivity, acquisition benefits or sustainable returns could be stronger than this deliberately simplified build captures. Conversely, recent cash conversion may not persist. Terminal value contributes 74.9% of base enterprise value. Changing discount rates and terminal reinvestment can dominate the apparent gap to price.'
   nextdata='Asset-level depreciation and disposal cohorts, owned-fleet utilization by category, rental rate versus mix, maintenance spending and an instrument-level debt maturity schedule would most improve the model.'
   change='The base cash-only threshold is about $9,527m of EBITDA to fund the full $1,500m repurchase ceiling while holding working capital, asset sales and capex unchanged. This is a local cash stress calculation, not a realistic standalone operating forecast. A durable improvement in yield or a defensible reduction in investment would change the allocation conclusion.'
  else:
   title='Can Crocs fund buybacks while reducing debt?'
   opening=f'The base scenario funds $600m of first-period repurchases and {money(b["debt_sweep"])} of residual debt repayment. The case depends on assumed brand contribution margins. A lower share count alone does not establish an operating recovery.'
   findings=[f'<strong>Buybacks and debt reduction compete for the same cash.</strong> First-period operating cash of {money(b["cfo"])} less $80m capex leaves {money(b["cfo"]+b["cfi"])}. Opening cash above the $150m reserve adds about $13m. After $600m repurchases, {money(b["debt_sweep"])} remains for debt repayment.',
    '<strong>A noncash charge is different from trading pressure.</strong> The downside case combines weaker sales and contribution margins with a hypothetical $200m nondeductible impairment. The charge reduces earnings and assets, but does not itself reduce cash. Downside operating cash is $363m and net debt / EBITDA reaches 1.73x. The impairment is not a forecast of an actual charge.',
    f'<strong>The base DCF has little room for error.</strong> Its ${v["per_share"]:.2f} per-share indication is close to the dated $150.52 quote. With five cash flows fixed, the quote implies a {v["implied_terminal_ebit_margin"]:.1%} terminal EBIT margin at 11% WACC, 2% growth and 15% terminal ROIC. Terminal value contributes 64.4% of enterprise value.']
   decision='Evaluate repurchases alongside brand cash contribution and debt reduction. Treat faster EPS growth cautiously when it mainly reflects fewer shares. Keep distributions conditional on cash generation rather than assuming a fixed repurchase pace through a brand downturn.'
   choice='The most consequential operating choice is the contribution margin assigned to each brand before D&A and SG&A. Base Crocs contribution is 65%, with HEYDUDE at 46% rising to 48%. These are analyst assumptions, not disclosed brand cash margins. Because brand D&A allocation is unavailable, the model uses a combined PPE and finite-intangible depreciation pool.'
   against='The strongest argument against the base conclusion is that assumed contribution margins and modest SG&A improvement overstate sustainable cash profitability. The DCF range spans about $71 to $213 across the three operating cases at the same WACC and growth. This is a scenario range without assigned probabilities, not a statistical confidence interval.'
   nextdata='Brand and channel contribution margins, promotion intensity, returns, unit volumes and prices, geographic tariff exposure and financing terms would most improve the analysis. Sell-in revenue is not proof of consumer sell-through.'
   change='A cash-only first-period EBITDA threshold of about $854m funds the $600m ceiling with other cash drivers unchanged. Base EBITDA is $1,022m. A persistent contribution-margin decline, slower inventory conversion or refinancing shortfall would support reducing the ceiling. Evidence of brand recovery that survives these tests would strengthen it.'
  compare=table(['First forecast period','Base','Downside','Upside'],[[label]+[fmt(res[c]['forecast'][0][key])for c in ['base','down','up']]for label,key,fmt in [('Revenue','revenue',money),('Operating cash','cfo',money),('Repurchases','buybacks',money),('Debt at close','closing_debt',money),('Net debt / EBITDA','net_leverage',lambda x:f'{x:.2f}x'),('Modeled EPS','eps',lambda x:f'${x:.2f}')]])
  sources='<ol>'+''.join(f'<li><a href="{x["url"]}">{x["id"]}</a>. Consolidated statements, business and risk disclosures. Retrieved {x["retrieved_at"][:10]} UTC.</li>'for x in manifest if x['id'].startswith(sym))+f'<li><a href="{d["market"]["price_source"]}">Closing-price history</a>, corroborated with <a href="{d["market"]["price_corroboration"]}">second vendor</a>. Price: 30 October 2026. Shares: {d["market"]["shares_millions"]:.6f}m, cover page dated {d["market"]["shares_date"]}. September balances are not October balances.</li></ol>'
  context=json.loads((ROOT/'data/context_sources.json').read_text()).get(sym,[])
  body=f'<p class="stamp">Prathamesh Singh · Financial modeling research · 2 November 2026 · Review draft</p><h1>{title}</h1><p class="lead">{opening}</p><p><strong>Decision:</strong> {decision}</p><h2>Three findings</h2><ol>'+''.join('<li>'+x+'</li>'for x in findings)+'</ol>'+chart(sym,res)+compare+f'<p class="muted">All comparison values are hypothetical 12-month periods ending 30 September 2027. Downside and upside are assumption bundles, not probabilities or forecasts issued by management.</p><h2>The modeling choice to defend</h2><p>{choice}</p><h2>The strongest challenge</h2><p>{against}</p><h2>What would change the conclusion?</h2><p>{change}</p><p>{nextdata}</p><h2>Scope and limitations</h2><p>Three annual periods, an LTM bridge and five forecast periods connect operations, the balance sheet, cash flow and financing. Latest actual balances are 30 September 2026. The valuation uses the 30 October price and latest dated cover-page shares. The first forecast cash flow is prorated 11/12 using equal months, which ignores seasonality. Interest is charged on opening debt, with financing assumed at period end. Future acquisitions and noncash lease additions are excluded. Other assets and non-payable liabilities remain constant. Working-capital cost definitions differ between reported calibration and the simplified forecast. Debt repayment budgets and refinancing fractions are hypothetical and do not represent secured funding or contractual maturities. No tax refunds are modeled on losses. Operating lease expense remains in earnings, so operating leases are excluded from valuation debt. Stock compensation stays an economic expense in DCF.</p><p>Per-share EPS uses a fixed reference-price settlement proxy for stock compensation and buybacks. It is not an award-level dilution forecast. The valuation share count remains the latest reported cover-page count. These are educational decision models, not stock recommendations. No claim of unique analysis is made.</p><h2>Sources</h2>'+sources
  body+='<h2>Additional company materials</h2><ul>'+''.join(f'<li><a href="{url}">{label}</a></li>'for label,url in context)+'</ul>'
  (OUT/f'{sym}_Executive_Memo.html').write_text(page(title,body))
  research=f'''# {name}: research and model notes

Research cutoff: 2 November 2026. Market price cutoff: 30 October 2026.

## Decision and business economics

{decision}

'''+('United Rentals rents owned equipment and provides related services. Rental yield, average equipment cost, disposal economics and reinvestment determine cash conversion. Its annual report describes a fragmented market with local, regional and national competitors and equipment vendors that sell and rent. Scale can aid purchasing and fleet transfers, but it does not eliminate rate, utilization or resale risk. General and specialty equipment have different economics. This model separates owned rental revenue from ancillary rental and equipment sales, but does not claim a fully disclosed segment utilization model. Public evidence is adequate for a conditional capital-allocation analysis, not an exact fleet-cohort forecast.'if sym=='URI'else'Crocs sells through wholesale and direct channels under Crocs and HEYDUDE. The model preserves four disclosed brand-channel revenue streams. Channel growth alone does not identify price, volume, returns or promotion. The annual report names Nike, adidas, Deckers, Birkenstock, Steven Madden, Wolverine and VF among competitors. Their brand and channel mixes differ, so no peer multiple or peer-derived WACC is imposed. Public evidence supports a brand and cash-allocation stress model, but does not identify brand cash contribution precisely.')+f'''

## Historical bridge

Annual 2023, 2024 and 2025 figures are taken from the downloaded annual filings. Comparative nine-month 2025 and nine-month 2026 flows use the latest quarterly filing. LTM = annual 2025 + nine-month 2026 - nine-month 2025. Balance-sheet stocks use dated balances, never this flow formula. Restated comparative values are preferred where present. Missing data remain missing unless a zero is explicitly disclosed. Each selected numeric fact has a context, dimension, source ID and source hash in source_lineage.csv. Annual and September-ending forecast dates are deliberately different.

The workbook adds reported impairment back to historical recurring operating income where available, while showing the charge and reported operating income separately. This is an analytical reconciliation. It does not imply the loss was harmless. Crocs FY2025 reported net loss and unusual tax history remain visible. Historical EPS is omitted rather than approximated using period-end shares.

## Assumptions and conflicting evidence

{choice}

Base is a modeling reference, not a probability-weighted expected outcome. Growth and contribution margins are analyst scenarios bounded by downside and upside inputs. Management guidance informed the first investment budget only and is not relabeled as guidance for a September-ending forecast year. Historical strength supports testing continued cash generation. Cyclicality, competitive pricing, investment needs and incomplete cost disclosures support the downside. The result is deliberately conditional.

'''
  for k,x in d['drivers'].items():research+=f'- **{k}**: base {x["base"]}; downside {x["down"]}; upside {x["up"]}. {x["basis"]}\n'
  research+=f'''
## Valuation and reverse valuation

DCF discounts unlevered cash flow after stock compensation expense. Terminal reinvestment = terminal growth / terminal ROIC. Base WACC is {d['globals']['wacc']:.0%}, terminal growth {d['globals']['terminal_growth']:.1%}, and terminal ROIC {d['globals']['terminal_roic']:.0%}. These are analyst hurdle assumptions, not a precisely estimated CAPM. The workbook exposes WACC/growth sensitivity. Reverse valuation fixes the explicit cash flows and solves the terminal EBIT margin needed to reconcile enterprise value to price times cover-page shares plus September net debt. The answer is conditional on this exact setup. It does not identify a unique market forecast.

{against}

## Model mechanics and reviewer concerns

{change}

New borrowing is an explicit funding need when cash is insufficient, not evidence that a lender will fund it. Financing interest starts in the following year. Repayment budgets after the initial current-debt amount are assumptions, not security-level maturities. The cash reserve is an analyst policy, not a covenant. Other balance-sheet items remain constant, limiting deferred-tax, lease and pension detail. Forecast FX is zero. No future acquisitions are assumed. Dividend and repurchase ceilings are illustrative. The two-input repurchase table changes only the first operating shock and capex multiplier, so it is a local sensitivity, not a full downside case. The cash-only EBITDA threshold freezes the other cash drivers. Equal-month valuation proration is a material timing simplification for seasonal businesses.

## Decision evidence to request

{nextdata}

## Reproduction and checks

Run src/model.py, then src/validate.py. The latter tests all case balance sheets and cash closes, the cash distribution cap, impairment tax/cash behavior, a financing shortfall, later-driver propagation, valuation monotonicity and invalid discount rates. SQLite checks independently reconcile reported balance sheets and cash changes. The Excel builder tests all five forecasts against Python for each case, changes a later driver and compares native two-input Data Table cells with direct recalculation. Excel desktop and PowerPoint desktop were not available for manual application testing.

The Excel builder requires @oai/artifact-tool. Numeric model reproduction requires only Python standard library plus lxml for source re-extraction. Chart recreation additionally requires matplotlib. Selected input snapshots are distributed. Full filing HTML is not redistributed in this package. Re-download using filing_manifest.json and verify hashes before running extract.py and prepare.py. SEC may restrict automated requests, so use a descriptive user-agent and honor rate limits.
'''
  research+='\n## Additional company context sources\n\n'+''.join(f'- [{label}]({url}). Management presentation or release, distinct from the SEC statement facts.\n'for label,url in context)
  (ROOT/f'docs/{sym}_Research_Methodology.md').write_text(research)
  notes=f'''# {name}: interview notes

## Thirty-second explanation
{opening} The model connects operating drivers to cash and financing, then asks what the dated market price requires. All future numbers are scenarios.

## Three findings
'''+ '\n\n'.join(html.unescape(x.replace('<strong>','').replace('</strong>',''))for x in findings)+f'''

## Most consequential choice
{choice}

## Best objection
{against}

## Questions to rehearse
1. Why do stronger profits not necessarily increase repurchase capacity?
2. Why does a noncash impairment affect assets and equity without an equal cash outflow?
3. Why use dated cover-page shares for market capitalization instead of weighted-average EPS shares?
4. What happens when refinancing is unavailable? Does the model assume a facility?
5. Why retain stock compensation as an economic cost in DCF?
6. What fraction of value comes after the explicit forecast, and what changes it?
7. Which cost and working-capital assumptions could reverse the conclusion?

## Explain the funding waterfall
Opening cash + CFO + CFI - principal repayment + assumed refinancing. Compare with the cash reserve. Show any additional funding required explicitly. Cap dividends and buybacks to available cash. Sweep residual cash to debt. Link closing cash, debt and equity back to the balance sheet. Interest uses opening debt to avoid circularity.

## Honest closing
{nextdata} I would improve those inputs before presenting this as an investment recommendation.
'''
  (ROOT/f'docs/{sym}_Interview_Notes.md').write_text(notes)
  copy=f'''# Proposed portfolio case study: {name}

## {title}

{opening}

**Who it helps:** A financial analyst evaluating capital allocation, cash requirements and downside resilience.

**Evidence:** Three years of reported statements, latest quarterly comparatives, dated share count and a corroborated closing price. Five-year projections are labeled scenarios.

**What I built:** An integrated Excel model with operating drivers, three statements, a financing waterfall, DCF, reverse valuation and two-input sensitivities. Python reproduces the analysis. SQL reconciles reported financial statements.

**Finding:** {html.unescape(findings[0].replace('<strong>','').replace('</strong>',''))}

**Why it matters:** {decision}

**Limitation:** {choice} {against}

**Downloadable, offline project:** Excel workbook, executive memo, five-minute presentation, data, methods and code. No hosted application is claimed. Pending review and publication.
'''
  (ROOT/f'docs/{sym}_Portfolio_Copy.md').write_text(copy)
  allrows=[dict(case=c,**r)for c,z in res.items()for r in z['forecast']]
  fields=list(dict.fromkeys(k for row in allrows for k in row))
  with(OUT/f'{sym}_Scenario_Results.csv').open('w')as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(allrows)
  sens=[]
  for w in [d['globals']['wacc']+(i-2)*.01 for i in range(5)]:
   for g in [d['globals']['terminal_growth']+(i-2)*.005 for i in range(5)]:sens.append({'wacc':w,'terminal_growth':g,'dcf_per_share':valuation(d,res['base']['forecast'],wacc=w,growth=g)['per_share']})
  with(OUT/f'{sym}_Valuation_Sensitivity.csv').open('w')as f:
   w=csv.DictWriter(f,fieldnames=list(sens[0]));w.writeheader();w.writerows(sens)
  print(sym,'memo and evidence exports created')

if __name__=='__main__':main()
