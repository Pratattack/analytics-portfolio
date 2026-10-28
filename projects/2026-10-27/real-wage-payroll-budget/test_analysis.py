import unittest,json,hashlib
import numpy as np,pandas as pd
from presentation import ROOT,OUT,load
class WageEvidenceTests(unittest.TestCase):
 def setUp(self):self.df=pd.read_csv(OUT/'monthly_evidence.csv',index_col='date')
 def test_source_integrity(self):
  for s in json.loads((ROOT/'data/source_manifest.json').read_text())['sources']:
   b=(ROOT/'data/raw'/(s['series']+'.csv')).read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),s['sha256']);self.assertEqual(len(b),s['bytes'])
 def test_calendar_gap_is_retained(self):
  self.assertEqual(len(self.df),237);self.assertTrue(np.isnan(self.df.loc['2025-10-01','cpi']));self.assertTrue(np.isnan(self.df.loc['2025-10-01','real_weekly_1982_84_usd']))
  self.assertEqual(int(self.df.cpi.isna().sum()),1)
 def test_no_implicit_cpi_forward_fill(self):
  # A missing October cannot become a spurious zero inflation observation.
  self.assertTrue(np.isnan(self.df.loc['2025-10-01','cpi_yoy_pct']))
  self.assertTrue(np.isnan(self.df.loc['2025-10-01','real_hourly_1982_84_usd_yoy_pct']))
 def test_raw_latest_reproduces_headline(self):
  h=load('CES0500000003');c=load('CPIAUCSL');real=h/c
  expected=(real.iloc[-1]/real.iloc[-13]-1)*100
  self.assertAlmostEqual(expected,json.loads((OUT/'summary.json').read_text())['real_hourly_yoy_pct'],places=10)
 def test_exact_bridge_all_anchors(self):
  d=pd.read_csv(OUT/'anchor_sensitivity.csv');self.assertTrue(np.allclose(d.hourly_log_points+d.hours_log_points+d.inflation_log_points,d.real_weekly_log_points,atol=1e-8))
 def test_sql_independent_reconciliation(self):
  d=pd.read_csv(OUT/'sql_reconciliation.csv');self.assertTrue(np.allclose(d.real_weekly_1982_84_usd,self.df.real_weekly_1982_84_usd,equal_nan=True,atol=1e-8))
 def test_scenario_grid_inverts_identity(self):
  d=pd.read_csv(OUT/'hypothetical_budget_grid.csv');actual=(1+d.required_hourly_raise_pct/100)*(1+d.assumed_hours_change_pct/100)/(1+d.assumed_inflation_pct/100)-1
  self.assertTrue(np.allclose(actual,.01,atol=1e-12))
if __name__=='__main__':unittest.main()
