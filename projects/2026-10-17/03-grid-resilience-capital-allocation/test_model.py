import copy, json, unittest
from pathlib import Path
from model import build_options, independent_equal_weight_dp, intervention_value, solve, validate

ROOT=Path(__file__).resolve().parent

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'config.json').read_text())

    def test_hand_calculated_social_value(self):
        c=dict(discount_rate=0.,life_years=2,value_per_customer_hour_usd=10)
        d=dict(customers=600,cost_factor=1)
        p=dict(normal_reduction=.5,event_reduction=.25,annual_opex_musd=.01,capex_musd=.1)
        s=dict(year=2024,normal_factor=1,event_factor=1,efficacy=1,capex_factor=1,delay_years=0)
        b=dict(normal_2024=60,all_2024=180)
        r=intervention_value(d,p,s,b,c)
        # (60*.5 + 120*.25)*600/60 = 600 avoided customer-hours.
        self.assertEqual(r['annual_customer_hours_avoided'],600)
        self.assertAlmostEqual(r['npv_musd'],-.108)

    def test_delay_and_cost_shock(self):
        c=dict(discount_rate=0.,life_years=2,value_per_customer_hour_usd=10)
        r=intervention_value(dict(customers=600,cost_factor=1),dict(normal_reduction=.5,event_reduction=.25,annual_opex_musd=.01,capex_musd=.1),dict(year=2024,normal_factor=1,event_factor=1,efficacy=1,capex_factor=1.2,delay_years=1),dict(normal_2024=60,all_2024=180),c)
        self.assertAlmostEqual(r['npv_musd'],-.124)

    def toy(self):
        def p(name,cost,values):return dict(state=name,intervention=name,reserve_musd=cost,crew=0,critical=0,values=values)
        return [[p('none',0,[0,0]),p('skew',2,[8,0]),p('balanced',2,[3,3])],[p('none',0,[0,0]),p('other-skew',2,[0,8]),p('small',1,[2,2])]]

    def test_known_robust_optimum(self):
        c=dict(budget_musd=3,crew_limit=10,minimum_critical_districts=0)
        r=solve(self.toy(),c)
        self.assertEqual(r['score'],5);self.assertEqual(r['enumerated'],9)

    def test_equal_weight_oracle(self):
        c=dict(budget_musd=3,crew_limit=10,minimum_critical_districts=0)
        self.assertEqual(solve(self.toy(),c,objective='equal_weight')['score'],6)
        self.assertEqual(independent_equal_weight_dp(self.toy(),c),6)

    def test_zero_budget(self):
        r=solve(self.toy(),dict(budget_musd=0,crew_limit=0,minimum_critical_districts=0))
        self.assertEqual(r['score'],0)

    def test_infeasible_critical_floor(self):
        with self.assertRaises(ValueError):solve(self.toy(),dict(budget_musd=0,crew_limit=0,minimum_critical_districts=1))

    def test_unknown_objective(self):
        with self.assertRaises(ValueError):solve(self.toy(),dict(budget_musd=3,crew_limit=0,minimum_critical_districts=0),objective='forecast')

    def test_no_double_purchase(self):
        c=dict(budget_musd=100,crew_limit=10,minimum_critical_districts=0)
        r=solve(self.toy(),c)
        self.assertEqual(len(r['plan']),2)
        self.assertEqual(r['score'],8)

    def test_invalid_assumptions(self):
        for field,val in [('budget_musd',-1),('discount_rate',-.1),('budget_reserve_factor',.9)]:
            c=copy.deepcopy(self.config);c[field]=val
            with self.assertRaises(ValueError):validate(c)

    def test_efficacy_bounds(self):
        c=copy.deepcopy(self.config);c['interventions'][0]['event_reduction']=1.1
        with self.assertRaises(ValueError):validate(c)

    def test_reserve_guards_modeled_cost(self):
        c=copy.deepcopy(self.config);c['scenarios'][0]['capex_factor']=1.3
        with self.assertRaises(ValueError):validate(c)

    def test_monotonic_budget_toy(self):
        scores=[solve(self.toy(),dict(budget_musd=b,crew_limit=10,minimum_critical_districts=0))['score'] for b in range(5)]
        self.assertEqual(scores,sorted(scores))

if __name__=='__main__':unittest.main()
