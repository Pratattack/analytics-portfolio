from pathlib import Path
import csv,json,math,sqlite3
import numpy as np
from extract import ROOT,run,days,write_csv,CUTOFF
from models import inventory_features,ridge_fit,inventory_scenario,rail_scenario,fixed_asset_return
SEM='semiconductor-inventory-funding';RAIL='freight-rail-capital-review'
def dump(p,o):p.write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def warehouse(root,rows):
 # SQLite ephemeral; checked SQL exports are the persistent artifact.
 db=sqlite3.connect(':memory:');cols=list(rows[0]);numeric=set(cols)-{'ticker','end','filed','accn','form','ppe_net_basis','ppe_gross_basis'}
 db.execute('CREATE TABLE panel ('+','.join('"'+k+'" '+('REAL' if k in numeric else 'TEXT') for k in cols)+')')
 db.executemany('INSERT INTO panel VALUES ('+','.join('?' for _ in cols)+')',[[r.get(k) for k in cols] for r in rows])
 sql=(root/'warehouse.sql').read_text();cur=db.execute(sql);out=[dict(zip([d[0] for d in cur.description],r)) for r in cur];write_csv(root/'outputs/sql_summary.csv',out);return out

def semi():
 root=ROOT/SEM;rows=run(SEM);group={t:sorted([r for r in rows if r['ticker']==t],key=lambda r:r['end']) for t in sorted({r['ticker'] for r in rows})};samples=[];feature_gaps=[]
 for t,rs in group.items():
  for i in range(4,len(rs)-1):
   seq=rs[i-4:i+2]
   if not all(75<=days(a['end'],b['end'])<=105 for a,b in zip(seq,seq[1:])):
    feature_gaps.append({'ticker':t,'origin':rs[i]['end'],'reason':'six consecutive fiscal quarters unavailable'});continue
   a,z=rs[i],rs[i+1]
   # All five input statements precede the origin filing. Original disclosures only.
   if any(s['filed']>a['filed'] for s in seq[:-1]):raise AssertionError('information timing')
   samples.append({'ticker':t,'origin_end':a['end'],'origin_filed':a['filed'],'target_end':z['end'],'target_filed':z['filed'],'x':inventory_features(rs,i),'y':math.log(z['inventory']/a['inventory']),'base':a['inventory'],'actual':z['inventory'],'seasonal':rs[i-3]['inventory']})
 samples.sort(key=lambda s:(s['origin_filed'],s['ticker']))
 # Genuine label availability, not only period ordering. No same-day labels used.
 def pred(s,penalty):
  train=[z for z in samples if z['target_filed']<s['origin_filed'] and z['target_end']<s['origin_end']]
  if len(train)<60:return None
  b=ridge_fit([z['x'] for z in train],[z['y'] for z in train],penalty)
  return s['base']*math.exp(float(np.dot(s['x'],b)))
 selection=[]
 for penalty in [1.,10.,100.]:
  pairs=[(s,pred(s,penalty)) for s in samples if s['target_end'][:4]=='2022']
  pairs=[(s,p) for s,p in pairs if p is not None]
  selection.append({'penalty':penalty,'selection_year':2022,'cases':len(pairs),'mae_usd':sum(abs(s['actual']-p) for s,p in pairs)/len(pairs)})
 penalty=min(selection,key=lambda s:s['mae_usd'])['penalty'];preds=[]
 known=max(s['target_filed'] for s in samples if s['target_end'][:4]=='2022')
 for s in samples:
  if s['target_end']<'2023-01-01' or s['origin_filed']<=known:continue
  p=pred(s,penalty)
  if p is None:continue
  training=[z for z in samples if z['target_filed']<s['origin_filed'] and z['target_end']<s['origin_end']]
  history=[r for r in preds if r['target_filed']<s['origin_filed']]
  # Expanding prequential calibration. Finite sample rank; dependence invalidates IID guarantees.
  scores=sorted(abs(r['actual']-r['forecast'])/r['base'] for r in history)
  q=scores[min(len(scores)-1,math.ceil((len(scores)+1)*.9)-1)] if len(scores)>=20 else None
  lo=max(0,p-(q or 0)*s['base']);hi=p+(q or 0)*s['base']
  preds.append({k:v for k,v in s.items() if k not in ('x','y')}|{'forecast':p,'training_n':len(training),'latest_training_label_filed':max(z['target_filed'] for z in training),'penalty_known_after':known,'last_value':s['base'],'lower90':lo if q is not None else None,'upper90':hi if q is not None else None,'calibration_n':len(scores),'split':'calibration' if s['target_end']<'2024-01-01' else 'test'})
 test=[r for r in preds if r['split']=='test'];metrics={'cutoff':CUTOFF,'records':len(rows),'forecast_test_cases':len(test),'selected_penalty':penalty,'selection':selection,'issuers':len(group),'future_filing_labels_used':0}
 for model in ['forecast','last_value','seasonal']:
  metrics[model+'_wape_pct']=100*sum(abs(r['actual']-r[model]) for r in test)/sum(r['actual'] for r in test)
 calibrated=[r for r in test if r['lower90'] is not None];metrics['coverage90_pct']=100*sum(r['lower90']<=r['actual']<=r['upper90'] for r in calibrated)/len(calibrated);metrics['interval_cases']=len(calibrated)
 # Issuer cluster bootstrap on unscaled USD absolute error difference, not IID quarters.
 rng=np.random.default_rng(20261021);keys=sorted({r['ticker'] for r in test});effects=[]
 for _ in range(4000):
  chosen=rng.choice(keys,len(keys),replace=True);rs=[r for t in chosen for r in test if r['ticker']==t]
  effects.append(sum(abs(r['actual']-r['last_value'])-abs(r['actual']-r['forecast']) for r in rs)/len(rs))
 metrics['mae_improvement_usd_interval95']=list(map(float,np.quantile(effects,[.025,.975])));metrics['test_issuer_clusters']=len(keys)
 latest=[]
 for t,rs in group.items():
  a=rs[-1];stale=days(a['end'],CUTOFF)>180
  seq=rs[-5:];eligible=len(seq)==5 and all(75<=days(u['end'],v['end'])<=105 for u,v in zip(seq,seq[1:]))
  if not eligible or stale:
   latest.append({'ticker':t,'end':a['end'],'inventory':a['inventory'],'cost':a['cost'],'status':'STALE_OR_GAPPED','filed':a['filed'],'forecast':None,'upper90':None,'lower90':None,'inventory_days_proxy':91.25*a['inventory']/a['cost']});continue
  x=inventory_features(rs,len(rs)-1);train=[s for s in samples if s['target_filed']<=CUTOFF];b=ridge_fit([s['x'] for s in train],[s['y'] for s in train],penalty);p=a['inventory']*math.exp(float(np.dot(x,b)))
  scores=sorted(abs(r['actual']-r['forecast'])/r['base'] for r in preds if r['target_filed']<=CUTOFF);q=scores[min(len(scores)-1,math.ceil((len(scores)+1)*.9)-1)]
  latest.append({'ticker':t,'end':a['end'],'inventory':a['inventory'],'cost':a['cost'],'filed':a['filed'],'forecast':p,'lower90':max(0,p-q*a['inventory']),'upper90':p+q*a['inventory'],'status':'RESEARCH_ONLY','inventory_days_proxy':91.25*a['inventory']/a['cost']})
 metrics['model_promotion_pass']=bool(metrics['mae_improvement_usd_interval95'][0]>0 and metrics['coverage90_pct']>=85 and all(r['status']!='STALE_OR_GAPPED' for r in latest));metrics['current_usable_issuers']=sum(r['status']!='STALE_OR_GAPPED' for r in latest);metrics['current_usable_inventory_usd']=sum(r['inventory'] for r in latest if r['status']!='STALE_OR_GAPPED')
 write_csv(root/'outputs/forecast_diagnostics.csv',preds);write_csv(root/'outputs/feature_gaps.csv',feature_gaps);write_csv(root/'outputs/latest_decisions.csv',latest);dump(root/'outputs/metrics.json',metrics)
 warehouse(root,rows)
 scenarios=[]
 for a in latest:
  if a['forecast'] is None:continue
  for carry in [5,10,20]:
   for buffer in [0,10,20]:scenarios.append({'ticker':a['ticker'],'carry_pct':carry,'buffer_pct':buffer,**inventory_scenario(a['inventory'],a['forecast'],a['upper90'],carry,buffer)})
 write_csv(root/'outputs/assumption_scenarios.csv',scenarios);return metrics

def rail():
 root=ROOT/RAIL;rows=run(RAIL);annual=[];sens=[]
 for t in sorted({r['ticker'] for r in rows}):
  rs=sorted([r for r in rows if r['ticker']==t],key=lambda r:r['end'])
  for i,r in enumerate(rs):
   prior=rs[i-1] if i and 350<=days(rs[i-1]['end'],r['end'])<=380 and rs[i-1]['ppe_net_basis']==r['ppe_net_basis'] else None
   s=rail_scenario(r['cfo'],r['capex'],r['dividends'],r['buybacks'],0,100)
   annual.append(r|s|{'net_asset_return21':fixed_asset_return(r['op_income'],prior['ppe_net'],r['ppe_net'],21) if prior else None,'gross_asset_return21':fixed_asset_return(r['op_income'],prior['ppe_gross'],r['ppe_gross'],21) if prior and prior['ppe_gross'] and r['ppe_gross'] else None,'cash_return_coverage':(r['cfo']-r['capex'])/(r['dividends']+r['buybacks']) if r['dividends']+r['buybacks']>0 else None,'cfo_shock_to_zero_gap_pct':100*((r['capex']+r['dividends']+r['buybacks'])/r['cfo']-1),'capex_to_sales':r['capex']/r['revenue']})
  a=annual[-1]
  if len(rs)>=2 and rs[-1]['ppe_net_basis']==rs[-2]['ppe_net_basis']:
   for tax in [21,25,30]:
    for basis in ['net','gross']:
     current=a['ppe_'+basis];previous=rs[-2]['ppe_'+basis]
     if not current or not previous:continue
     for hurdle in [6,8,10,12]:
      base=(current+previous)/2;ret=fixed_asset_return(a['op_income'],previous,current,tax)
      sens.append({'ticker':t,'tax_pct':tax,'asset_basis':basis,'hurdle_pct':hurdle,'aftertax_asset_return_pct':100*ret,'proxy_surplus_usd':a['op_income']*(1-tax/100)-base*hurdle/100,'ebit_to_hurdle_usd':base*hurdle/100/(1-tax/100)-a['op_income']})
 latest=[r for r in annual if r['end']==max(z['end'] for z in annual if z['ticker']==r['ticker'])];scenarios=[]
 for a in latest:
  for shock in [-40,-30,-20,-10,0,10]:
   for reinvest in [80,100,120,150]:scenarios.append({'ticker':a['ticker'],'cfo_shock_pct':shock,'capex_pct':reinvest,**rail_scenario(a['cfo'],a['capex'],a['dividends'],a['buybacks'],shock,reinvest)})
 rolling=[]
 for a in annual:
  rs=[r for r in annual if r['ticker']==a['ticker'] and int(a['end'][:4])-2<=int(r['end'][:4])<=int(a['end'][:4])]
  if len(rs)==3:
   cfo=sum(r['cfo'] for r in rs);capex=sum(r['capex'] for r in rs);dist=sum(r['dividends']+r['buybacks'] for r in rs)
   rolling.append({'ticker':a['ticker'],'end':a['end'],'cfo':cfo,'capex':capex,'cash_returns':dist,'retained_after_returns':cfo-capex-dist,'coverage':(cfo-capex)/dist})
 m={'cutoff':CUTOFF,'records':len(rows),'issuers':len(latest),'latest_end':max(r['end'] for r in latest),'latest_cfo_usd':sum(r['cfo'] for r in latest),'latest_capex_usd':sum(r['capex'] for r in latest),'latest_cash_returns_usd':sum(r['buybacks']+r['dividends'] for r in latest),'latest_gap_usd':sum(r['distribution_gap'] for r in latest),'latest_uncovered_issuers':sum(r['distribution_gap']<0 for r in latest),'scenario_cases':len(scenarios),'negative_gap_scenarios':sum(r['distribution_gap']<0 for r in scenarios),'asset_sensitivity_cases':len(sens),'adoption_gate':'NOT_AUTHORIZED: maintenance/growth split, current budgets, merger terms and safety constraints absent'}
 write_csv(root/'outputs/capital_history.csv',annual);write_csv(root/'outputs/latest_decisions.csv',latest);write_csv(root/'outputs/rolling_coverage.csv',rolling);write_csv(root/'outputs/cash_scenarios.csv',scenarios);write_csv(root/'outputs/asset_sensitivities.csv',sens);dump(root/'outputs/metrics.json',m);warehouse(root,rows);return m
if __name__=='__main__':
 print(json.dumps({'semiconductor':semi(),'rail':rail()},indent=2))
