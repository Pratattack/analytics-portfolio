import unittest
from pipeline import bridge, contract_npv
class Tests(unittest.TestCase):
    def test_hand_bridge(self):
        a=[dict(quantity=10,price=100,unit_cost=60)]
        b=[dict(quantity=12,price=110,unit_cost=65)]
        self.assertEqual(bridge(a,b),dict(volume=80,mix=0,price=120,cost=-60))
    def test_mix(self):
        a=[dict(quantity=10,price=100,unit_cost=60),dict(quantity=10,price=100,unit_cost=80)]
        b=[dict(quantity=15,price=100,unit_cost=60),dict(quantity=5,price=100,unit_cost=80)]
        self.assertEqual(bridge(a,b),dict(volume=0,mix=100,price=0,cost=0))
    def test_zero_churn_and_full_churn(self):
        self.assertAlmostEqual(contract_npv(10,100,60,0,-1,0,0,0),1200)
        self.assertEqual(contract_npv(10,100,60,.05,-1,1,0),0)
    def test_invalid(self):
        with self.assertRaises(ValueError): contract_npv(10,100,60,0,-1,1.1,0)
if __name__=='__main__': unittest.main()
