import unittest,json,csv,gzip,hashlib,math
from collections import defaultdict
from decimal import Decimal as D
import numpy as np
from extract import ROOT,CUTOFF,days
from models import ridge_fit,inventory_scenario,rail_scenario,fixed_asset_return
from audit_filings import numeric_facts
PROJECTS=['semiconductor-inventory-funding','freight-rail-capital-review']
def read(p):
 with p.open() as f:return list(csv.DictReader(f))
class InputContracts(unittest.TestCase):
 def test_pinned_archives_and_originals(self):
  for p in PROJECTS:
   root=ROOT/p
   for m in json.loads((root/'data/source_manifest.json').read_text()):
    b=(root/'data/raw'/f"{m['ticker']}.json.gz").read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),m['sha256_archive']);raw=gzip.decompress(b);self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256_uncompressed']);self.assertEqual(json.loads(raw)['cik'],m['cik'])
   for m in json.loads((root/'data/filing_manifest.json').read_text()):
    b=gzip.decompress((root/'data/raw'/m['file']).read_bytes());self.assertEqual(hashlib.sha256(b).hexdigest(),m['snapshot_sha256']);self.assertLessEqual(m['filed'],CUTOFF);self.assertGreater(len(json.loads(b)),30)
    sub=gzip.decompress((root/'data/raw'/f"{m['ticker']}-submissions.json.gz").read_bytes());self.assertEqual(hashlib.sha256(sub).hexdigest(),m['submissions_sha256'])
 def test_lineage_and_independent_operand_reconciliation(self):
  for p in PROJECTS:
   root=ROOT/p;panel={(r['ticker'],r['end']):r for r in read(root/'outputs/panel.csv')};sums=defaultdict(lambda:D(0));sources={t:json.loads(gzip.decompress((root/'data/raw'/f'{t}.json.gz').read_bytes())) for t in {t for t,e in panel}}
   for r in read(root/'outputs/source_lineage.csv'):
    obj=sources[r['ticker']]
    for part in r['pointer'].split('/')[1:]:obj=obj[int(part)] if isinstance(obj,list) else obj[part]
    self.assertEqual(D(str(obj['val'])),D(r['value_usd']));self.assertEqual(obj['accn'],r['accn']);self.assertEqual(obj['filed'],r['filed']);self.assertLessEqual(r['filed'],panel[r['ticker'],r['record_end']]['filed'])
    sums[(r['ticker'],r['record_end'],r['metric'])]+=D(r['value_usd'])*(-1 if r['operand']=='ytd9_minus' else 1)
   for (t,e,k),v in sums.items():self.assertEqual(v,D(panel[t,e][k]))
 def test_unique_positive_periods_and_visible_exclusions(self):
  for p in PROJECTS:
   root=ROOT/p;rows=read(root/'outputs/panel.csv');self.assertEqual(len(rows),len({(r['ticker'],r['end']) for r in rows}));self.assertTrue(read(root/'outputs/exclusions.csv'));self.assertTrue(read(root/'outputs/later_revision_audit.csv'))
   for r in rows:self.assertLess(r['end'],r['filed']);self.assertLessEqual(r['filed'],CUTOFF);self.assertGreater(float(r['revenue']),0)
 def test_original_filing_reconciliation(self):
  n=0
  for p in PROJECTS:
   rs=read(ROOT/p/'outputs/original_filing_reconciliation.csv');n+=len(rs);self.assertTrue(all(r['status']=='PASS' and int(r['matching_inline_cells'])>0 for r in rs))
  self.assertEqual(n,36)
class IndependentMethods(unittest.TestCase):
 def test_pinned_decision_results(self):
  for p in PROJECTS:
   root=ROOT/p;expected=json.loads((root/'data/expected_results.json').read_text());actual=json.loads((root/'outputs/metrics.json').read_text())
   for k,v in expected.items():
    if isinstance(v,float):self.assertAlmostEqual(v,actual[k],places=9)
    else:self.assertEqual(v,actual[k])

 def test_hand_worked_inventory_scenario_and_bounds(self):
  r=inventory_scenario(100,110,120,10,20);self.assertEqual(r,{'planning_inventory':144,'incremental_balance':44,'quarterly_carry_cost':3.6})
  for a,b in [(-1,0),(41,0),(1,51),(float('nan'),1)]:
   with self.assertRaises(ValueError):inventory_scenario(100,100,100,a,b)
 def test_hand_worked_rail_funding_and_asset_denominator(self):
  r=rail_scenario(100,40,20,30,-20,100);self.assertEqual(r,{'buyback_capacity':20,'distribution_gap':-10,'capex_budget':40})
  self.assertEqual(fixed_asset_return(20,80,120,25),.15)
  self.assertEqual(rail_scenario(30,40,10,20,0,100)['buyback_capacity'],0)
  for a,b in [(-61,100),(21,100),(0,79),(0,151),(float('inf'),100)]:
   with self.assertRaises(ValueError):rail_scenario(100,40,20,30,a,b)
 def test_ridge_against_augmented_svd_solution(self):
  X=np.array([[1,2,3],[1,0,1],[1,2,0],[1,3,2]],float);y=np.array([1,3,2,4.]);lam=10.;augment=np.diag([0,math.sqrt(lam),math.sqrt(lam)])
  b=np.linalg.lstsq(np.vstack([X,augment]),np.r_[y,[0,0,0]],rcond=None)[0];np.testing.assert_allclose(ridge_fit(X,y,lam),b,atol=1e-12)
 def test_information_timing_and_forecast_metrics(self):
  root=ROOT/PROJECTS[0];rs=read(root/'outputs/forecast_diagnostics.csv');test=[r for r in rs if r['split']=='test'];m=json.loads((root/'outputs/metrics.json').read_text())
  for r in rs:self.assertLess(r['latest_training_label_filed'],r['origin_filed']);self.assertLess(r['penalty_known_after'],r['origin_filed']);self.assertLess(r['origin_filed'],r['target_filed']);self.assertLess(r['origin_end'],r['target_end'])
  for key in ['forecast','last_value','seasonal']:
   w=100*math.fsum(abs(float(r['actual'])-float(r[key])) for r in test)/math.fsum(float(r['actual']) for r in test);self.assertAlmostEqual(w,m[key+'_wape_pct'],places=10)
  calibrated=[r for r in test if r['lower90']];cov=100*sum(float(r['lower90'])<=float(r['actual'])<=float(r['upper90']) for r in calibrated)/len(calibrated);self.assertEqual(cov,m['coverage90_pct']);self.assertFalse(m['model_promotion_pass'])
 def test_all_forecasts_against_independent_svd(self):
  # Reconstruct features independently from published disclosure panel; no model helpers.
  root=ROOT/PROJECTS[0];panel=read(root/'outputs/panel.csv');samples=[]
  for t in sorted({r['ticker'] for r in panel}):
   rs=sorted([r for r in panel if r['ticker']==t],key=lambda r:r['end'])
   for i in range(4,len(rs)-1):
    seq=rs[i-4:i+2]
    if not all(75<=days(a['end'],b['end'])<=105 for a,b in zip(seq,seq[1:])):continue
    a,b,c,z=rs[i],rs[i-1],rs[i-4],rs[i+1];iv=lambda r:float(r['inventory']);cost=lambda r:float(r['cost']);angle=2*math.pi*(int(a['end'][5:7])-1)/12
    x=[1,math.log(iv(a)/iv(b)),math.log(cost(a)/cost(b)),math.log(iv(a)/iv(c)),math.sin(angle),math.cos(angle)]
    samples.append({'ticker':t,'origin':a,'target':z,'x':x,'y':math.log(iv(z)/iv(a))})
  m=json.loads((root/'outputs/metrics.json').read_text());P=np.diag([0]+[math.sqrt(m['selected_penalty'])]*5)
  for r in read(root/'outputs/forecast_diagnostics.csv'):
   s=next(s for s in samples if s['ticker']==r['ticker'] and s['origin']['end']==r['origin_end']);train=[z for z in samples if z['target']['filed']<r['origin_filed'] and z['target']['end']<r['origin_end']];self.assertEqual(len(train),int(r['training_n']))
   b=np.linalg.lstsq(np.vstack([[z['x'] for z in train],P]),np.r_[[z['y'] for z in train],[0]*6],rcond=None)[0];expected=float(s['origin']['inventory'])*math.exp(np.dot(s['x'],b));self.assertAlmostEqual(float(r['forecast'])/expected,1.,places=12)
 def test_rail_all_scenarios_and_common_year(self):
  root=ROOT/PROJECTS[1];latest={r['ticker']:r for r in read(root/'outputs/latest_decisions.csv')};self.assertEqual({r['end'] for r in latest.values()},{'2025-12-31'})
  for r in read(root/'outputs/cash_scenarios.csv'):
   a=latest[r['ticker']];cfo=D(a['cfo'])*(1+D(r['cfo_shock_pct'])/100);capex=D(a['capex'])*D(r['capex_pct'])/100;gap=cfo-capex-D(a['dividends'])-D(a['buybacks']);self.assertEqual(gap,D(r['distribution_gap']));self.assertEqual(max(D(0),gap+D(a['buybacks'])),D(r['buyback_capacity']))
  for r in read(root/'outputs/capital_history.csv'):
   if r['ticker']=='UNP' and r['end']=='2024-12-31':self.assertEqual(r['net_asset_return21'],'')
 def test_sql_independent_aggregation(self):
  for p in PROJECTS:
   root=ROOT/p;panel=read(root/'outputs/panel.csv');sql=read(root/'outputs/sql_summary.csv')
   for r in sql:
    rs=[z for z in panel if z['ticker']==r['ticker']];self.assertEqual(len(rs),int(r['records']))
    if p.startswith('semi'):self.assertEqual(sum(D(z['inventory']) for z in rs),D(r['balance_sum_for_reconciliation']))
    else:self.assertEqual(sum(D(z['cfo'])-D(z['capex'])-D(z['dividends'])-D(z['buybacks']) for z in rs),D(r['residual']))
if __name__=='__main__':unittest.main(verbosity=2)
