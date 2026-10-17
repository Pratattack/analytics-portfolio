import unittest
from pipeline import npv, experiment
class Tests(unittest.TestCase):
    def test_hand_npv(self):
        self.assertAlmostEqual(npv(1000,1000,.20,.10,.5,100,1,.05,0,1),-42)
    def test_pd_sensitivity(self):
        self.assertLess(npv(1000,1000,.2,.2,.5,100),npv(1000,1000,.2,.1,.5,100))
    def test_cac(self):
        self.assertAlmostEqual(npv(1000,1000,.2,.1,.5,170)-npv(1000,1000,.2,.1,.5,100),-70)
    def test_experiment(self):
        r=[dict(arm=a,converted=v) for a in [0,1] for v in [0,1,0,1]]
        e=experiment(r); self.assertEqual(e['absolute_lift'],0); self.assertLess(e['ci_low'],0)
    def test_invalid(self):
        with self.assertRaises(ValueError): npv(1000,1000,.2,1.1,.5,100)
if __name__=='__main__': unittest.main()
