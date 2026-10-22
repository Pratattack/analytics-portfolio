import unittest,math,json,csv,gzip,sqlite3,itertools
from decimal import Decimal
from config import ROOT,LAND,HOTEL
from models import land_option,recovery
from extract import select

class HandWorked(unittest.TestCase):
 def test_sunk_deposit(self):
  a=land_option(100,20,.9);b=land_option(100,80,.9)
  self.assertEqual(a['exercise_now'],-10);self.assertEqual(a['best_now'],0);self.assertEqual(a['exercise_now'],b['exercise_now']);self.assertEqual(a['exercise_threshold_ratio'],1)
 def test_wait_enumerated(self):
  z=land_option(100,20,1.1,up=1.2,down=.8,p=.5,rate=.1,extension=.02)
  self.assertAlmostEqual(z['wait'],16/1.1-2);self.assertAlmostEqual(z['best_now'],10)
 def test_refund_opportunity(self):
  z=land_option(100,20,1.1,refund=1)
  self.assertEqual(z['best_now'],20);self.assertEqual(z['exercise_threshold_ratio'],1.2)
 def test_recovery_hand_case(self):
  z=recovery(1000,600,620,100,.1,0,0,.15)
  self.assertEqual(z['net_revenue'],400);self.assertEqual(z['profit_ex_recovery'],120);self.assertAlmostEqual(z['scenario_op_income'],38);self.assertAlmostEqual(z['required_recovery_growth'],22/600)
 def test_invalid(self):
  for x in [float('nan'),float('inf'),-.01,1.01,True]:
   with self.assertRaises(ValueError):land_option(100,20,p=x)
  for x in [float('nan'),float('inf'),-.51,.51]:
   with self.assertRaises(ValueError):recovery(1000,600,620,100,cost_growth=x)
  with self.assertRaises(ValueError):recovery(600,600,620,100)
 def test_rounding_contract(self):
  f={'tag':'x','dimensions':{},'start':'','end':'2025-01-01','unit':'iso4217:USD','value':1683109000,'decimals':'-3','element_index':1}
  q=dict(f,value=1680000000,decimals='-7',element_index=2);v=[]
  self.assertEqual(select([q,f],['x'],{},'','2025-01-01',v),f);self.assertEqual(len(v),1)
  with self.assertRaises(ValueError):select([f,dict(f,value=1684109000)],['x'],{},'','2025-01-01',[])

class IndependentReconciliation(unittest.TestCase):
 def rows(self,p,n):
  with (ROOT/p/'outputs'/n).open() as f:return list(csv.DictReader(f))
 def test_all_land_state_enumeration(self):
  latest={r['ticker']:r for r in self.rows(LAND,'latest_decisions.csv')}
  for row in self.rows(LAND,'conditional_option_grid.csv'):
   r=latest[row['ticker']];k=Decimal(r['remaining_price']);v=k*Decimal(row['value_ratio_assumed']);p=Decimal(row['up_probability_assumed']);disc=Decimal(1)+Decimal(row['discount_rate_assumed']);fee=Decimal(row['extension_cost_rate_assumed'])*k
   # Enumerate all four independent exercise/abandon policies across two future states.
   policies=[]
   for au,ad in itertools.product([0,1],repeat=2):policies.append((p*au*(v*Decimal('1.25')-k)+(1-p)*ad*(v*Decimal('.75')-k))/disc-fee)
   self.assertAlmostEqual(float(max(policies)),float(row['wait']),delta=max(.001,float(k)*1e-12))
 def test_all_hotel_decimal_and_root(self):
  latest={r['ticker']:r for r in self.rows(HOTEL,'latest_decisions.csv')}
  for row in self.rows(HOTEL,'conditional_recovery_grid.csv'):
   r=latest[row['ticker']];D=Decimal;R=D(r['revenue']);RR=D(r['reimb_revenue']);RE=D(r['reimb_expense']);O=D(r['op_income']);B=R-RR;P=O-RR+RE;cost=D(row['cost_growth_assumed']);g=D(row['recovery_growth_assumed']);budget=D(row['budget_share_assumed'])*B;floor=D(row['income_floor_assumed'])*B
   actual=P+RR*(1+g)-RE*(1+cost)-budget;self.assertAlmostEqual(float(actual),float(row['scenario_op_income']),delta=.001)
   # Independent bisection of the income-floor constraint; no analytic formula reused.
   lo,hi=D('-10'),D('10')
   for _ in range(90):
    mid=(lo+hi)/2
    if P+RR*(1+mid)-RE*(1+cost)-budget<floor:lo=mid
    else:hi=mid
   self.assertAlmostEqual(float((lo+hi)/2),float(row['required_recovery_growth']),places=10)
 def test_source_pointers_and_reconstruction(self):
  for project in [LAND,HOTEL]:
   sources={p.name:{f['element_index']:f for f in json.loads(gzip.decompress(p.read_bytes()))} for p in (ROOT/project/'data/raw').glob('*.gz')};groups={}
   for r in self.rows(project,'source_lineage.csv'):
    f=sources[r['source_file']][int(r['cell_index'])];self.assertEqual(f['tag'],r['tag']);self.assertEqual(f['context'],r['context']);self.assertEqual(f['dimensions'],json.loads(r['dimensions']));self.assertEqual(f['start'],r['start']);self.assertEqual(f['end'],r['end']);self.assertEqual(f['value'],float(r['value_usd']));self.assertEqual(f['unit'].upper(),'ISO4217:USD');groups.setdefault(r['record'],[]).append(r)
   for r in self.rows(project,'panel.csv'):
    key=r['ticker']+'|'+(r['scope']+'|'+r['end'] if project==LAND else r['start']+'|'+r['end']);a=groups[key]
    metrics=['deposits','disclosed_price'] if project==LAND else ['revenue','reimb_revenue','reimb_expense','op_income','operating_costs']
    for metric in metrics:self.assertEqual(float(r[metric]),sum(float(x['value_usd']) for x in a if x['metric']==metric or x['metric'].startswith(metric+'_component_')))
 def test_scope_and_sql(self):
  for r in self.rows(LAND,'scope_reconciliation.csv'):self.assertEqual(float(r['difference']),0)
  for r in self.rows(HOTEL,'yoy_income_bridge.csv'):self.assertEqual(float(r['identity_error']),0)
  # Independent grouped totals check SQL output against raw records, including no double-counted land components or overlapping periods.
  for project in [LAND,HOTEL]:
   panel=self.rows(project,'panel.csv');sql=self.rows(project,'sql_summary.csv')
   for r in sql:
    a=[x for x in panel if x['ticker']==r['ticker'] and (x['scope']=='total' if project==LAND else x['period']=='annual')]
    self.assertEqual(int(r['total_scope_dates'] if project==LAND else r['annual_records']),len(a))
    if project==LAND:self.assertEqual(float(r['historical_deposit_sum_not_current_exposure']),sum(float(x['deposits']) for x in a))
    else:self.assertEqual(float(r['annual_profit_ex_recovery']),sum(float(x['op_income'])-float(x['reimb_revenue'])+float(x['reimb_expense']) for x in a))
if __name__=='__main__':unittest.main()
