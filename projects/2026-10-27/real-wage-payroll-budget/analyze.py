"""Pinned BLS wage, hours and CPI accounting. Run: python analyze.py."""
from presentation import *
import numpy as np,sqlite3

def main():
 df=pd.concat({'hourly_usd':load('CES0500000003'),'weekly_hours':load('AWHAETP'),'cpi':load('CPIAUCSL')},axis=1)
 assert df[['hourly_usd','weekly_hours']].notna().all().all()
 assert df.cpi.notna().sum()>200
 df[['cpi']].isna().rename(columns={'cpi':'cpi_missing'}).to_csv(OUT/'missing_observations.csv')
 assert len(df)==len(pd.date_range(df.index.min(),df.index.max(),freq='MS'))
 df['nominal_weekly_usd']=df.hourly_usd*df.weekly_hours
 df['real_hourly_1982_84_usd']=df.hourly_usd/df.cpi*100
 df['real_weekly_1982_84_usd']=df.nominal_weekly_usd/df.cpi*100
 for col in ['hourly_usd','weekly_hours','cpi','real_hourly_1982_84_usd','real_weekly_1982_84_usd']:
  df[col+'_yoy_pct']=df[col].pct_change(12,fill_method=None)*100
 df.index.name='date';df.to_csv(OUT/'monthly_evidence.csv',float_format='%.10f')
 latest=df.iloc[-1];anchors=[]
 for date in ['2007-01-01','2019-01-01','2020-02-01']:
  b=df.loc[date];a={'anchor':date,'end':str(df.index[-1].date())}
  for name in ['hourly_usd','weekly_hours','cpi','real_hourly_1982_84_usd','real_weekly_1982_84_usd']:a[name+'_change_pct']=(latest[name]/b[name]-1)*100
  a['hourly_log_points']=100*np.log(latest.hourly_usd/b.hourly_usd)
  a['hours_log_points']=100*np.log(latest.weekly_hours/b.weekly_hours)
  a['inflation_log_points']=-100*np.log(latest.cpi/b.cpi)
  a['real_weekly_log_points']=100*np.log(latest.real_weekly_1982_84_usd/b.real_weekly_1982_84_usd)
  assert abs(a['hourly_log_points']+a['hours_log_points']+a['inflation_log_points']-a['real_weekly_log_points'])<1e-10
  anchors.append(a)
 anchors=pd.DataFrame(anchors);anchors.to_csv(OUT/'anchor_sensitivity.csv',index=False,float_format='%.10f')
 # Independent SQL arithmetic for every month, rather than testing a copy of a summary.
 con=sqlite3.connect(':memory:');df[['hourly_usd','weekly_hours','cpi']].reset_index().to_sql('monthly',con,index=False)
 sql=(ROOT/'reconcile.sql').read_text();check=pd.read_sql_query(sql,con)
 assert np.allclose(check.real_weekly_1982_84_usd,df.real_weekly_1982_84_usd,rtol=0,atol=1e-10,equal_nan=True)
 check.to_csv(OUT/'sql_reconciliation.csv',index=False,float_format='%.10f')
 base=df.loc['2020-02-01'];since=df.loc['2020-02-01':]
 def indices(ax):
  for i,(c,label) in enumerate([('hourly_usd','Nominal hourly pay'),('cpi','Consumer prices'),('real_hourly_1982_84_usd','Real hourly pay'),('real_weekly_1982_84_usd','Real weekly pay')]):ax.plot(since.index,100*since[c]/base[c],label=label,color=COLORS[i],lw=2)
  ax.axhline(100,color='#a6b3c6',lw=.7,ls=':');ax.set_ylabel('Index, February 2020 = 100');ax.legend(loc='upper left',frameon=False,fontsize=9,ncol=2)
 chart('wage-index','Pay rises do not tell the whole story','U.S. private payrolls | Monthly, seasonally adjusted | February 2020 = 100',indices)
 def growth(ax):
  for i,(c,label) in enumerate([('real_hourly_1982_84_usd_yoy_pct','Real hourly earnings'),('real_weekly_1982_84_usd_yoy_pct','Real weekly earnings')]):ax.plot(df.index,df[c],label=label,color=COLORS[i],lw=1.7)
  ax.axhline(0,color='#a6b3c6',lw=.8);ax.set_ylabel('Change from 12 months earlier (%)');ax.legend(frameon=False)
 chart('wage-growth','Hours change the purchasing-power story','Aggregate earnings are affected by the mix of workers and industries',growth)
 a=anchors.iloc[-1]
 def decomposition(ax):
  values=[a.hourly_log_points,a.inflation_log_points,a.hours_log_points,a.real_weekly_log_points]
  labels=['Hourly pay','Consumer prices','Weekly hours','Net real weekly pay']
  bars=ax.bar(labels,values,color=[COLORS[0],COLORS[3],COLORS[2],COLORS[1]],width=.6)
  ax.axhline(0,color='#a6b3c6',lw=.8);ax.set_ylabel('100 × log change, not percentage change')
  for bar,v in zip(bars,values):ax.annotate(f'{v:+.2f}',(bar.get_x()+bar.get_width()/2,v),ha='center',va='bottom' if v>=0 else 'top',xytext=(0,4 if v>=0 else -4),textcoords='offset points')
 chart('wage-decomposition','What accounts for the change in real weekly pay?',f'February 2020 to {df.index[-1]:%B %Y} | Additive log decomposition',decomposition)
 # Scenario surface is explicitly hypothetical, independent of observed charts.
 scenarios=[]
 for inflation in [0,.02,.04,.06,.08]:
  for hours in [-.04,-.02,0,.02,.04]:
   target=.01;raise_req=(1+inflation)*(1+target)/(1+hours)-1
   scenarios.append(dict(assumed_inflation_pct=100*inflation,assumed_hours_change_pct=100*hours,target_real_weekly_change_pct=1,required_hourly_raise_pct=100*raise_req))
 scenarios=pd.DataFrame(scenarios);scenarios.to_csv(OUT/'hypothetical_budget_grid.csv',index=False)
 summary=dict(months=len(df),complete_real_pay_months=int(df.cpi.notna().sum()),missing_cpi_months=[str(x.date()) for x in df.index[df.cpi.isna()]],start=str(df.index[0].date()),end=str(df.index[-1].date()),latest_hourly_usd=float(latest.hourly_usd),latest_weekly_hours=float(latest.weekly_hours),real_hourly_yoy_pct=float(latest.real_hourly_1982_84_usd_yoy_pct),real_weekly_yoy_pct=float(latest.real_weekly_1982_84_usd_yoy_pct),since_feb2020_real_hourly_pct=float(a.real_hourly_1982_84_usd_change_pct),since_feb2020_real_weekly_pct=float(a.real_weekly_1982_84_usd_change_pct),sql_rows_verified=len(check),max_log_identity_error=float(max(abs(anchors.hourly_log_points+anchors.hours_log_points+anchors.inflation_log_points-anchors.real_weekly_log_points))))
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 finding=f'From February 2020 to {df.index[-1]:%B %Y}, real hourly earnings changed {summary["since_feb2020_real_hourly_pct"]:+.1f}% and real weekly earnings changed {summary["since_feb2020_real_weekly_pct"]:+.1f}%. In the latest twelve months, real weekly earnings changed {summary["real_weekly_yoy_pct"]:+.1f}%.'
 limits='These are national private-sector averages, not the pay path of the same workers. Changing employment composition can move the averages. CPI-U does not describe an individual household or Houston specifically. Earnings exclude benefits, employer payroll taxes and irregular bonuses. Historical values are revised; this is not a real-time forecast or an employment recommendation.'
 body=metrics([('Latest nominal hourly earnings',f'${latest.hourly_usd:.2f}'),('Real hourly change, latest 12 months',f'{summary["real_hourly_yoy_pct"]:+.1f}%'),('Real weekly change, latest 12 months',f'{summary["real_weekly_yoy_pct"]:+.1f}%')])
 body+='<h2>The question</h2><p>When nominal pay rises, how much purchasing power remains after prices and weekly hours change? A workforce finance team needs this distinction before translating a broad wage statistic into a payroll assumption.</p><h2>The finding</h2><p>'+finding+'</p><p class="note">This is an accounting decomposition of aggregate series. It does not identify a causal inflation effect or measure raises received by individual workers.</p>'
 body+=figure('wage-index','Observed monthly BLS data. Four series are rebased to February 2020 = 100; real pay divides earnings by CPI-U.')
 body+=figure('wage-growth','Observed year-over-year changes in real hourly and weekly earnings. Hours explain their divergence; workforce composition also affects both measures.')
 body+=figure('wage-decomposition','Observed changes decomposed into hourly pay, consumer prices and hours. Log contributions sum exactly; they are not ordinary percentage-point contributions.')
 body+='<h2>Does the starting point change the result?</h2><p>Three prespecified anchors show the sensitivity to the comparison month. February 2020 is useful for a pre-pandemic comparison, but it is not a neutral universal baseline.</p>'+table(anchors[['anchor','end','real_hourly_1982_84_usd_change_pct','real_weekly_1982_84_usd_change_pct']].rename(columns={'real_hourly_1982_84_usd_change_pct':'Real hourly change (%)','real_weekly_1982_84_usd_change_pct':'Real weekly change (%)'}))
 body+='<h2>Turn the evidence into an explicit assumption</h2><p>The <a href="workbench.html">budget workbench</a> solves for an hourly raise consistent with a chosen inflation rate, hours change and target change in real weekly pay. It is a scenario identity, not a recommended compensation rate.</p><h2>Data and method</h2><p>Inner calendar alignment of three monthly seasonally adjusted series: CES0500000003, AWHAETP and CPIAUCSL. Duplicate dates, missing calendar rows and non-positive observed values fail the build. October 2025 CPI is absent in this export. BLS attributes missing collection to the 2025 federal lapse in appropriations. That month remains missing in real-pay calculations and charts; it is never interpolated or forward-filled. The calendar is retained so twelve-month comparisons do not shift. Real weekly earnings = hourly earnings × weekly hours ÷ CPI × 100. Log changes provide an exact additive bridge. SQL independently reconciles all monthly real weekly calculations.</p><h2>Limitations</h2><p>'+limits+'</p><h2>Inspect the evidence</h2><p><a href="monthly_evidence.csv">Monthly data and calculations</a> · <a href="anchor_sensitivity.csv">Anchor sensitivity</a> · <a href="sql_reconciliation.csv">SQL reconciliation</a> · <a href="hypothetical_budget_grid.csv">Hypothetical budget grid</a> · <a href="summary.json">Machine-readable results</a></p><p>Sources: <a href="https://fred.stlouisfed.org/series/CES0500000003">BLS hourly earnings via FRED</a>, <a href="https://fred.stlouisfed.org/series/AWHAETP">BLS weekly hours via FRED</a>, <a href="https://fred.stlouisfed.org/series/CPIAUCSL">BLS CPI-U via FRED</a>, <a href="https://www.bls.gov/news.release/realer.htm">BLS Real Earnings</a>, <a href="https://www.bls.gov/web/empsit/cesfaq.htm">CES definitions and composition caveats</a>. See also the <a href="https://www.bls.gov/cpi/additional-resources/2025-federal-government-shutdown-impact-cpi-faq.htm">BLS missing CPI explanation</a>. Snapshot hashes and exact export URLs are in the repository data manifest.</p>'
 write_page('report.html','When a pay rise buys less',finding,body)
 work='<p class="note">Hypothetical assumptions. This calculator does not predict inflation or recommend a pay decision. Employee count, benefits, overtime, turnover and employer taxes are outside the calculation.</p><form id="budget"><div class="fields"><div><label for="inflation">Assumed inflation (%)</label><input id="inflation" type="number" min="-20" max="50" step="0.1" value="4" required></div><div><label for="hours">Assumed weekly hours change (%)</label><input id="hours" type="number" min="-50" max="50" step="0.1" value="0" required></div><div><label for="target">Target real weekly pay change (%)</label><input id="target" type="number" min="-50" max="50" step="0.1" value="1" required></div></div><output id="result" aria-live="polite"></output><p id="explain"></p></form><h2>Why the answer changes</h2><p>If hours decline, a larger hourly increase is needed to reach the same real weekly pay target. Required hourly change = (1 + inflation) × (1 + real weekly target) ÷ (1 + hours change) − 1. This multiplicative identity avoids adding percentages as if compounding did not matter.</p><p><a href="hypothetical_budget_grid.csv">Download the scenario grid</a> or <a href="report.html">return to the actual-data evidence</a>.</p><noscript>JavaScript is required for recalculation. The scenario grid remains available as a CSV.</noscript>'
 script='<script src="calculator.js"></script>'
 write_page('workbench.html','What hourly raise would meet a weekly pay target?','Change the assumptions and see the required hourly pay adjustment.',work,script)
 (ROOT/'docs/executive_memo.md').write_text('# Real wages and payroll budgets\n\n'+finding+'\n\n## Decision use\nSeparate hourly pay, hours and consumer prices before choosing a budget assumption. Use the scenario tool to make those assumptions visible.\n\n## Limits\n'+limits+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
