import unittest,json,math,copy,sqlite3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import model
from model import DEFAULT,ROOT,REPORT,evaluate,steady,payment,validate
class UnderwritingTests(unittest.TestCase):
 def test_annuity_known_values_and_zero_rate(self):
  self.assertAlmostEqual(payment(100000,.06,30),599.5505251527569,places=8)
  self.assertAlmostEqual(payment(100000,0,20),100000/240,places=10);self.assertEqual(payment(0,.1,20),0)
 def test_source_totals_all_cases(self):
  for x in REPORT['scenarios'].values():self.assertEqual(sum(x[k] for k in ['store_sales','lottery_ticket_sales','deli_sales','pizza_sales']),x['reported_nonfuel_receipts'])
 def test_receipts_bridge_and_lottery_adjustment(self):
  s=steady(DEFAULT);self.assertAlmostEqual(s['nonfuel_receipts'],138031);self.assertAlmostEqual(s['lottery_commission'],1867.95);self.assertAlmostEqual(s['retained_nonfuel_receipts'],102539.95)
  self.assertAlmostEqual(sum(v for _,v in s['bridge'][:-1]),s['cfads'],places=8)
 def test_commission_change_applies_once(self):
  a=steady(DEFAULT);b=steady({**DEFAULT,'lottery_commission':.06});expected=37359*.01
  self.assertAlmostEqual(b['cfads']-a['cfads'],expected);self.assertAlmostEqual(b['retained_nonfuel_receipts']-a['retained_nonfuel_receipts'],expected)
 def test_labor_uses_calendar_and_loaded_coverage(self):
  self.assertAlmostEqual(steady(DEFAULT)['loaded_labor'],19*365/12*1.5*18*1.18,places=8)
 def test_sql_contribution_reconciles_independently(self):
  import pandas as pd
  con=sqlite3.connect(':memory:');pd.DataFrame([dict(case=k,**v) for k,v in REPORT['scenarios'].items()]).to_sql('report_sales',con,index=False);pd.DataFrame([DEFAULT]).to_sql('assumptions',con,index=False)
  df=pd.read_sql_query((ROOT/'reconcile.sql').read_text(),con)
  for row in df.itertuples():self.assertAlmostEqual(row.net_contribution,steady({**DEFAULT,'report_scenario':row.case})['contribution'],places=8)
 def test_loan_draws_and_capex_sources_reconcile(self):
  r=evaluate(DEFAULT);s=r['steady'];dev=[x for x in r['months'] if x['phase']!='operations']
  self.assertAlmostEqual(sum(x['capex'] for x in dev),s['eligible_budget'],places=6);self.assertAlmostEqual(sum(x['loan_draw'] for x in dev),s['loan'],places=6)
  expected=s['eligible_budget']-s['loan']+r['development_interest']+r['development_carry']+r['loan_fee']+DEFAULT['working_capital'];self.assertAlmostEqual(r['equity_at_opening'],expected,places=6)
 def test_development_interest_is_on_drawn_balances(self):
  r=evaluate(DEFAULT);prev=0
  for x in r['months']:
   if x['phase']=='closing':prev=x['loan_balance'];continue
   if x['phase']=='operations':break
   self.assertAlmostEqual(x['construction_interest'],(prev+x['loan_draw']/2)*DEFAULT['annual_interest_rate']/12,places=8);prev=x['loan_balance']
 def test_delay_adds_draw_aware_carry_not_full_loan_interest(self):
  a=evaluate(DEFAULT);b=evaluate({**DEFAULT,'permit_delay_months':9});initial_draw=(DEFAULT['land_cost']+DEFAULT['soft_cost'])*DEFAULT['loan_to_cost'];delta=9*(DEFAULT['preopening_carry_monthly']+initial_draw*DEFAULT['annual_interest_rate']/12)
  self.assertAlmostEqual(b['equity_at_opening']-a['equity_at_opening'],delta,places=6);self.assertAlmostEqual(b['steady']['dscr'],a['steady']['dscr']);self.assertEqual(b['opening_month']-a['opening_month'],9)
 def test_working_capital_funded_once(self):
  r=evaluate(DEFAULT);self.assertEqual(sum(x['working_capital'] for x in r['months']),DEFAULT['working_capital'])
  z=evaluate({**DEFAULT,'working_capital':0});self.assertAlmostEqual(r['peak_sponsor_funding_36m']-z['peak_sponsor_funding_36m'],DEFAULT['working_capital'],places=6);self.assertEqual(r['year1_cfads'],z['year1_cfads'])
 def test_ramp_and_year_one_use_operating_months(self):
  r=evaluate(DEFAULT);ops=[x for x in r['months'] if x['phase']=='operations'];self.assertEqual(ops[0]['ramp'],.45);self.assertEqual(ops[5]['ramp'],1.);self.assertAlmostEqual(sum(x['cfads'] for x in ops[:12]),r['year1_cfads'])
  a=evaluate({**DEFAULT,'ramp_months':1});self.assertAlmostEqual(a['year1_cfads'],12*a['steady']['cfads'])
 def test_financing_ceiling_hits_target(self):
  s=steady(DEFAULT);c={**DEFAULT,'hard_cost':s['maximum_core_hard_cost']};self.assertAlmostEqual(steady(c)['dscr'],DEFAULT['target_dscr'],places=9)
 def test_all_sales_threshold_hits_target(self):
  s=steady(DEFAULT);self.assertAlmostEqual(steady({**DEFAULT,'sales_multiplier':s['required_sales_multiplier']})['dscr'],DEFAULT['target_dscr'],places=9)
 def test_required_fuel_holds_nonfuel_constant(self):
  s=steady(DEFAULT);report=copy.deepcopy(REPORT);report['scenarios']['average']['fuel_gallons']=s['required_fuel_gallons'];old=model.REPORT
  try:model.REPORT=report;self.assertAlmostEqual(steady(DEFAULT)['dscr'],DEFAULT['target_dscr'],places=9)
  finally:model.REPORT=old
 def test_traffic_denominator_is_explicit(self):
  s=steady({**DEFAULT,'fuel_source':'traffic'});self.assertAlmostEqual(s['gallons'],10200*.5*.03*10*365/12)
  doubled=steady({**DEFAULT,'fuel_source':'traffic','eligible_traffic_share':1});self.assertAlmostEqual(doubled['gallons'],2*s['gallons'])
 def test_all_equity_and_zero_fuel_margin(self):
  r=evaluate({**DEFAULT,'loan_to_cost':0});self.assertIsNone(r['steady']['dscr']);self.assertEqual(r['steady']['monthly_debt_service'],0);self.assertIn('unverified',r['overall_decision'])
  self.assertIsNone(steady({**DEFAULT,'net_fuel_margin':0})['required_fuel_gallons'])
 def test_one_year_loan_does_not_overpay(self):
  r=evaluate({**DEFAULT,'amortization_years':1});ops=[x for x in r['months'] if x['phase']=='operations'];self.assertAlmostEqual(ops[11]['loan_balance'],0,places=5);self.assertLess(ops[12]['debt_service'],.00001)
 def test_peak_funding_matches_independent_cumulative_cash(self):
  r=evaluate(DEFAULT);self.assertAlmostEqual(max(x['cumulative_sponsor_funding'] for x in r['months']),r['peak_sponsor_funding_36m'],places=6)
 def test_wash_includes_incremental_cost_and_labor(self):
  a=steady(DEFAULT);b=steady({**DEFAULT,'scope':'full'});self.assertAlmostEqual(b['eligible_budget']-a['eligible_budget'],450000*1.2);self.assertAlmostEqual(b['loaded_labor']-a['loaded_labor'],60*18*1.18)
 def test_risk_labels_recompute_and_do_not_become_probabilities(self):
  rows=json.loads((ROOT/'data/risk_register.json').read_text());self.assertEqual(len(rows),31);self.assertEqual(sum(x['mismatch'] for x in rows),4);self.assertEqual(sum(x['recomputed_band']=='CRITICAL' for x in rows),1)
  self.assertTrue(all(x['recomputed_score']==x['likelihood']*x['impact'] for x in rows))
 def test_invalid_and_nonfinite_inputs_rejected(self):
  for changes in [{'hard_cost':-1},{'hourly_wage':float('nan')},{'scope':'other'},{'loan_to_cost':1},{'ramp_months':0},{'permit_delay_months':1.5},{'lottery_commission':.01},{'annual_interest_rate':2},{'target_dscr':0}]:
   with self.subTest(changes=changes),self.assertRaises(ValueError):validate({**DEFAULT,**changes})
if __name__=='__main__':unittest.main()
