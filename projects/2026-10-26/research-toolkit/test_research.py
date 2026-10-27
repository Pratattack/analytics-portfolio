"""Independent economic, source-scope and numerical checks."""
import unittest,json,csv,gzip,itertools,math,sqlite3
import numpy as np
from scipy.special import expit
from common import ROOT,CREDIT,REST,digest,readcsv
import credit,restaurant
class CreditTests(unittest.TestCase):
 def test_source_projection_and_calendar(self):
  p=ROOT/CREDIT/'data';m=json.loads((p/'manifest.json').read_text());self.assertEqual(digest(p/m['raw_file']),m['raw_sha256']);raw=readcsv((p/m['raw_file']));expected=[r for r in raw if '1960-01-01'<=r['observation_date']<='2024-12-31'];actual=readcsv((p/'monthly.csv'));self.assertEqual(expected,actual)
  dates=[r['observation_date'] for r in actual];index=[int(d[:4])*12+int(d[5:7]) for d in dates];self.assertTrue(all(b-a==1 for a,b in zip(index,index[1:])))
 def test_target_independent_and_label_embargo(self):
  panel=credit.make_panel();raw=readcsv((ROOT/CREDIT/'data/monthly.csv'));lookup={x['observation_date']:i for i,x in enumerate(raw)}
  for r in panel:
   i=lookup[r['date']];self.assertEqual(r['y'],max(int(float(x['USREC'])) for x in raw[i+1:i+13]));self.assertLess(r['feature_month'],r['date'])
  for r in readcsv(ROOT/CREDIT/'outputs/test_predictions.csv'):self.assertLessEqual(r['last_training_label'],r['date']);self.assertLess(r['last_training_origin'],r['date'])
 def test_objective_gradient_finite_difference(self):
  X=np.array([[1,-1.,2],[1,0,1],[1,2,-1.]]);y=np.array([0,1,1]);b=np.array([.2,-.1,.3]);val,g=credit.objective(b,X,y,1.3);fd=[]
  for i in range(3):
   d=np.zeros(3);d[i]=1e-6;fd.append((credit.objective(b+d,X,y,1.3)[0]-credit.objective(b-d,X,y,1.3)[0])/2e-6)
  np.testing.assert_allclose(fd,g,rtol=1e-6,atol=1e-7)
 def test_rank_metric_ties_and_score_hand_case(self):
  y=np.array([0,1,0,1]);p=np.array([.1,.8,.2,.8]);self.assertEqual(credit.auc(y,p),1);self.assertEqual(credit.auc(y,np.ones(4)),.5);self.assertAlmostEqual(credit.metrics(y,p)['brier'],(.01+.04+.04+.04)/4)
 def test_independent_test_sql_and_threshold(self):
  p=ROOT/CREDIT/'outputs';r=readcsv((p/'test_predictions.csv'));m=json.loads((p/'metrics.json').read_text());db=sqlite3.connect(':memory:');db.execute('CREATE TABLE f(y,p,q,u)');db.executemany('INSERT INTO f VALUES(?,?,?,?)',[(int(x['y']),float(x['candidate_probability']),float(x['curve_probability']),float(x['unconditional'])) for x in r]);x=db.execute('SELECT avg((p-y)*(p-y)),avg((q-y)*(q-y)),avg((u-y)*(u-y)) FROM f').fetchone()
  np.testing.assert_allclose(x,[m[k]['brier'] for k in ['candidate','curve_baseline','expanding_unconditional']],rtol=1e-12)
  self.assertEqual(m['candidate']['tp']+m['candidate']['fn'],m['candidate']['positive_months']);self.assertFalse(m['promotion_gate']);self.assertEqual(len(r),192)
 def test_block_mean_fixture_and_input_perturbation(self):
  np.testing.assert_allclose(credit.block_interval(np.ones(30)*.1),[.1,.1],atol=1e-14);X=np.array([[-2.],[-1.],[1.],[2.]]);y=np.array([0,0,1,1]);self.assertGreater(credit.fit_predict(X,y,np.array([1.]),1),.5)
class RestaurantTests(unittest.TestCase):
 def test_original_context_audit(self):
  p=ROOT/REST/'data';audit=json.loads((p/'original_audit.json').read_text());self.assertEqual(len(audit),24)
  for r in audit:
   a=json.loads((p/(r['ticker']+'-filing.json')).read_text());h=[x for x in a if x['context']==r['context'] and x['element_index']==r['element_index'] and x['tag']=='us-gaap:'+r['tag']];self.assertEqual(len(h),1);self.assertFalse(h[0]['dimensions']);self.assertEqual(h[0]['unit'],'iso4217:USD');self.assertAlmostEqual(h[0]['value'],r['value'],delta=1.)
 def test_lineage_same_accession_and_positive_scope(self):
  p=ROOT/REST/'data';a=json.loads((p/'panel.json').read_text());f=json.loads((p/'lineage.json').read_text());self.assertEqual(len(a),32)
  for r in a:
   for k in ['revenue','ebit','lease_cost','lease_cash']:
    hits=[x for x in f if x['ticker']==r['ticker'] and x['field']==k and x['start']==r['start'] and x['end']==r['end'] and x['accn']==r['accn']];self.assertEqual(len(hits),1);self.assertEqual(hits[0]['val'],r[k]);self.assertLessEqual(r['filed'],'2026-10-26')
 def test_hand_case_no_rent_double_count(self):
  r=restaurant.response(1000,100,50,.1,.5,.1,.03);self.assertEqual(r['stressed_ebit'],45);self.assertEqual(r['gap_to_floor'],0);self.assertTrue(r['feasible']);self.assertEqual(r['assumed_response_resource'],0)
  r=restaurant.response(1000,50,50,.2,.5,0,0);self.assertEqual(r['gap_to_floor'],50);self.assertTrue(r['feasible']);self.assertAlmostEqual(r['cost_savings'],0);self.assertAlmostEqual(r['recovered_sales'],100);self.assertAlmostEqual(r['assumed_response_resource'],15)
 def test_every_published_scenario_vs_independent_lp(self):
  p=ROOT/REST/'outputs';latest={r['ticker']:r for r in json.loads((ROOT/REST/'data/panel.json').read_text())} # ascending source rows; latest overwritten
  rows=readcsv((p/'scenario_frontier.csv'));self.assertEqual(len(rows),216)
  for r in rows:
   base=latest[r['ticker']];s,m,e,f=[float(r[k]) for k in ['shock','contribution_margin','lease_escalation','ebit_floor']];q=restaurant.independent_lp(base,s,m,e,f);self.assertEqual(q.success,r['feasible']=='True')
   if q.success:self.assertAlmostEqual(q.fun,float(r['assumed_response_resource']),delta=max(.02,abs(q.fun)*1e-8))
 def test_boundary_vertex_enumeration(self):
  # Independent 2D LP vertices: rectangle corners and gap-line intersections.
  for E,s,m in itertools.product([-50,0,50],[0,.1,.4],[.2,.5,.8]):
   r=restaurant.response(1000,E,30,s,m,.1,.03);gap=max(0,30-E+1000*s*m+3);xc=20;yc=s*500;candidates=[]
   for x,y in [(0,0),(xc,0),(0,yc),(xc,yc),(gap,0),(0,gap/m),(xc,(gap-xc)/m),(gap-m*yc,yc)]:
    if -1e-9<=x<=xc+1e-9 and -1e-9<=y<=yc+1e-9 and x+m*y>=gap-1e-9:candidates.append(.5*x+.15*y)
   self.assertEqual(bool(candidates),r['feasible'])
   if candidates:self.assertAlmostEqual(min(candidates),r['assumed_response_resource'])
 def test_invalid_scenarios_and_infeasible(self):
  for v in [float('nan'),-.1,1.1]:
   with self.assertRaises(ValueError):restaurant.response(1000,20,30,v,.3,.1,.03)
  self.assertFalse(restaurant.response(1000,-100,50,.8,1,1,.3)['feasible'])
if __name__=='__main__':unittest.main(verbosity=2)
