import unittest,json,math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import stress,ROOT
class CreditTests(unittest.TestCase):
 def setUp(self):self.rows=json.loads((ROOT/'data/vehicle_balance_sheets.json').read_text())
 def test_missing_equity_is_not_zero(self):self.assertIsNone(self.rows[-1]['equity']);self.assertEqual(len(stress(self.rows)),3)
 def test_rounded_balance_identity(self):
  for r in self.rows[:3]:self.assertLessEqual(abs(r['assets']-r['liabilities']-r['equity']),1.5)
 def test_zero_mark_recovers_source(self):
  for r,s in zip(self.rows,stress(self.rows,0,0)):
   self.assertEqual(s['loss'],0);self.assertAlmostEqual(s['equity_share'],r['equity']/r['assets'])
 def test_marks_preserve_liabilities_and_rounding(self):
  for r,s in zip(self.rows,stress(self.rows,.1,.2)):
   self.assertAlmostEqual(s['stressed_assets']-r['liabilities']-s['stressed_equity'],r['balance_rounding_residual'])
 def test_reverse_screen_solves_identity(self):
  for i,x in enumerate(stress(self.rows,.1,.2,.25)):
   h=x['loan_mark_at_floor_raw']
   if 0<=h<=1:self.assertAlmostEqual(stress(self.rows,h,.2,.25)[i]['equity_share'],.25)
 def test_scopes_are_not_mixed(self):
  s=json.loads((ROOT/'outputs/summary.json').read_text());self.assertEqual(s['us_business_private_credit_billions'],1458);self.assertEqual(s['nonfinancial_private_credit_billions'],1310);self.assertAlmostEqual(s['nonfinancial_debt_share_pct'],1.31/23.29*100)
 def test_invalid_inputs(self):
  for args in [(2,0,.25),(0,-.1,.25),(0,0,1),(float('nan'),0,.25)]:
   with self.assertRaises(ValueError):stress(self.rows,*args)
