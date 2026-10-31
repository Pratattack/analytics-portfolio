import unittest,json,sys,hashlib,subprocess,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from model import bill,twelve_cycles,exit_fee
PLANS=json.loads((ROOT/'data/plans.json').read_text());BY_ID={p['id']:p for p in PLANS}
PROFILES=json.loads((ROOT/'data/scenarios.json').read_text())['profiles']

class AuditTests(unittest.TestCase):
 def test_all_21_published_prices(self):
  for p in PLANS:
   for q,expected in zip([500,1000,2000],p['published_cents']):
    with self.subTest(plan=p['id'],q=q):self.assertLessEqual(abs(bill(p,q)['effective_cents']-expected),.05000001)
 def test_threshold_credit_inclusive(self):
  p=BY_ID['discount-credit-12'];self.assertEqual(bill(p,999)['credit'],0);self.assertEqual(bill(p,1000)['credit'],125)
 def test_bill_can_rise_when_usage_falls(self):
  p=BY_ID['discount-credit-12'];self.assertAlmostEqual(bill(p,999)['total']-bill(p,1000)['total'],124.807241)
 def test_lower_threshold_inclusive(self):
  p=BY_ID['payless-prepaid-12'];self.assertEqual(bill(p,500)['credit'],15);self.assertEqual(bill(p,501)['credit'],0)
 def test_prepaid_short_cycle(self):
  p=BY_ID['payless-prepaid-12'];b=bill(p,400,days=15);self.assertEqual(b['credit'],7.5);self.assertAlmostEqual(b['total'],400*.149993+12.45+2.45-7.5)
 def test_daily_fee_31_days(self):
  p=BY_ID['payless-prepaid-12'];self.assertAlmostEqual(bill(p,1000,31)['total']-bill(p,1000,30)['total'],.83)
 def test_no_interpolation_across_threshold(self):
  p=BY_ID['discount-credit-12'];a=bill(p,500)['total'];b=bill(p,1000)['total'];self.assertNotAlmostEqual((a+b)/2,bill(p,750)['total'])
 def test_equal_total_usage(self):self.assertEqual(sum(PROFILES[0]['usage']),sum(PROFILES[1]['usage']))
 def test_750_difference(self):
  p=BY_ID['discount-credit-12'];self.assertAlmostEqual(twelve_cycles(p,PROFILES[1]['usage'])['total']-twelve_cycles(p,PROFILES[0]['usage'])['total'],750)
 def test_flat_price_equal_total(self):
  p=BY_ID['discount-basic-36'];self.assertAlmostEqual(twelve_cycles(p,PROFILES[1]['usage'])['total'],twelve_cycles(p,PROFILES[0]['usage'])['total'])
 def test_no_unknown_renewal(self):
  for name in ['goodcharlie-9','payless-prepaid-6']:
   with self.assertRaises(ValueError):twelve_cycles(BY_ID[name],[1000]*12)
 def test_invalid_inputs(self):
  for q,d in [(0,30),(-1,30),(float('nan'),30),(float('inf'),30),(1000,0),(1000,32),(1000,float('nan'))]:
   with self.subTest(q=q,d=d),self.assertRaises(ValueError):bill(PLANS[0],q,d)
 def test_normalization_changes_delivery_only(self):
  p=BY_ID['goodcharlie-9'];self.assertAlmostEqual(bill(p,1000,normalized=True)['total']-bill(p,1000)['total'],1.203)
 def test_exit_fee_contract_length(self):
  self.assertEqual(exit_fee(BY_ID['goodcharlie-9'],3),120);self.assertEqual(exit_fee(BY_ID['goodcharlie-9'],9),0);self.assertEqual(exit_fee(BY_ID['discount-credit-12'],3),150)
 def test_identical_price_functions_different_terms(self):
  a,b=BY_ID['discount-credit-12'],BY_ID['discount-credit-24'];self.assertEqual(bill(a,1200),bill(b,1200));self.assertNotEqual(exit_fee(a,3),exit_fee(b,3))
 def test_source_hashes(self):
  sources={s['id']:s for s in json.loads((ROOT/'data/source_manifest.json').read_text())}
  if not all((ROOT/f"data/raw/{p['source_id']}.pdf").exists() for p in PLANS):self.skipTest('Provider PDFs are not redistributed. Run src/download_sources.py to attempt source reverification.')
  for p in PLANS:
   s=sources[p['source_id']];self.assertEqual(hashlib.sha256((ROOT/f"data/raw/{s['id']}.pdf").read_bytes()).hexdigest(),s['sha256'])
 def test_data_complete(self):
  self.assertEqual(len(BY_ID),len(PLANS))
  for p in PLANS:
   self.assertTrue(p['efl_date']<='2026-10-31');self.assertGreater(p['term_months'],0);self.assertEqual(len(p['published_cents']),3);self.assertIn(p['credit_rule'],['none','lte','gte'])
 def test_sql_reconciles_rows(self):
  con=sqlite3.connect(ROOT/'results/audit.sqlite');self.assertEqual(con.execute('SELECT COUNT(*) FROM price_audit WHERE within_rounding=1').fetchone()[0],21)
 def test_sql_scenario_difference(self):
  con=sqlite3.connect(ROOT/'results/audit.sqlite');v=con.execute("SELECT b.cost_dollars-a.cost_dollars FROM scenarios a JOIN scenarios b USING(plan_id) WHERE a.plan_id='discount-credit-12' AND a.profile_id='steady' AND b.profile_id='seasonal'").fetchone()[0];self.assertAlmostEqual(v,750)
 def test_python_javascript_parity(self):
  cases=[dict(p=p,q=q,days=d) for p in PLANS for q in [249,499,500,501,999,1000,1001,2000,4000] for d in [15,30,31]]
  script="const fs=require('fs'),m=require('./app/model.js'),cases=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(cases.map(x=>m.bill(x.p,x.q,x.days,true))));"
  out=json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT,input=json.dumps(cases).encode()))
  for c,b in zip(cases,out):self.assertAlmostEqual(bill(c['p'],c['q'],c['days'],True)['total'],b['total'],places=8)
 def test_browser_horizon_parity(self):
  p=BY_ID['discount-credit-12'];profile=PROFILES[1]['usage'];s="const m=require('./app/model.js');console.log(JSON.stringify(m.twelveCycles("+json.dumps(p)+","+json.dumps(profile)+")));";out=json.loads(subprocess.check_output(['node','-e',s],cwd=ROOT));self.assertAlmostEqual(out['total'],twelve_cycles(p,profile)['total'])

if __name__=='__main__':unittest.main(verbosity=2)
