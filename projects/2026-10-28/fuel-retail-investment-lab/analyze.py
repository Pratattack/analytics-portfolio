"""Regenerate evidence, scenario outputs and charts from sanitized inputs."""
from pathlib import Path
import json,csv,hashlib,sqlite3,copy
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import ROOT,REPORT,DEFAULT,evaluate,steady
OUT=ROOT/'outputs'
plt.rcParams.update({'figure.facecolor':'#0b1420','axes.facecolor':'#0b1420','savefig.facecolor':'#0b1420','text.color':'#edf1f5','axes.labelcolor':'#b9c9da','xtick.color':'#b9c9da','ytick.color':'#b9c9da','axes.edgecolor':'#465d76','grid.color':'#314358','font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'fuel-retail-underwriting-2026','axes.spines.top':False,'axes.spines.right':False})
BLUE='#9cc7f5';GOLD='#e9bc83';GREEN='#8ad4bd';RED='#e3a0a0'
def dump(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def chart(name,title,subtitle,draw):
 fig,ax=plt.subplots(figsize=(11,6));draw(ax);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.35)
 fig.suptitle(title,x=.09,ha='left',fontsize=18,fontweight='bold');fig.text(.09,.88,subtitle,color='#b9c9da',fontsize=10)
 fig.text(.09,.025,'Report estimates + hypothetical assumptions | Not actual operating results | Prathamesh Singh',color='#b9c9da',fontsize=8)
 fig.subplots_adjust(top=.8,bottom=.17,left=.1,right=.95)
 fig.savefig(OUT/(name+'.svg'),metadata={'Date':None})
 # Internal chart QA is not a screenshot or browser test.
 preview=ROOT.parents[3].parent/'review-assets';preview.mkdir(exist_ok=True)
 fig.savefig(preview/(name+'.png'),dpi=120);plt.close(fig)

def main():
 base=evaluate(DEFAULT);s=base['steady'];dump(OUT/'reference_results.json',base)
 pd.DataFrame(base['months']).to_csv(OUT/'reference_monthly_cash_flow.csv',index=False,float_format='%.8f')
 pd.DataFrame(s['bridge'],columns=['component','usd_per_month']).to_csv(OUT/'cash_bridge.csv',index=False,float_format='%.8f')
 report_rows=[dict(case=k,**v) for k,v in REPORT['scenarios'].items()];pd.DataFrame(report_rows).to_csv(OUT/'report_estimate_reconciliation.csv',index=False)
 risks=json.loads((ROOT/'data/risk_register.json').read_text());pd.DataFrame(risks).to_csv(OUT/'risk_register_audit.csv',index=False)
 checks=[]
 for row in report_rows:
  total=sum(row[k] for k in ['store_sales','lottery_ticket_sales','deli_sales','pizza_sales']);assert total==row['reported_nonfuel_receipts'];checks.append(dict(case=row['case'],recomputed_total=total,reported_total=row['reported_nonfuel_receipts'],difference=0))
 pd.DataFrame(checks).to_csv(OUT/'source_total_checks.csv',index=False)
 # Independent SQL computes category contribution and reconciles the lottery adjustment.
 con=sqlite3.connect(':memory:');pd.DataFrame(report_rows).to_sql('report_sales',con,index=False)
 pd.DataFrame([DEFAULT]).to_sql('assumptions',con,index=False)
 query=(ROOT/'reconcile.sql').read_text();sql=pd.read_sql_query(query,con)
 for row in sql.itertuples():
  c={**DEFAULT,'report_scenario':row.case};r=steady(c)
  assert abs(row.retained_nonfuel_receipts-r['retained_nonfuel_receipts'])<1e-8
  assert abs(row.net_contribution-r['contribution'])<1e-8
 sql.to_csv(OUT/'sql_reconciliation.csv',index=False,float_format='%.8f')
 scenarios=[];case_configs=[]
 for case in ['low','average','high']:
  for scope in ['core','full']:
   for delay in [0,3,6,9]:
    c={**DEFAULT,'report_scenario':case,'scope':scope,'permit_delay_months':delay};r=evaluate(c);a=r['steady']
    scenarios.append(dict(report_case=case,scope=scope,delay_months=delay,eligible_budget=a['eligible_budget'],stabilized_cfads_monthly=a['cfads'],monthly_debt_service=a['monthly_debt_service'],stabilized_dscr=a['dscr'],year1_dscr=r['year1_dscr'],equity_at_opening=r['equity_at_opening'],peak_sponsor_funding_36m=r['peak_sponsor_funding_36m'],development_interest=r['development_interest'],development_carry=r['development_carry'],illustrative_coverage_pass=a['illustrative_coverage_pass'],evidence_gates='Unverified'))
    case_configs.append(c)
 pd.DataFrame(scenarios).to_csv(OUT/'scenario_comparison.csv',index=False,float_format='%.8f')
 changes=[('All sales','sales_multiplier',.8,1.2),('Core construction','hard_cost',1500000,2300000),('Fuel contribution / gallon','net_fuel_margin',.10,.40),('Store gross margin','store_margin',.25,.39),('Concurrent staff','average_staff_on_duty',1.25,1.75),('Loan interest rate','annual_interest_rate',.065,.105)]
 sensitivity=[]
 for label,key,low,high in changes:
  lo=steady({**DEFAULT,key:low});hi=steady({**DEFAULT,key:high});sensitivity.append(dict(driver=label,key=key,low_input=low,high_input=high,low_dscr=lo['dscr'],high_dscr=hi['dscr'],reference_dscr=s['dscr']))
 pd.DataFrame(sensitivity).to_csv(OUT/'one_at_a_time_sensitivity.csv',index=False,float_format='%.8f')
 grid=[]
 for volume in np.linspace(.7,1.3,13):
  for hard in np.linspace(1200000,2600000,15):
   q=steady({**DEFAULT,'sales_multiplier':float(volume),'hard_cost':float(hard)})
   grid.append(dict(sales_multiplier=float(volume),core_hard_cost=float(hard),stabilized_dscr=q['dscr'],passes_illustrative_target=q['illustrative_coverage_pass']))
 pd.DataFrame(grid).to_csv(OUT/'coverage_frontier.csv',index=False,float_format='%.8f')
 def receipts(ax):
  vals=[s['nonfuel_receipts'],s['retained_nonfuel_receipts'],s['contribution'],s['cfads'],s['monthly_debt_service']]
  names=['Nonfuel\nreceipts','Nonfuel retained\nafter lottery transfer','All-category\ncontribution','Cash available\nfor debt','Debt\nservice']
  bars=ax.bar(names,np.array(vals)/1000,color=[BLUE,BLUE,GOLD,GREEN,RED],width=.58)
  ax.set_ylabel('USD thousands per stabilized month')
  for b,v in zip(bars,vals):ax.annotate(f'${v/1000:,.1f}k',(b.get_x()+b.get_width()/2,b.get_height()),ha='center',va='bottom',xytext=(0,7),textcoords='offset points',fontsize=10)
 chart('receipts-to-cash','Sales can reconcile while debt coverage falls short','Reference illustration | Average report sales, core scope | Contribution includes net fuel income',receipts)
 def frontier(ax):
  df=pd.DataFrame(grid);pivot=df.pivot(index='sales_multiplier',columns='core_hard_cost',values='stabilized_dscr');im=ax.imshow(pivot.values,origin='lower',aspect='auto',extent=[1.15,2.65,.675,1.325],cmap='RdYlBu',vmin=.3,vmax=2.2)
  xs=pivot.columns.values/1e6;ys=pivot.index.values;ax.contour(xs,ys,pivot.values,levels=[DEFAULT['target_dscr']],colors=['#0b1420'],linewidths=2)
  ax.plot(DEFAULT['hard_cost']/1e6,1,marker='o',color='#fff',markeredgecolor='#0b1420',markersize=9,label=f'Reference: {s["dscr"]:.2f}x')
  ax.set_xlabel('Core hard-cost input before contingency (USD millions)');ax.set_ylabel('All sales / selected report estimate');ax.legend(frameon=True,facecolor='#101d2c',loc='upper right');plt.colorbar(im,ax=ax,label='Stabilized cash / debt service')
 chart('coverage-frontier','Where does the illustrative financing screen change?','Black contour: 1.25x coverage | Fixed margins, staffing, debt share and all other reference inputs',frontier)
 def funding(ax):
  for delay,color in [(0,BLUE),(9,GOLD)]:
   r=evaluate({**DEFAULT,'permit_delay_months':delay});df=pd.DataFrame(r['months']);ax.plot(df.month,df.cumulative_sponsor_funding/1e6,lw=2,color=color,label=f'{delay} added delay months')
  ax.set_xlabel('Months since closing');ax.set_ylabel('Cumulative sponsor cash invested (USD millions)');ax.legend(frameon=False)
 chart('sponsor-funding','Development draws and ramp losses consume sponsor cash','Interest on staged draws | Opening inventory/working capital is separate from the operating loss reserve',funding)
 def tornado(ax):
  ss=sorted(sensitivity,key=lambda x:abs(x['high_dscr']-x['low_dscr']))
  for i,x in enumerate(ss):ax.plot([x['low_dscr'],x['high_dscr']],[i,i],lw=8,color=BLUE,solid_capstyle='butt');ax.plot(x['low_dscr'],i,'o',color=GOLD);ax.plot(x['high_dscr'],i,'o',color=GREEN)
  ax.set_yticks(range(len(ss)));ax.set_yticklabels([x['driver'] for x in ss],fontsize=9);ax.axvline(s['dscr'],color='#b9c9da',ls=':');ax.axvline(DEFAULT['target_dscr'],color=RED,ls='--');ax.set_xlabel('Stabilized debt coverage (x)');ax.set_xlim(left=min(.1,min(min(x['low_dscr'],x['high_dscr']) for x in ss))-.05)
  ax.figure.subplots_adjust(left=.25);ax.grid(False)
 chart('coverage-sensitivity','Staffing and contribution assumptions can reverse the screen','One input at a time | Gold: lower input, green: higher input | Dashed line: 1.25x target',tornado)
 fixtures=case_configs+[dict(DEFAULT,**c) for c in [{'loan_to_cost':0},{'annual_interest_rate':0},{'net_fuel_margin':0},{'fuel_source':'traffic'},{'sales_multiplier':0},{'ramp_months':1},{'amortization_years':1},{'ramp_months':24,'ramp_start':0.1},{'permit_delay_months':36,'construction_months':1}]]
 dump(OUT/'parity_fixtures.json',[dict(config=c,result=evaluate(c)) for c in fixtures])
 full=evaluate({**DEFAULT,'scope':'full'});delay=evaluate({**DEFAULT,'permit_delay_months':9})
 summary=dict(reference_stabilized_dscr=s['dscr'],reference_year1_dscr=base['year1_dscr'],reference_cfads_monthly=s['cfads'],reference_debt_service_monthly=s['monthly_debt_service'],reference_peak_sponsor_funding_36m=base['peak_sponsor_funding_36m'],financing_capacity_eligible_budget=s['maximum_supported_eligible_budget'],required_sales_multiplier=s['required_sales_multiplier'],required_fuel_gallons=s['required_fuel_gallons'],full_scope_stabilized_dscr=full['steady']['dscr'],nine_month_delay_extra_opening_funding=delay['equity_at_opening']-base['equity_at_opening'],risk_records=len(risks),risk_band_mismatches=sum(r['mismatch'] for r in risks),unverified_evidence_gates=8,scenario_count=len(scenarios),coverage_grid_points=len(grid),python_javascript_parity_cases=len(fixtures),source_totals_reconcile=True)
 dump(OUT/'summary.json',summary)
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
