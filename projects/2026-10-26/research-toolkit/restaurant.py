"""Lease-aware earnings stress and a conditional two-lever response frontier."""
import json,sqlite3,itertools
import numpy as np
from scipy.optimize import linprog
from common import ROOT,REST,dump,csvout,digest

def response(revenue,ebit,lease_cost,shock,margin,escalation,floor,cost_cap=.02,recovery_fraction=.5,cost_weight=.5,recovery_weight=.15):
 vals=[revenue,ebit,lease_cost,shock,margin,escalation,floor,cost_cap,recovery_fraction,cost_weight,recovery_weight]
 if not all(np.isfinite(vals)) or revenue<=0 or lease_cost<0 or not 0<=shock<=.8 or not 0<margin<=1 or not 0<=escalation<=1 or not 0<=floor<=.3 or not 0<=cost_cap<=.2 or not 0<=recovery_fraction<=1 or min(cost_weight,recovery_weight)<=0:raise ValueError('Invalid scenario domain')
 stressed=ebit-revenue*shock*margin-lease_cost*escalation
 gap=max(0,floor*revenue-stressed);caps=[revenue*cost_cap,revenue*shock*recovery_fraction];capacity=caps[0]+margin*caps[1]
 # Two bounded response levers; exact fractional-knapsack solution to a one-row LP.
 x=y=0.;remaining=gap
 for k in sorted([0,1],key=lambda k:([cost_weight,recovery_weight][k]/[1,margin][k],k)):
  used=min(caps[k],remaining/[1,margin][k]);remaining=max(0,remaining-used*[1,margin][k])
  if k==0:x=used
  else:y=used
 feasible=gap<=capacity+1e-6
 return {'stressed_ebit':stressed,'gap_to_floor':gap,'max_ebit_support':capacity,'feasible':bool(feasible),'cost_savings':x if feasible else None,'recovered_sales':y if feasible else None,'assumed_response_resource':cost_weight*x+recovery_weight*y if feasible else None,'remaining_gap_after_full_capacity':max(0,gap-capacity),'cost_only_feasible':bool(gap<=caps[0]+1e-6)}

def independent_lp(r,shock,margin,escalation,floor,cap=.02,recover=.5):
 gap=max(0,floor*r['revenue']-r['ebit']+r['revenue']*shock*margin+r['lease_cost']*escalation)
 sol=linprog([.5,.15],A_ub=[[-1,-margin]],b_ub=[-gap],bounds=[(0,cap*r['revenue']),(0,recover*shock*r['revenue'])],method='highs')
 return sol

def analyze():
 p=ROOT/REST/'data';hashes=json.loads((p/'hashes.json').read_text());assert all(digest(p/n)==s for n,s in hashes.items());panel=json.loads((p/'panel.json').read_text());out=ROOT/REST/'outputs';latest=[]
 for ticker in sorted({x['ticker'] for x in panel}):
  r=max([x for x in panel if x['ticker']==ticker],key=lambda x:x['end']);assert r['revenue']>0 and r['lease_cost']>0 and r['lease_cash']>=0
  latest.append(dict(**r,ebit_margin=r['ebit']/r['revenue'],lease_cost_share=r['lease_cost']/r['revenue'],lease_cash_minus_cost=r['lease_cash']-r['lease_cost'],rent_only_earnings_cover=(r['ebit']+r['lease_cost'])/r['lease_cost']))
 scenarios=[]
 for r in latest:
  for shock,margin,escalation,floor in itertools.product([.05,.1,.2],[.2,.35,.5],[0,.1],[0,.03]):
   v=response(r['revenue'],r['ebit'],r['lease_cost'],shock,margin,escalation,floor);sol=independent_lp(r,shock,margin,escalation,floor);assert bool(sol.success)==v['feasible']
   if sol.success:assert abs(float(sol.fun)-v['assumed_response_resource'])<=max(.01,abs(sol.fun)*1e-8)
   scenarios.append(dict(ticker=r['ticker'],shock=shock,contribution_margin=margin,lease_escalation=escalation,ebit_floor=floor,**v))
 sensitivity=[]
 for r in latest:
  for cap,recovery in itertools.product([.01,.02,.03],[0,.25,.5,1]):sensitivity.append(dict(ticker=r['ticker'],cost_cap=cap,recovery_fraction=recovery,**response(r['revenue'],r['ebit'],r['lease_cost'],.2,.35,.1,.03,cap,recovery)))
 # Historical replay is only a challenge: the model is not calibrated to causal cost elasticity.
 history=[]
 for ticker in sorted({x['ticker'] for x in panel}):
  rows=sorted([x for x in panel if x['ticker']==ticker],key=lambda x:x['end'])
  for a,b in zip(rows,rows[1:]):
   if int(b['end'][:4])-int(a['end'][:4])!=1:continue
   change=(b['revenue']-a['revenue'])/a['revenue'];actual=b['ebit']-a['ebit'];modeled=a['revenue']*change*.35
   history.append(dict(ticker=ticker,base_end=a['end'],next_end=b['end'],revenue_change=change,actual_ebit_change=actual,constant_margin_proxy_change=modeled,residual=actual-modeled))
 db=sqlite3.connect(':memory:');db.execute('CREATE TABLE scenarios(ticker TEXT,feasible INT,cost_only INT,gap REAL)');db.executemany('INSERT INTO scenarios VALUES(?,?,?,?)',[(x['ticker'],int(x['feasible']),int(x['cost_only_feasible']),x['gap_to_floor']) for x in scenarios]);s=db.execute('SELECT ticker,count(*),sum(feasible),sum(cost_only),avg(gap) FROM scenarios GROUP BY ticker').fetchall();csvout(out/'sql_feasibility.csv',[dict(ticker=x[0],scenarios=x[1],feasible=x[2],cost_only_feasible=x[3],average_assumed_gap=x[4]) for x in s]);csvout(out/'latest.csv',latest);csvout(out/'scenario_frontier.csv',scenarios);csvout(out/'support_sensitivity.csv',sensitivity);csvout(out/'historical_challenge.csv',history);csvout(out/'annual_panel.csv',panel)
 report={'issuer_years':len(panel),'issuers':len(latest),'source_original_filings_audited':6,'original_cells_audited':len(json.loads((p/'original_audit.json').read_text())),'latest_revenue':sum(x['revenue'] for x in latest),'latest_operating_lease_cost':sum(x['lease_cost'] for x in latest),'latest_operating_lease_cash':sum(x['lease_cash'] for x in latest),'scenarios':len(scenarios),'infeasible':sum(not x['feasible'] for x in scenarios),'combined_only_feasible':sum(x['feasible'] and not x['cost_only_feasible'] for x in scenarios),'independent_lp_reconciliations':len(scenarios),'support_sensitivities':len(sensitivity),'history_challenges':len(history),'promotion_gate':False,'interpretation':'Dated FY2025 earnings stress; scenario levers, response costs and caps are assumed, not achieved savings, covenant tests or liquidity forecasts.'};dump(out/'metrics.json',report);print(REST,report,flush=True);return report
if __name__=='__main__':analyze()
