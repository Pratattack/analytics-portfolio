"""Economic and accounting invariants, plus SQL audit of reported facts."""
import copy,csv,json,sqlite3,unittest
from pathlib import Path
from model import inputs,simulate,valuation,ROOT

class ModelTests(unittest.TestCase):
 def test_all_cases_balance_and_cash(self):
  for sym in ['URI','CROX']:
   d=inputs(sym)
   for case in ['base','down','up']:
    for r in simulate(d,case):
     self.assertAlmostEqual(r['assets'],r['liabilities']+r['closing_equity'],7)
     self.assertAlmostEqual(r['opening_cash']+r['cfo']+r['cfi']+r['cff'],r['closing_cash'],7)
     self.assertGreaterEqual(r['closing_cash']+1e-8,d['globals']['min_cash'])
     self.assertLessEqual(r['buybacks']+r['dividends'],r['surplus']+1e-8)
 def test_impairment_is_noncash_and_nondeductible(self):
  d=inputs('CROX');a=simulate(d,'down');b=simulate(d,'down',{'impairment':[0]*5})
  self.assertAlmostEqual(a[0]['cfo'],b[0]['cfo'],8)
  self.assertAlmostEqual(a[0]['tax'],b[0]['tax'],8)
  self.assertAlmostEqual(b[0]['net_income']-a[0]['net_income'],200,8)
  self.assertAlmostEqual(b[0]['assets']-a[0]['assets'],200,8)
 def test_dividends_and_buybacks_stop_when_cash_falls(self):
  d=inputs('URI');r=simulate(d,'down',{'productivity':[-.6,0,0,0,0]})[0]
  self.assertEqual(r['buybacks'],0);self.assertEqual(r['dividends'],0)
  self.assertGreater(r['new_borrowing_required'],0)
 def test_lower_wacc_increases_value(self):
  for sym in ['URI','CROX']:
   d=inputs(sym);r=simulate(d)
   self.assertGreater(valuation(d,r,wacc=.09)['per_share'],valuation(d,r,wacc=.12)['per_share'])
 def test_invalid_discount_rate_rejected(self):
  d=inputs('URI')
  with self.assertRaises(ValueError):valuation(d,simulate(d),wacc=.02,growth=.03)
 def test_buybacks_change_eps_not_enterprise_cashflows(self):
  d=inputs('CROX');base=simulate(d);none=simulate(d,overrides={'repurchases':[0]*5})
  self.assertAlmostEqual(base[0]['ufcf'],none[0]['ufcf'],8)
  self.assertGreater(base[0]['eps'],none[0]['eps'])
 def test_later_driver_changes_future_not_past(self):
  d=inputs('CROX');base=simulate(d);g=d['drivers']['crocs_dtc_growth']['base'].copy();g[2]-=.02
  alt=simulate(d,overrides={'crocs_dtc_growth':g})
  self.assertEqual(base[1]['revenue'],alt[1]['revenue']);self.assertLess(alt[2]['revenue'],base[2]['revenue'])

def sql_audit():
 con=sqlite3.connect(ROOT/'data/audit.sqlite');con.execute('DROP TABLE IF EXISTS actuals')
 con.execute('CREATE TABLE actuals(company TEXT,period TEXT,metric TEXT,value REAL)')
 for sym in ['URI','CROX']:
  d=inputs(sym)
  for period,obj in list(d['historical'].items())+[(f'9M{y}',x)for y,x in d['interim'].items()]:
   con.executemany('INSERT INTO actuals VALUES(?,?,?,?)',[(sym,period,k,v)for k,v in obj.items()if v is not None])
 con.commit();sql=(ROOT/'src/reconcile.sql').read_text();cur=con.execute(sql)
 rows=cur.fetchall()
 with (ROOT/'outputs/sql_reconciliations.csv').open('w')as f:
  w=csv.writer(f);w.writerow([x[0]for x in cur.description]);w.writerows(rows)
 for row in rows:
  assert abs(row[-1])<.001,row
 return len(rows)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ModelTests))
 n=sql_audit();(ROOT/'qa/analysis-validation.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'sql_reconciliations':n},indent=2))
 if not result.wasSuccessful():raise SystemExit(1)
