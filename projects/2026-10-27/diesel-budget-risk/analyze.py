"""Retrospective, non-overlapping 13-week fuel budget evaluation."""
from presentation import *
import numpy as np,sqlite3
TAU=.9

def pinball(y,q,tau=TAU):
 e=np.asarray(y)-np.asarray(q);return np.maximum(tau*e,(tau-1)*e)

def make_blocks(s):
 assert ((s.index.to_series().diff().dropna()/pd.Timedelta(days=1))==7).all(),'Missing weekly observation'
 assert (s.index.dayofweek==0).all()
 rows=[]
 # Fixed calendar anchored to the second observed Monday, no optimized start date.
 for i in range(1,len(s)-12,13):
  future=s.iloc[i:i+13];quote=s.iloc[i-1]
  assert len(future)==13
  rows.append(dict(origin=str(s.index[i].date()),quote_date=str(s.index[i-1].date()),end=str(future.index[-1].date()),quote=float(quote),actual_mean=float(future.mean()),ratio=float(future.mean()/quote)))
 return pd.DataFrame(rows)

def history(blocks,row):
 # All 13 prices from a previous block must be a week old at this origin.
 cutoff=pd.Timestamp(row.origin)-pd.Timedelta(days=7)
 hist=blocks[pd.to_datetime(blocks.end)<=cutoff]
 assert hist.empty or (pd.to_datetime(hist.end)<pd.Timestamp(row.origin)).all()
 return hist

def reserve(hist,window,tau=TAU):
 x=hist.ratio if window=='all' else hist.ratio.tail(int(window))
 assert len(x)>=20
 return max(1.,float(np.quantile(x,tau,method='higher')))

def evaluate(blocks,window):
 rows=[]
 for row in blocks.itertuples():
  hist=history(blocks,row)
  if len(hist)<20:continue
  if row.origin<'2016-01-01':continue
  for rule,mult in [('No buffer',1.),('Fixed 10%',1.1),('Historical q90',reserve(hist,window))]:
   budget=row.quote*mult;short=max(0,row.actual_mean-budget)
   rows.append(dict(origin=row.origin,end=row.end,quote_date=row.quote_date,training_last_end=hist.end.iloc[-1],training_blocks=len(hist),rule=rule,quote=row.quote,budget_per_gallon=budget,actual_mean=row.actual_mean,buffer_pct=100*(mult-1),covered=int(row.actual_mean<=budget+1e-12),shortfall_per_gallon=short,unused_per_gallon=max(0,budget-row.actual_mean),pinball_per_gallon=float(pinball(row.actual_mean,budget))))
 return pd.DataFrame(rows)

def main():
 s=load('GASDESW');s.rename('usd_per_gallon').to_csv(OUT/'weekly_evidence.csv',float_format='%.6f')
 blocks=make_blocks(s);blocks.to_csv(OUT/'completed_13week_blocks.csv',index=False,float_format='%.10f')
 validation=[]
 for w in ['20','40','all']:
  ev=evaluate(blocks,w);v=ev[(ev.origin<'2020-01-01')&(ev.rule=='Historical q90')]
  validation.append(dict(window=w,validation_blocks=len(v),mean_pinball_usd_per_gallon=float(v.pinball_per_gallon.mean()),coverage_pct=float(100*v.covered.mean()),mean_buffer_pct=float(v.buffer_pct.mean())))
 val=pd.DataFrame(validation);assert len(set(val.validation_blocks))==1 and val.validation_blocks.min()>0
 # Stable first candidate tie break. Freeze window after validation, before holdout metrics.
 selected=str(val.sort_values('mean_pinball_usd_per_gallon',kind='stable').iloc[0]['window'])
 val.to_csv(OUT/'validation_selection.csv',index=False,float_format='%.10f')
 ev=evaluate(blocks,selected);ev['period']=np.where(ev.origin<'2020-01-01','validation_2016_2019','holdout_2020_2026')
 # Expanding historical outcomes may enter later holdout origins; the rule and window stay frozen.
 ev.to_csv(OUT/'budget_evaluation.csv',index=False,float_format='%.10f')
 test=ev[ev.period=='holdout_2020_2026'];scores=[]
 for rule,g in test.groupby('rule',sort=False):
  scores.append(dict(rule=rule,quarters=len(g),covered=int(g.covered.sum()),coverage_pct=100*g.covered.mean(),mean_buffer_pct=g.buffer_pct.mean(),mean_shortfall_usd_100k_gallons=100000*g.shortfall_per_gallon.mean(),max_shortfall_usd_100k_gallons=100000*g.shortfall_per_gallon.max(),mean_unused_usd_100k_gallons=100000*g.unused_per_gallon.mean(),mean_pinball_usd_per_gallon=g.pinball_per_gallon.mean()))
 scores=pd.DataFrame(scores);scores.to_csv(OUT/'holdout_metrics.csv',index=False,float_format='%.10f')
 # SQL independently checks realized quarter means from raw weekly prices, plus per-rule accounting.
 con=sqlite3.connect(':memory:');s.rename('price').reset_index().to_sql('prices',con,index=False);blocks.to_sql('blocks',con,index=False);ev.to_sql('evaluation',con,index=False)
 query=(ROOT/'reconcile.sql').read_text().split('-- NEXT QUERY --')
 actual=pd.read_sql_query(query[0],con);assert np.allclose(actual.sql_mean,blocks.actual_mean,rtol=0,atol=1e-10)
 costs=pd.read_sql_query(query[1],con);assert np.allclose(costs.sql_shortfall,ev.shortfall_per_gallon,rtol=0,atol=1e-10)
 actual.to_csv(OUT/'sql_quarter_reconciliation.csv',index=False,float_format='%.10f')
 def price_chart(ax):
  ax.plot(s.index,s.values,color=COLORS[0],lw=1.5);ax.set_ylabel('Retail price (USD/gallon, includes taxes)')
 chart('diesel-history','A current quote is not a quarter-long budget','Observed U.S. weekly retail diesel prices | Not seasonally adjusted',price_chart)
 def budget_chart(ax):
  q=test[test.rule=='Historical q90'];d=pd.to_datetime(q.origin)
  ax.plot(d,q.actual_mean,color='#eef3fa',label='Realized 13-week mean',lw=2)
  for i,rule in enumerate(['No buffer','Fixed 10%','Historical q90']):
   g=test[test.rule==rule];ax.plot(pd.to_datetime(g.origin),g.budget_per_gallon,color=COLORS[i],label=rule,lw=1.5,ls='--' if i<2 else '-')
  ax.set_ylabel('USD/gallon');ax.legend(frameon=False,ncol=2,fontsize=9)
 chart('diesel-budget','How each budget compared with the realized bill','Holdout quarters only | Prior-week quote | Equal gallons in each of 13 weeks',budget_chart)
 def shortfalls(ax):
  for i,rule in enumerate(['No buffer','Fixed 10%','Historical q90']):
   g=test[test.rule==rule];x=np.arange(len(g));ax.bar(x+(i-1)*.26,g.shortfall_per_gallon*100000,width=.25,color=COLORS[i],label=rule)
  g=test[test.rule=='No buffer'];ticks=np.arange(0,len(g),4);ax.set_xticks(ticks);ax.set_xticklabels([g.iloc[i].origin[:4] for i in ticks]);ax.set_ylabel('Budget shortfall (USD / assumed 100,000 gallons)');ax.legend(frameon=False,fontsize=9)
 chart('diesel-shortfalls','A reserve can still miss a price shock','Hypothetical fixed volume applied to actual historical prices | Unused reserves are not savings',shortfalls)
 # Current scenario is not counted as a completed evaluation outcome.
 next_origin=s.index[-1]+pd.Timedelta(days=7)
 eligible=blocks[pd.to_datetime(blocks.end)<=next_origin-pd.Timedelta(days=7)]
 mult=reserve(eligible,selected)
 sensitivity=[]
 for w in ['20','40','all']:
  for tau in [.8,.9,.95]:sensitivity.append(dict(window=w,quantile=tau,eligible_blocks=min(len(eligible),int(w)) if w!='all' else len(eligible),reserve_pct=100*(reserve(eligible,w,tau)-1)))
 pd.DataFrame(sensitivity).to_csv(OUT/'current_reserve_sensitivity.csv',index=False,float_format='%.10f')
 q=scores[scores.rule=='Historical q90'].iloc[0];fixed=scores[scores.rule=='Fixed 10%'].iloc[0]
 summary=dict(weekly_observations=len(s),start=str(s.index[0].date()),end=str(s.index[-1].date()),completed_blocks=len(blocks),validation_selected_window=selected,validation_blocks=int(val.validation_blocks.iloc[0]),holdout_blocks=int(q.quarters),holdout_covered=int(q.covered),holdout_coverage_pct=float(q.coverage_pct),fixed10_coverage_pct=float(fixed.coverage_pct),historical_q90_mean_buffer_pct=float(q.mean_buffer_pct),historical_q90_mean_shortfall_usd_100k=float(q.mean_shortfall_usd_100k_gallons),historical_q90_max_shortfall_usd_100k=float(q.max_shortfall_usd_100k_gallons),latest_observed_price=float(s.iloc[-1]),next_origin=str(next_origin.date()),illustrative_reserve_pct=100*(mult-1),sql_blocks_verified=len(actual),sql_budget_rows_verified=len(costs))
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 finding=f'The historical q90 rule covered {int(q.covered)} of {int(q.quarters)} completed holdout quarters ({q.coverage_pct:.1f}%), compared with {fixed.coverage_pct:.1f}% for a fixed 10% buffer. Its average reserve was {q.mean_buffer_pct:.1f}% of the prior-week quote. The worst shortfall was ${q.max_shortfall_usd_100k_gallons:,.0f} at an assumed 100,000 gallons.'
 limits='National retail pump prices include taxes; they are not fleet contract invoices, local route costs or wholesale hedging prices. Equal gallons across weeks and 100,000 gallons per quarter are illustrative. The current revised export is not an archived real-time vintage. A one-week quote lag guards publication timing, but does not eliminate revision risk. Non-overlapping quarters avoid shared outcomes but can remain serially dependent. Coverage is historical frequency, not a guaranteed future probability. No actual company savings or hedge performance is claimed.'
 body=metrics([('Holdout coverage, historical q90',f'{int(q.covered)}/{int(q.quarters)}'),('Average reserve over quote',f'{q.mean_buffer_pct:.1f}%'),('Worst shortfall, assumed 100k gallons',f'${q.max_shortfall_usd_100k_gallons:,.0f}')])
 body+='<h2>The decision</h2><p>How much cash should an operations team reserve for thirteen weeks of diesel purchases? Compare a flat quote, a fixed 10% buffer and a reserve calibrated from completed historical quarters.</p><h2>The result</h2><p>'+finding+'</p><p class="note">A q90 label is a calibration target, not a coverage guarantee. Reserves tie up budget capacity. An unused reserve is not an economic saving.</p>'
 body+=figure('diesel-history','Observed weekly EIA retail diesel prices from 2007 through the snapshot cutoff. The series includes taxes and is not seasonally adjusted.')
 body+=figure('diesel-budget','Holdout: budgets set from the prior-week quote compared with the subsequent completed 13-week mean. No outcome from the current quarter enters its reserve estimate.')
 body+='<h2>Budget adequacy and the price of conservatism</h2><p>All dollar columns assume 100,000 gallons per quarter, evenly distributed across thirteen weeks. Shortfall and unused reserve measure budget adequacy, not operating profit.</p>'+table(scores.rename(columns={'mean_shortfall_usd_100k_gallons':'Mean shortfall ($)','max_shortfall_usd_100k_gallons':'Worst shortfall ($)','mean_unused_usd_100k_gallons':'Mean unused reserve ($)'}))
 body+=figure('diesel-shortfalls','Three budget rules applied to the same actual prices and hypothetical 100,000-gallon exposure. Zero means the budget covered that quarter, not that diesel was free.')
 body+='<h2>Validation before holdout</h2><p>Candidate histories were the most recent 20 completed quarters, 40 completed quarters and all completed quarters. The 2016 to 2019 validation period selected the lowest mean 90th-quantile pinball loss in dollars per gallon. Ties use candidate order. The selected window was '+selected+'. The window and quantile were frozen for 2020 onward; newly completed history could update the reserve at later origins.</p>'+table(val)
 body+='<h2>Timing and method</h2><p>Blocks begin on the second Monday in the snapshot and advance thirteen weeks. Each budget uses the preceding Monday quote, allowing time for publication. Training targets must end at least seven days before the decision origin. At least twenty completed blocks are required. The historical rule is the higher empirical 90th quantile of realized quarter mean divided by its prior-week quote, floored at one. Only complete thirteen-week outcomes are scored. SQL independently recalculates all realized quarter means and budget shortfalls.</p><h2>Use the scenario tool</h2><p>The <a href="workbench.html">fuel budget workbench</a> makes volume, price and reserve assumptions explicit. It does not predict future prices. <a href="current_reserve_sensitivity.csv">Current window and quantile sensitivity</a> shows how the chosen reserve depends on those choices; this table is not used to retune holdout results.</p><h2>Limitations</h2><p>'+limits+'</p><h2>Inspect the evidence</h2><p><a href="weekly_evidence.csv">Weekly observations</a> · <a href="completed_13week_blocks.csv">Quarter construction</a> · <a href="budget_evaluation.csv">Every evaluated budget</a> · <a href="holdout_metrics.csv">Holdout metrics</a> · <a href="validation_selection.csv">Window selection</a> · <a href="sql_quarter_reconciliation.csv">SQL reconciliation</a> · <a href="summary.json">Summary</a></p><p>Sources: <a href="https://fred.stlouisfed.org/series/GASDESW">EIA diesel series via FRED</a>, <a href="https://www.eia.gov/petroleum/gasdiesel/diesel_proc-methods.php">EIA survey methodology</a>, <a href="https://www.eia.gov/dnav/pet/PET_PRI_GND_A_EPD2D_PTE_DPGAL_W.htm">EIA historical series</a>. These prices are retail cash self-serve observations including taxes. Older history includes the transition from low-sulfur to ultra-low-sulfur diesel; the series is not a uniform fuel specification across all years.</p>'
 write_page('report.html','How much diesel-price risk should a budget carry?',finding,body)
 work=f'<p class="note">Hypothetical budget scenario. Default price ${s.iloc[-1]:.3f}/gallon is observed on {s.index[-1]:%Y-%m-%d}. The default reserve {100*(mult-1):.2f}% uses the frozen historical rule and completed blocks only. It is not a forecast or a guaranteed 90% protection level.</p><form id="budget"><div class="fields"><div><label for="price">Assumed quote (USD/gallon)</label><input id="price" type="number" min="0.01" max="30" step="0.001" value="{s.iloc[-1]:.3f}" required></div><div><label for="gallons">Assumed 13-week gallons</label><input id="gallons" type="number" min="1" max="100000000" step="1" value="100000" required></div><div><label for="reserve">Assumed reserve over quote (%)</label><input id="reserve" type="number" min="0" max="200" step="0.01" value="{100*(mult-1):.2f}" required></div></div><label for="stress">Assumed realized mean price change from quote (%)</label><input id="stress" type="number" min="-99" max="300" step="1" value="20" required><output id="result" aria-live="polite"></output><p id="explain"></p></form><h2>Keep the assumptions visible</h2><p>Base cost = quote × gallons. Budget = base cost × (1 + reserve). Stress cost = base cost × (1 + assumed realized price change). Shortfall = max(0, stress cost − budget). Equal weekly volumes are assumed. Volume changes, tax treatment, delivery charges, contracts and hedges require a separate model.</p><p><a href="report.html">Read the historical evaluation</a> · <a href="current_reserve_sensitivity.csv">Download reserve sensitivity</a></p><noscript>JavaScript is required for recalculation. All evaluation CSV files remain available.</noscript>'
 write_page('workbench.html','What would a diesel shock do to your budget?','Choose a volume, quote, reserve and price stress. Every company-level input is hypothetical.',work,'<script src="calculator.js"></script>')
 (ROOT/'docs/executive_memo.md').write_text('# Diesel budget risk\n\n'+finding+'\n\n## Decision use\nCompare budget coverage against unused capacity and residual shortfalls. Validate with actual route-level invoices before use.\n\n## Limits\n'+limits+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
