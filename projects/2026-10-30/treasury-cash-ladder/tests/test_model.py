import unittest,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import solve
class ModelTests(unittest.TestCase):
 def test_zero_quotes(self):
  r=solve([0,0,0]);self.assertAlmostEqual(r['incremental_interest'],0)
 def test_conservation(self):
  r=solve([3.91,4.02,4]);self.assertAlmostEqual(sum(r['allocations']),1e6);self.assertGreaterEqual(min(r['balances']),1e5-1e-6)
 def test_infeasible_early_cash(self):
  self.assertFalse(solve([4,4,4],shock=1e6)['feasible'])
 def test_fee_cannot_improve(self):
  self.assertLessEqual(solve([4,4,4],fee=10)['incremental_interest'],solve([4,4,4])['incremental_interest']+1e-6)
 def test_reserve_cannot_improve(self):
  self.assertLessEqual(solve([4,4,4],reserve=2e5)['incremental_interest'],solve([4,4,4])['incremental_interest']+1e-6)
 def test_price_convention(self):
  r=solve([4,4,4]);self.assertAlmostEqual(r['factors'][0],1/(1-.04*28/360))
 def test_all_cash_when_fee_exceeds_return(self):
  r=solve([.1,.1,.1],fee=100);self.assertAlmostEqual(r['allocations'][3],1e6);self.assertAlmostEqual(r['incremental_interest'],0)
 def test_ledger_independent(self):
  r=solve([3,5,4]);x=r['allocations'];cash=x[3]-50000;self.assertAlmostEqual(cash,r['balances'][0]);
  for i,payment in enumerate([200000,250000,200000]):
   cash+=x[i]*r['factors'][i]-payment;self.assertAlmostEqual(cash,r['balances'][i+1])
 def test_invalid(self):
  with self.assertRaises(ValueError):solve([4,4,4],capital=-1)
if __name__=='__main__':unittest.main()
