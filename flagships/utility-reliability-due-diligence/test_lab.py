import copy,json,math,threading,unittest,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from analysis import scenario,quantile,peer_reference,predictions,read_panel,valid
from etl import number
from app import Handler,api
class CoreTests(unittest.TestCase):
    def test_missing_is_not_zero(self):
        self.assertIsNone(number('.'));self.assertIsNone(number(None));self.assertEqual(number(0),0)
    def test_invalid_numeric_source(self):
        for x in [-1,float('nan'),'unexpected']:
            with self.assertRaises(ValueError):number(x)
    def test_scenario_hand_calculation(self):
        r=scenario(60,1000,.1,10,500,0,2)
        self.assertEqual(r['annual_customer_hours_avoided_proxy'],100)
        self.assertEqual(r['break_even_upfront_cost_usd'],1000)
    def test_discounted_scenario(self):
        r=scenario(60,1000,.1,10,0,.1,2)
        self.assertAlmostEqual(r['break_even_upfront_cost_usd'],1000/1.1+1000/1.1**2)
    def test_invalid_scenario(self):
        for reduction in [-.1,1.1,float('nan')]:
            with self.assertRaises(ValueError):scenario(60,1000,reduction,10,0,.1,10)
    def test_quantile(self):
        self.assertEqual(quantile([5,1,3],.5),3)
        with self.assertRaises(ValueError):quantile([],1)
    def test_peer_excludes_whole_utility(self):
        pool=[dict(utility_id=i,state='TX',ownership='Cooperative',customers=20000,saidi_normal=100+i) for i in range(20)]
        pool.append(dict(utility_id=0,state='NM',ownership='Cooperative',customers=20000,saidi_normal=99999))
        name,peers=peer_reference(pool[0],pool)
        self.assertTrue(all(r['utility_id']!=0 for r in peers));self.assertEqual(name,'state_ownership')
    def test_peer_fallback(self):
        pool=[dict(utility_id=i,state=str(i),ownership='Cooperative',customers=20000,saidi_normal=100) for i in range(20)]
        self.assertEqual(peer_reference(pool[0],pool)[0],'ownership_size')
    def test_future_target_does_not_change_predictions(self):
        rows=read_panel();before=predictions(rows,2025)
        changed=copy.deepcopy(rows)
        for r in changed:
            if r['year']==2025 and valid(r):r['saidi_normal']+=10000
        after=predictions(changed,2025)
        self.assertEqual([r['prediction'] for r in before],[r['prediction'] for r in after])
    def test_view_excludes_quarantine(self):
        m=api('/api/status',{});rows=api('/api/utilities',{})['rows']
        self.assertEqual(m['decision_view_year'],2024);self.assertEqual(m['quarantined_years'],[2025]);self.assertFalse(m['predictive_component_promotable'])
        self.assertTrue(all(int(r['year'])==2024 for r in rows))
    def test_filter(self):
        r=api('/api/utilities',{'state':['TX'],'ownership':['Cooperative']})['rows']
        self.assertTrue(r);self.assertTrue(all(x['state']=='TX' and x['ownership']=='Cooperative' for x in r))
    def test_api_rejects_unknown_utility(self):
        with self.assertRaises(ValueError):api('/api/scenario',{'utility_id':['-1'],'state':['TX']})
class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.origin=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_status_and_headers(self):
        with urllib.request.urlopen(self.origin+'/api/status') as r:
            self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff');self.assertEqual(json.load(r)['decision_view_year'],2024)
    def test_index(self):
        with urllib.request.urlopen(self.origin+'/') as r:self.assertIn(b'Utility reliability due diligence',r.read())
    def test_unlisted_paths_not_served(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(self.origin+'/../config.json')
        self.assertEqual(cm.exception.code,404)
    def test_invalid_scenario_is_400(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(self.origin+'/api/scenario?utility_id=-1&state=TX')
        self.assertEqual(cm.exception.code,400)
if __name__=='__main__':unittest.main()
