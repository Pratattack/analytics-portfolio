import copy
import math
import unittest
import numpy as np
from scipy.optimize import linprog
from finance_models import cash_path, required_rollover, chain_ladder
from insurance_pipeline import triangle_inventory, complete_triangle
from reit_pipeline import records
from sec_sources import numeric, inline_facts


def fixture_triangle():
    # Hand-designed cumulative multipliers 2, 1.5, 1.2, 1.1.
    multipliers=[1,2,3,3.6,3.96]
    return {(ay,ay+age):100*(ay-2015+1)*multipliers[age] for ay in range(2015,2020) for age in range(2020-ay)}


class SourceContracts(unittest.TestCase):
    def test_sign_scale_and_zero(self):
        self.assertEqual(numeric('1,250',6,'-'),-1250000000)
        self.assertEqual(numeric('(125)',3),-125000)
        self.assertEqual(numeric('—',6),0)
        for text in ['', 'NaN', 'unexpected']:
            with self.assertRaises(ValueError):numeric(text)
    def test_context_dimensions_and_nil(self):
        value=inline_facts(b'<html><xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit><xbrli:context id="c"><xbrli:entity><xbrli:identifier>1</xbrli:identifier><xbrli:segment><xbrldi:explicitmember dimension="dei:LegalEntityAxis">demo:ParentMember</xbrldi:explicitmember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2025-12-31</xbrli:instant></xbrli:period></xbrli:context><ix:nonfraction id="a" name="us-gaap:Cash" contextref="c" unitref="USD" scale="3" sign="-">12</ix:nonfraction><ix:nonfraction id="b" name="us-gaap:Cash" contextref="c" unitref="USD" xsi:nil="true">-</ix:nonfraction></html>')
        self.assertEqual(len(value['facts']),1)
        self.assertEqual(value['facts'][0]['value'],-12000)
        self.assertEqual(value['facts'][0]['unit_measure'],'iso4217:USD')
        self.assertEqual(value['facts'][0]['dimensions'],{'dei:LegalEntityAxis':'demo:ParentMember'})
        self.assertEqual(len(value['rejected_numeric']),1)


class LossDevelopment(unittest.TestCase):
    def test_hand_factors_and_ultimate(self):
        result=chain_ladder(fixture_triangle(),2019)
        for actual,expected in zip(result['factors'].values(),[2,1.5,1.2,1.1]):self.assertAlmostEqual(actual,expected)
        self.assertAlmostEqual(result['ultimate'],100*3.96*sum(range(1,6)))
        latest=sum(value for (ay,vy),value in fixture_triangle().items() if vy==2019)
        self.assertAlmostEqual(result['unpaid'],5940-latest)
    def test_tail_applies_to_ultimate_not_reserve(self):
        base=chain_ladder(fixture_triangle(),2019);tail=chain_ladder(fixture_triangle(),2019,tail=1.1)
        self.assertAlmostEqual(tail['unpaid']-base['unpaid'],base['ultimate']*.1)
    def test_future_cells_do_not_change_masked_fit(self):
        data=fixture_triangle();original=chain_ladder(data,2019)
        data[(2019,2020)]=1e12
        self.assertEqual(original,chain_ladder(data,2019))
    def test_invalid_assumptions_and_decreasing_paid(self):
        data=fixture_triangle();data[(2015,2016)]=50
        with self.assertRaises(ValueError):chain_ladder(data,2019)
        with self.assertRaises(ValueError):chain_ladder(fixture_triangle(),2019,tail=.99)
    def test_incomplete_triangle_fails_gate(self):
        data=fixture_triangle();del data[(2017,2018)]
        with self.assertRaises(ValueError):complete_triangle(data,2019)
    def test_all_accepted_factors_independent_numpy(self):
        groups,cells,_,_=triangle_inventory();checked=0
        for gid,group in groups.items():
            if group['aggregate']:continue
            data={(ay,vy):v for (g,ay,vy,metric),v in cells.items() if g==gid and metric=='paid'}
            try:complete_triangle(data,2025);fit=chain_ladder(data,2025)
            except ValueError:continue
            for age,actual in fit['factors'].items():
                pairs=np.array([(v,data[(ay,vy+1)]) for (ay,vy),v in data.items() if vy-ay==age and (ay,vy+1) in data and v>0])
                independent=np.sum(pairs[:,1])/np.sum(pairs[:,0]);self.assertAlmostEqual(actual,independent)
            for row in fit['estimates']:
                f=[fit['factors'][age] for age in sorted(fit['factors']) if age>=row['valuation_year']-row['accident_year']]
                independent=row['latest_paid']*float(np.prod(np.array(f)))
                self.assertTrue(math.isclose(independent,row['ultimate'],rel_tol=1e-12))
            checked+=1
        self.assertGreaterEqual(checked,25)


class Refinancing(unittest.TestCase):
    def setUp(self):self.row=dict(cfo=100,distributions=20,cash=10,maturities=[100,100,100,100,100])
    def test_hand_cash_no_interest(self):
        rows=cash_path(self.row,rollover=0,maintenance_share=0,issuance_fee=0,cash_floor_share=0)
        self.assertEqual([r['closing_cash'] for r in rows],[-10,-30,-50,-70,-90])
        solution=required_rollover(self.row,maintenance_share=0,issuance_fee=0,cash_floor_share=0)
        self.assertAlmostEqual(solution['minimum_rollover'],.18)
    def test_half_year_new_interest(self):
        rows=cash_path(self.row,rollover=1,spread_bps=200,maintenance_share=0,issuance_fee=0,cash_floor_share=0)
        self.assertEqual([r['incremental_interest'] for r in rows],[1,3,5,7,9])
        self.assertEqual(rows[-1]['closing_cash'],385)
    def test_recovery_changes_levels_not_compounding(self):
        rows=cash_path(self.row,rollover=1,cfo_decline=.2,recovery_after=2,maintenance_share=0,issuance_fee=0,cash_floor_share=0)
        self.assertEqual([r['closing_cash'] for r in rows],[70,130,210,290,370])
    def test_infeasible_is_not_clamped_to_success(self):
        row={**self.row,'distributions':200}
        solution=required_rollover(row)
        self.assertFalse(solution['feasible']);self.assertIsNone(solution['minimum_rollover']);self.assertGreater(solution['required_liquidity'],0)
    def test_invalid_inputs(self):
        for bad in [dict(rollover=1.1),dict(cfo_decline=float('nan')),dict(spread_bps=-1),dict(recovery_after=2.5)]:
            with self.assertRaises(ValueError):cash_path(self.row,**bad)
    def test_analytic_solution_against_independent_linear_program(self):
        inputs,_,_,_,_,_=records();checked=0
        for row in inputs:
            for decline in [0,.1,.2,.3,.4]:
                for spread in [0,200,400]:
                    for duration in [2,5]:
                        A=[];B=[];cumulative=0
                        # Direct closed-form coefficients, independent of sequential production cash_path.
                        for t in range(1,6):
                            cumulative+=row['maturities'][t-1]
                            constant=row['cash']+t*(.9*row['cfo']-row['distributions'])-min(t,duration)*row['cfo']*decline-cumulative
                            interest=sum(row['maturities'][j]*(t-j-.5) for j in range(t))*spread/10000
                            slope=.99*cumulative-interest
                            A.append([-slope/1e9]);B.append((constant-.1*row['cfo'])/1e9)
                        independent=linprog([1],A_ub=A,b_ub=B,bounds=[(0,1)],method='highs')
                        actual=required_rollover(row,cfo_decline=decline,spread_bps=spread,recovery_after=duration)
                        self.assertEqual(actual['feasible'],independent.success,(row['ticker'],decline,spread,duration))
                        if independent.success:self.assertAlmostEqual(actual['minimum_rollover'],independent.x[0],places=7)
                        checked+=1
        self.assertEqual(checked,180)


if __name__=='__main__':unittest.main()
