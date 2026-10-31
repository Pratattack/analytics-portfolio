import unittest,sys,json
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import stress,paired,build_panel
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_zero_stress(self):self.assertEqual(stress(200,100,0,0,0,0)['retained'],100)
 def test_growth_boundary(self):
  x=stress(200,100,0,0,0,20);self.assertAlmostEqual(stress(200,100,0,x['maximum_capex_growth'],0,20)['gap_to_target'],0)
 def test_cash_decline_boundary(self):
  x=stress(200,100,0,.1,0,20);self.assertAlmostEqual(stress(200,100,x['maximum_cfo_decline'],.1,0,20)['gap_to_target'],0)
 def test_monotonicity(self):self.assertLess(stress(200,100,.1)['retained'],stress(200,100)['retained'])
 def test_invalid(self):
  with self.assertRaises(ValueError):stress(0,100)
 def test_common_calendar_window(self):
  x=pd.read_csv(ROOT/'outputs/latest_comparable_ttm.csv');self.assertEqual(set(x.period_start),{'2025-10-01'});self.assertEqual(set(x.end),{'2026-09-30'});self.assertEqual(len(x),3)
 def test_no_fiscal_ytd_scope_mixing(self):
  x=pd.read_csv(ROOT/'outputs/current_fiscal_ytd.csv');self.assertEqual(x[x.symbol=='MSFT'].start.item(),'2026-07-01');self.assertEqual(x[x.symbol=='GOOGL'].start.item(),'2026-01-01')
 def test_paired_filing_and_time_cutoff(self):
  facts=json.loads((ROOT/'data/companyfacts_selected.json').read_text());p=paired(facts,'GOOGL','2026-01-01','2026-09-30');self.assertEqual(p['cfo']['accn'],p['capex']['accn']);self.assertLessEqual(p['cfo']['filed'],'2026-10-30')
 def test_no_unsupported_substitution(self):
  facts=json.loads((ROOT/'data/companyfacts_selected.json').read_text())
  with self.assertRaises(ValueError):paired(facts,'AMZN','2026-01-01','2026-09-30')
 def test_original_audit_and_sql(self):
  cells=pd.read_csv(ROOT/'outputs/original_filing_reconciliation.csv');self.assertEqual(len(cells),18);self.assertTrue((cells.difference==0).all());p=pd.read_csv(ROOT/'outputs/ttm_panel.csv');s=pd.read_csv(ROOT/'outputs/sql_ttm.csv');self.assertEqual(len(s),2*len(p))
if __name__=='__main__':unittest.main()
