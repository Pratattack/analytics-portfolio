import copy,csv,unittest
from pathlib import Path
from model import features,fit,predict,quantile,decision_cost,solve_linear
ROOT=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/'data/day.csv').open() as f:cls.rows=list(csv.DictReader(f))
    def test_linear_solver(self):
        b=solve_linear([[2,1],[1,3]],[5,5]);self.assertAlmostEqual(b[0],2);self.assertAlmostEqual(b[1],1)
    def test_singular_system(self):
        with self.assertRaises(ValueError):solve_linear([[1,1],[2,2]],[1,2])
    def test_quantile(self):
        self.assertEqual(quantile([1,2,3,4],.5),2);self.assertEqual(quantile([1,2,3,4],.8,True),4)
    def test_cost_hand_example(self):
        self.assertEqual(decision_cost(10,8,4,.75),8);self.assertEqual(decision_cost(10,12,4,.75),1.5)
    def test_no_target_or_weather_leakage(self):
        rows=copy.deepcopy(self.rows);before=features(rows,100)
        for k in ['cnt','casual','registered','temp','atemp','hum','windspeed','weathersit']:rows[100][k]='999999'
        self.assertEqual(before,features(rows,100))
    def test_lags(self):
        f=features(self.rows,100);self.assertEqual(f[-4],float(self.rows[99]['cnt']));self.assertEqual(f[-3],float(self.rows[93]['cnt']))
    def test_fit_excludes_future(self):
        rows=copy.deepcopy(self.rows);before=fit(rows,80,10)
        for r in rows[80:]:r['cnt']='999999'
        self.assertEqual(before,fit(rows,80,10))
    def test_training_guard(self):
        f=fit(self.rows,80,10)
        with self.assertRaises(ValueError):predict(f,self.rows,79)
    def test_nonnegative_forecast(self):
        self.assertGreaterEqual(predict(fit(self.rows,80,10),self.rows,80),0)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):features(self.rows,1)
        with self.assertRaises(ValueError):decision_cost(1,-1,1,1)
if __name__=='__main__':unittest.main()
