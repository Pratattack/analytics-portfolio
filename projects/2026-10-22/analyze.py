"""Empirical scope reconciliation and conditional decision analysis, no model training."""
import csv,json,sqlite3,itertools
from config import ROOT,LAND,HOTEL
from extract import run,write_csv
from models import land_option,recovery

def sql_summary(project,panel):
 con=sqlite3.connect(':memory:');fields=list(dict.fromkeys(k for r in panel for k in r));numeric={'deposits','disclosed_price','remaining_price','additional_preacquisition','revenue','reimb_revenue','reimb_expense','op_income','fee_revenue'}
 con.execute('CREATE TABLE observations ('+','.join('"'+k+'" '+('REAL' if k in numeric else 'TEXT') for k in fields)+')');con.executemany('INSERT INTO observations VALUES ('+','.join('?' for k in fields)+')',[[r.get(k) for k in fields] for r in panel]);q=(ROOT/project/'warehouse.sql').read_text();cur=con.execute(q);rows=[dict(zip([x[0] for x in cur.description],r)) for r in cur.fetchall()];write_csv(ROOT/project/'outputs/sql_summary.csv',rows);return rows

def analyze_land():
 panel=run(LAND);root=ROOT/LAND;out=root/'outputs';scopes=[]
 for t,end in sorted(set((r['ticker'],r['end']) for r in panel)):
  rows=[r for r in panel if r['ticker']==t and r['end']==end];total=next((r for r in rows if r['scope']=='total'),None);parts=[r for r in rows if r['scope']!='total']
  if total and len(parts)==2:
   for metric in ['deposits','disclosed_price']:
    delta=sum(r[metric] for r in parts)-total[metric];scopes.append({'ticker':t,'end':end,'metric':metric,'parts_sum':sum(r[metric] for r in parts),'total':total[metric],'difference':delta});assert abs(delta)<1
 write_csv(out/'scope_reconciliation.csv',scopes)
 latest=[max([r for r in panel if r['ticker']==t and r['scope']=='total'],key=lambda r:r['end']) for t in sorted(set(r['ticker'] for r in panel))];scenarios=[];current=[]
 for r in latest:
  for ratio,p,rate,extension in itertools.product([.8,1,1.2],[.25,.5,.75],[.05,.1,.2],[0,.02,.05]):
   z=land_option(r['remaining_price'],r['deposits'],ratio,p=p,rate=rate,extension=extension);scenarios.append({'ticker':r['ticker'],'value_ratio_assumed':ratio,'up_probability_assumed':p,'discount_rate_assumed':rate,'extension_cost_rate_assumed':extension,**z})
  current.append({**r,'deposit_share_of_reported_price':r['deposits']/r['disclosed_price'],'disclosed_at_risk_cost':r['deposits']+(r.get('additional_preacquisition') or 0),'extra_cost_scope':'preacquisition included in deposits' if r['ticker']=='PHM' else ('separate disclosed preacquisition added' if r['ticker']=='KBH' else 'cash deposits only; other costs unobserved'),**land_option(r['remaining_price'],r['deposits'])})
 write_csv(out/'latest_decisions.csv',current);write_csv(out/'conditional_option_grid.csv',scenarios)
 # Refund sensitivities affect the marginal threshold; lost deposits alone never make exercise beneficial.
 sens=[]
 for r in latest:
  for refund,ratio in itertools.product([0,.5,1],[.8,1,1.2]):sens.append({'ticker':r['ticker'],'refund_fraction_assumed':refund,'value_ratio_assumed':ratio,**land_option(r['remaining_price'],r['deposits'],ratio,refund=refund)})
 write_csv(out/'refund_sensitivity.csv',sens);sql=sql_summary(LAND,panel)
 metrics={'records':len(panel),'issuers':len(latest),'current_disclosed_cost':sum(r['disclosed_at_risk_cost'] for r in current),'current_remaining_purchase_price':sum(r['remaining_price'] for r in current),'scope_reconciliations':len(scopes),'scenarios':len(scenarios),'actions':{a:sum(r['action']==a for r in scenarios) for a in ['wait','exercise','abandon']},'refund_sensitivities':len(sens),'adoption_gate':False,'reason':'Aggregate portfolios, no deal-level land values, refund terms or extension rights; do not authorize exercise or treat conditional prices as debt.'}
 (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');return panel

def analyze_hotel():
 panel=run(HOTEL);root=ROOT/HOTEL;out=root/'outputs';bridges=[];recon=[]
 for r in panel:
  z=recovery(r['revenue'],r['reimb_revenue'],r['reimb_expense'],r['op_income']);bridges.append({**r,**z,'reimbursement_share':r['reimb_revenue']/r['revenue']})
 for t in sorted(set(r['ticker'] for r in panel)):
  for y in [2025,2026]:
   h=next(r for r in panel if r['ticker']==t and r['period']=='half' and r['end'].startswith(str(y)));q=next(r for r in panel if r['ticker']==t and r['period']=='quarter' and r['end'].startswith(str(y)))
   for metric in ['revenue','reimb_revenue','reimb_expense','op_income']:recon.append({'ticker':t,'year':y,'metric':metric,'half':h[metric],'q2':q[metric],'q1_derived':h[metric]-q[metric]})
 latest=[r for r in bridges if r['period']=='half' and r['end']=='2026-06-30'];scenarios=[]
 for r in latest:
  for cg,rg,budget_share,target in itertools.product([0,.05,.1],[-.05,0,.05,.1],[0,.02,.05],[.15,.3]):
   budget=budget_share*r['net_revenue'];z=recovery(r['revenue'],r['reimb_revenue'],r['reimb_expense'],r['op_income'],cg,rg,budget,target);scenarios.append({'ticker':r['ticker'],'cost_growth_assumed':cg,'recovery_growth_assumed':rg,'budget_share_assumed':budget_share,'income_floor_assumed':target,**z})
 write_csv(out/'earnings_bridge.csv',bridges);write_csv(out/'latest_decisions.csv',latest);write_csv(out/'quarter_ytd_reconciliation.csv',recon);write_csv(out/'conditional_recovery_grid.csv',scenarios)
 # YoY only compares identically defined periods within the same original Q2 filing.
 changes=[]
 for t in sorted(set(r['ticker'] for r in panel)):
  for period in ['quarter','half']:
   a=next(r for r in bridges if r['ticker']==t and r['period']==period and r['end']=='2025-06-30');b=next(r for r in bridges if r['ticker']==t and r['period']==period and r['end']=='2026-06-30')
   delta=b['op_income']-a['op_income'];core=b['profit_ex_recovery']-a['profit_ex_recovery'];rec=b['recovery_balance']-a['recovery_balance'];assert abs(delta-core-rec)<1
   changes.append({'ticker':t,'period':period,'op_income_change':delta,'ex_recovery_profit_change':core,'recovery_balance_change':rec,'identity_error':delta-core-rec})
 write_csv(out/'yoy_income_bridge.csv',changes)
 # Denominator-normalization rank diagnostics only compare matched annual or H1 windows.
 ranks=[]
 for period,end in sorted(set((r['period'],r['end']) for r in bridges)):
  same=[r for r in bridges if r['period']==period and r['end']==end]
  if len(same)!=3:continue
  reported=sorted(same,key=lambda r:-r['reported_margin']);normalized=sorted(same,key=lambda r:-r['ex_recovery_margin'])
  for r in same:ranks.append({'ticker':r['ticker'],'period':period,'end':end,'gaap_margin':r['reported_margin'],'margin_ex_net_recovery':r['ex_recovery_margin'],'gaap_rank':1+reported.index(r),'bridge_rank':1+normalized.index(r),'interpretation':'Not a pure-fee or valuation ranking; owned hotels, co-brand fees and other costs remain.'})
 write_csv(out/'matched_margin_ranks.csv',ranks)
 sql_summary(HOTEL,panel)
 metrics={'records':len(panel),'annual_records':sum(r['period']=='annual' for r in panel),'issuers':len(latest),'h1_2026_revenue':sum(r['revenue'] for r in latest),'h1_2026_reimbursement_revenue':sum(r['reimb_revenue'] for r in latest),'h1_2026_recovery_balance':sum(r['recovery_balance'] for r in latest),'h1_2026_op_income':sum(r['op_income'] for r in latest),'scenarios':len(scenarios),'below_assumed_floor':sum(r['gate']=='below assumed income floor' for r in scenarios),'adoption_gate':False,'reason':'Accounting bridges and hypothetical income floors; recovery lags, contract billability and forward core budgets unobserved. Not free cash, pure fee margin or issuer adjusted EBITDA.'}
 (out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');return panel
if __name__=='__main__':
 analyze_land();analyze_hotel()
