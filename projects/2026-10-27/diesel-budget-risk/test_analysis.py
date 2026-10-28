import unittest,json,hashlib
import numpy as np,pandas as pd
from presentation import ROOT,OUT,load
from analyze import make_blocks,history,reserve,pinball
class FuelEvidenceTests(unittest.TestCase):
 def test_source_hash_and_complete_weekly_calendar(self):
  for s in json.loads((ROOT/'data/source_manifest.json').read_text())['sources']:
   b=(ROOT/'data/raw'/(s['series']+'.csv')).read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),s['sha256'])
  s=load('GASDESW');self.assertEqual(len(s),1035);self.assertTrue(s.notna().all());self.assertTrue((s.index.to_series().diff().dropna()==pd.Timedelta(days=7)).all())
 def test_nonoverlapping_complete_targets(self):
  b=make_blocks(load('GASDESW'));starts=pd.to_datetime(b.origin);ends=pd.to_datetime(b.end)
  self.assertTrue((ends-starts==pd.Timedelta(days=84)).all());self.assertTrue((starts.iloc[1:].to_numpy()>ends.iloc[:-1].to_numpy()).all())
 def test_no_target_or_quote_leakage(self):
  e=pd.read_csv(OUT/'budget_evaluation.csv');origin=pd.to_datetime(e.origin)
  self.assertTrue((pd.to_datetime(e.quote_date)==origin-pd.Timedelta(days=7)).all());self.assertTrue((pd.to_datetime(e.training_last_end)<=origin-pd.Timedelta(days=7)).all());self.assertTrue((e.training_blocks>=20).all())
 def test_future_price_mutation_cannot_change_past_budget(self):
  s=load('GASDESW');b=make_blocks(s);row=b[b.origin>='2020-01-01'].iloc[0];r=reserve(history(b,row),'all')
  mutated=s.copy();mutated.loc[pd.Timestamp(row.origin):]*=10;b2=make_blocks(mutated)
  self.assertEqual(r,reserve(history(b2,row),'all'))
 def test_selection_uses_validation_only(self):
  v=pd.read_csv(OUT/'validation_selection.csv',dtype={'window':str});s=json.loads((OUT/'summary.json').read_text());self.assertEqual(s['validation_selected_window'],v.sort_values('mean_pinball_usd_per_gallon',kind='stable').iloc[0]['window']);self.assertTrue((v.validation_blocks==16).all())
 def test_undercoverage_reported_honestly(self):
  e=pd.read_csv(OUT/'budget_evaluation.csv');g=e[(e.period=='holdout_2020_2026')&(e.rule=='Historical q90')];s=json.loads((OUT/'summary.json').read_text());self.assertEqual(len(g),26);self.assertEqual(int(g.covered.sum()),20);self.assertAlmostEqual(s['holdout_coverage_pct'],100*g.covered.mean())
 def test_sql_quarter_means(self):
  a=pd.read_csv(OUT/'sql_quarter_reconciliation.csv');b=pd.read_csv(OUT/'completed_13week_blocks.csv');self.assertTrue((a.weeks==13).all());self.assertTrue(np.allclose(a.sql_mean,b.actual_mean,atol=1e-8))
 def test_shortfall_unused_exclusive_and_reconcile(self):
  e=pd.read_csv(OUT/'budget_evaluation.csv');self.assertTrue((e.shortfall_per_gallon*e.unused_per_gallon==0).all());self.assertTrue(np.allclose(e.actual_mean-e.budget_per_gallon,e.shortfall_per_gallon-e.unused_per_gallon,atol=1e-8))
 def test_pinball_asymmetry(self):
  self.assertAlmostEqual(float(pinball(2,1)),.9);self.assertAlmostEqual(float(pinball(1,2)),.1)
if __name__=='__main__':unittest.main()
