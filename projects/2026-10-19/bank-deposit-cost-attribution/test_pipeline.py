import csv,json,unittest,math
from collections import defaultdict
import pipeline as p
import io,gzip
def read_csv(path):return csv.DictReader(io.StringIO(gzip.decompress(path.read_bytes()).decode() if path.suffix==".gz" else path.read_text(encoding="utf-8-sig")))

class Accounting(unittest.TestCase):
    def test_constant_mix_rate_baseline_reconciliation(self):
        panel={(int(r['cert']),r['report_date']):r for r in read_csv(p.BASE/'outputs/source_audited_quarterly_panel.csv.gz')}
        total=0
        for row in read_csv(p.BASE/'outputs/bank_cost_bridge.csv'):
            before=panel[(int(row['cert']),'20250630')]
            after=panel[(int(row['cert']),'20260630')]
            baseline=float(before['edepdomq'])*float(after['average_domestic_deposits'])/float(before['average_domestic_deposits'])
            self.assertAlmostEqual(baseline,float(row['constant_mix_rate_baseline_expense_thousand_usd']),delta=1e-6)
            total+=baseline
        metrics=json.loads((p.BASE/'outputs/metrics.json').read_text())
        self.assertAlmostEqual(total,metrics['constant_mix_rate_baseline_expense_thousand_usd'],delta=1e-5)
        self.assertAlmostEqual(metrics['comparison_expense_thousand_usd']-total,metrics['baseline_gap_thousand_usd'],delta=1e-5)
    def test_constant_factors_and_single_rate_change(self):
        self.assertEqual(p.shapley([100,.5,.04],[100,.5,.04]),[0,0,0])
        r=p.shapley([100,.5,.04],[100,.5,.08]);self.assertEqual(r[:2],[0,0]);self.assertAlmostEqual(r[2],.5)
    def test_interactions_hand_symmetry(self):
        r=p.shapley([4,.5,1],[8,1,2])
        for v in r:self.assertAlmostEqual(v,7/6)
        self.assertAlmostEqual(sum(r),3.5)
    def test_retention_hand_case_and_break_even(self):
        # $1m target: retained savings 900k*.005=$4500; replacement premium 100k*.02=$2000.
        r=p.retention(1e6,.02,.005,1,.1,.04,500);self.assertAlmostEqual(r['modeled_annual_net_usd'],2000)
        threshold=r['break_even_attrition'];self.assertAlmostEqual(threshold,.18)
        self.assertAlmostEqual(p.retention(1e6,.02,.005,1,threshold,.04,500)['modeled_annual_net_usd'],0)
        with self.assertRaises(AssertionError):p.retention(1,.02,.03,1,0,.04,0)
    def test_quarter_boundaries(self):
        self.assertEqual(p.previous('20260331'),'20251231');self.assertEqual(p.previous('20260630'),'20260331')
    def test_full_source_pointer_and_proxy_reconciliation(self):
        raw={f.name:json.loads(gzip.decompress(f.read_bytes())) for f in (p.BASE/'data/raw').glob('*.json.gz')}
        lookup={(int(x['data']['CERT']),f[:8]):x['data'] for f,j in raw.items() for x in j['data']}
        rows=list(read_csv(p.BASE/'outputs/source_audited_quarterly_panel.csv.gz'))
        for r in rows:
            source=raw[r['source_file']]['data'][int(r['source_pointer'].split('/')[2])]['data']
            self.assertEqual(int(r['cert']),source['CERT']);self.assertEqual(r['report_date'],source['REPDTE']);self.assertEqual(source['INSAGNT1'],'DIF');self.assertNotEqual(source['BKCLASS'],'OI')
            for field in p.FIELDS:self.assertEqual(float(r[field.lower()]),source[field])
            prior=lookup[(int(r['cert']),r['previous_date'])]
            d=(source['DEPDOM']+prior['DEPDOM'])/2;b=(source['DEPDOM']-source['DEPNIDOM']+prior['DEPDOM']-prior['DEPNIDOM'])/2
            self.assertAlmostEqual(float(r['average_domestic_deposits']),d);self.assertAlmostEqual(float(r['average_interest_bearing_deposits']),b)
            self.assertAlmostEqual(float(r['annualized_proxy_rate']),4*source['EDEPDOMQ']/b)
        for r in read_csv(p.BASE/'outputs/industry_totals.csv'):
            data=[x['data'] for x in raw[r['report_date']+'.json.gz']['data']]
            self.assertEqual(int(r['institutions']),len(data));self.assertEqual(float(r['total_deposits_thousand_usd']),sum(x['DEP'] for x in data))
    def test_all_bridges_independent_closed_form(self):
        panel={(int(r['cert']),r['report_date']):r for r in read_csv(p.BASE/'outputs/source_audited_quarterly_panel.csv.gz')}
        totals=[0.,0.,0.]
        for r in read_csv(p.BASE/'outputs/bank_cost_bridge.csv'):
            a=panel[(int(r['cert']),'20250630')];b=panel[(int(r['cert']),'20260630')]
            x0=[float(a[k]) for k in ['average_domestic_deposits','interest_bearing_share','annualized_proxy_rate']];x1=[float(b[k]) for k in ['average_domestic_deposits','interest_bearing_share','annualized_proxy_rate']];dx=[y-x for x,y in zip(x0,x1)]
            # Analytic Shapley of a trilinear product: main effect + half two-way interactions + third three-way interaction.
            for i,field in enumerate(['volume_contribution_thousand_usd','mix_contribution_thousand_usd','proxy_rate_contribution_thousand_usd']):
                j,k=[q for q in range(3) if q!=i]
                closed=dx[i]*(x0[j]*x0[k]+.5*(dx[j]*x0[k]+x0[j]*dx[k])+dx[j]*dx[k]/3)/4
                self.assertAlmostEqual(closed,float(r[field]),delta=1e-5);totals[i]+=closed
            self.assertAlmostEqual(float(r['change_thousand_usd']),float(b['edepdomq'])-float(a['edepdomq']))
            self.assertLessEqual(abs(float(r['deposit_growth'])),.3);self.assertLessEqual(abs(float(r['quarter_deposit_growth'])),.3)
        summary=json.loads((p.BASE/'outputs/metrics.json').read_text());self.assertAlmostEqual(sum(totals),summary['change_thousand_usd'],delta=1e-4)
    def test_ytd_flags_and_cohort_partition(self):
        cfg=json.loads((p.BASE/'config.json').read_text());source,lookup,issues=p.load(cfg)
        for r in source:
            prior=lookup.get((r['cert'],r['previous_date']))
            expected=r['edepdom'] if r['report_date'].endswith('0331') else r['edepdom']-prior['edepdom'] if prior else None
            if expected is not None and abs(expected-r['edepdomq'])>1:self.assertEqual(r['accepted'],0)
        latest={r['cert'] for r in source if r['report_date']=='20260630'}
        kept={int(r['cert']) for r in read_csv(p.BASE/'outputs/bank_cost_bridge.csv')};excluded={int(r['cert']) for r in read_csv(p.BASE/'outputs/cohort_exclusions.csv')}
        self.assertFalse(kept&excluded);self.assertEqual(kept|excluded,latest);self.assertEqual(len(latest),4238)
    def test_scenario_grid_reconciles_and_has_downside(self):
        rows=list(read_csv(p.BASE/'outputs/retention_scenarios.csv'))
        self.assertTrue(any(float(r['modeled_annual_net_usd'])<0 for r in rows))
        for r in rows:self.assertAlmostEqual(float(r['annual_retained_balance_savings_usd'])-float(r['annual_replacement_increment_usd'])-float(r['assumed_annual_fixed_cost_usd']),float(r['modeled_annual_net_usd']))

if __name__=='__main__':unittest.main()
