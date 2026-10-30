import unittest,sys
from pathlib import Path
import pandas as pd,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import plan,evaluate
class ModelTests(unittest.TestCase):
 def test_zero_turnover(self):
  r=plan(separation=0);self.assertAlmostEqual(r['total_hires'],100);self.assertAlmostEqual(r['replacements'],0)
 def test_target_reached(self):
  r=plan();self.assertAlmostEqual(r['achieved_headcount'],1100)
 def test_replacement_identity(self):
  r=plan();self.assertAlmostEqual(r['total_hires']-r['replacements'],100)
 def test_steady_headcount(self):
  r=plan(growth=0);self.assertAlmostEqual(r['monthly_hires'],35);self.assertAlmostEqual(r['replacements'],r['total_hires'])
 def test_capacity_parity(self):
  r=plan();s=plan(capacity=r['monthly_hires']);self.assertAlmostEqual(s['capacity_gap'],0)
 def test_reduction_below_zero_hire_floor(self):
  r=plan(growth=-.8,separation=.01);self.assertTrue(r['target_requires_additional_separations']);self.assertEqual(r['monthly_hires'],0);self.assertGreater(r['achieved_headcount'],r['target_headcount'])
 def test_cost(self):
  r=plan(cost=2500);self.assertAlmostEqual(r['budget'],r['total_hires']*2500)
 def test_forecast_temporal_boundaries(self):
  s=pd.Series(np.arange(140)/100,index=pd.date_range('2015-01-01',periods=140,freq='MS'));r=evaluate(s);self.assertTrue((r.origin<r.target_start).all());self.assertTrue((r[r.split=='validation'].target_end<pd.Timestamp('2025-01-01')).all());self.assertTrue((r[r.split=='holdout'].target_start>=pd.Timestamp('2025-01-01')).all())
 def test_future_targets_not_features(self):
  s=pd.Series(np.arange(140)/100,index=pd.date_range('2015-01-01',periods=140,freq='MS'));r=evaluate(s);s.loc['2026-06-01':]=99;t=evaluate(s);a=r[r.target_start==pd.Timestamp('2026-06-01')].prediction.to_numpy();b=t[t.target_start==pd.Timestamp('2026-06-01')].prediction.to_numpy();np.testing.assert_array_equal(a,b)
 def test_invalid(self):
  with self.assertRaises(ValueError):plan(months=12.5)
if __name__=='__main__':unittest.main()
