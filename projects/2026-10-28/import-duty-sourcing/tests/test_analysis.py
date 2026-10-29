import unittest,json
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import sourcing,ROOT
class TradeTests(unittest.TestCase):
 def test_source_totals_reconcile(self):
  for y in [2025,2026]:
   d=pd.read_csv(ROOT/f'data/raw/product-country-{y}.csv',dtype={'hs4':str});tot=json.loads((ROOT/f'data/published-totals-{y}.json').read_text())
   for h,v in tot.items():self.assertEqual(d[d.hs4==h][['value_aug','duty_aug','value_ytd','duty_ytd']].sum().tolist(),v)
 def test_zero_value_duties_not_silently_dropped(self):
  for y in [2025,2026]:
   d=pd.read_csv(ROOT/f'data/raw/product-country-{y}.csv')
   for b in ['aug','ytd']:self.assertEqual(d.loc[d['value_'+b]==0,'duty_'+b].sum(),0)
 def test_decomposition_identity(self):
  d=pd.read_csv(ROOT/'outputs/duty_decomposition.csv')
  for x in d.itertuples():self.assertAlmostEqual(x.within_cell_change+x.mix_change,x.balanced_rate_change,places=8)
 def test_common_cells_are_positive_and_same_description(self):
  d=pd.read_csv(ROOT/'outputs/balanced_cells.csv');self.assertTrue((d.value_0>0).all() and (d.value_1>0).all());self.assertTrue((d.description_0==d.description_1).all())
 def test_pair_gate_and_standardization(self):
  p=pd.read_csv(ROOT/'outputs/eligible_sourcing_pairs.csv',dtype={'hs4':str,'source_country':str,'alternative_country':str});self.assertTrue((p.source_basket_coverage>=.8).all())
  d=pd.read_csv(ROOT/'data/raw/product-country-2026.csv',dtype={'hts10':str,'hs4':str,'country':str});p=p.iloc[0];a=d[(d.hs4==p.hs4)&(d.country==p.source_country)&(d.value_ytd>0)];b=d[(d.hs4==p.hs4)&(d.country==p.alternative_country)&(d.value_ytd>0)];m=a.merge(b,on='hts10',suffixes=('_s','_d'));m=m[m.description_s==m.description_d];w=m.value_ytd_s/m.value_ytd_s.sum();self.assertAlmostEqual(float((w*m.duty_ytd_d/m.value_ytd_d).sum()),p.alternative_fixed_basket_duty_ratio,places=8)
 def test_zero_shift_and_break_even(self):
  self.assertEqual(sourcing(100,0,.2,.1,0,50)['incremental_budget'],0)
  x=sourcing(1000000,.5,.2,.1,.02,10000);self.assertAlmostEqual(sourcing(1000000,.5,.2,.1,x['maximum_premium_for_breakeven'],10000)['incremental_budget'],0,places=7)
 def test_invalid_scenarios(self):
  for args in [(-1,.2,.1,.1,0,0),(1,2,.1,.1,0,0),(1,.2,.1,.1,-1,0)]:
   with self.assertRaises(ValueError):sourcing(*args)
