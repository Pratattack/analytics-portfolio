import unittest,sys,json
from pathlib import Path
import pandas as pd,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import cvar,evaluate,fit
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_cvar_fractional_tail(self):self.assertAlmostEqual(cvar([0,10,20,30],.5),25)
 def test_negative_tail_not_floored(self):self.assertEqual(cvar([-10,-5]),-5)
 def test_full_lock_has_only_assumed_charge(self):
  r=evaluate([[.1,-.1],[-.2,.2]],[100,-50],[1,1],20);np.testing.assert_allclose(r['losses'],[.3,.3])
 def test_unhedged_cash_flow_sign(self):
  r=evaluate([[.1,.1]],[100,-50],[0,0],0);self.assertEqual(r['losses'],[5])
 def test_netting_matches_residual_gross_exposure(self):
  pay,rec=400,300;ret=.08;h=.5;self.assertAlmostEqual((pay-rec)*(1-h)*ret,pay*(1-h)*ret-rec*(1-h)*ret)
 def test_quote_inversion(self):self.assertAlmostEqual((1/90)/(1/100)-1,1/9)
 def test_invalid_coverage(self):
  with self.assertRaises(ValueError):evaluate([[.1]],[100],[1.1])
 def test_fit_feasible_and_beats_feasible_training_baseline(self):
  r=pd.read_csv(ROOT/'outputs/completed_month_returns.csv',index_col=0);train=r[r.index<'2023-01-01'].to_numpy();w=pd.read_csv(ROOT/'outputs/netting_ledger.csv');net=w.net_usd_at_base_spot.to_numpy();h=np.array(fit(train,net));self.assertTrue(((h>=0)&(h<=1)).all());self.assertLessEqual(abs(net)@h,.5*abs(net).sum()+.01);self.assertLessEqual(evaluate(train,net,h)['cvar90'],evaluate(train,net,[.5]*5)['cvar90']+.01)
 def test_split_and_partial_month(self):
  r=pd.read_csv(ROOT/'outputs/policy_monthly_costs.csv');self.assertLess(r[r.split=='train'].month.max(),r[r.split=='holdout'].month.min());self.assertEqual(r[r.split=='holdout'].month.max(),'2026-09-30');self.assertEqual(r[r.split=='holdout'].month.nunique(),45)
 def test_independent_release_values(self):
  r=pd.read_csv(ROOT/'outputs/h10_reconciliation.csv');self.assertEqual(len(r),25);self.assertTrue((r.difference.abs()<1e-8).all())
if __name__=='__main__':unittest.main()
