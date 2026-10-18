import copy,json,random,unittest
from pathlib import Path
from model import generate,poisson,simulate
ROOT=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
    def setUp(self):
        self.c=json.loads((ROOT/'config.json').read_text());self.c.update(arrival_days=1,calendar_days=3,warmup_days=0,evaluation_end_day=1,base_slots=2,booking_window=3,urgent_no_show=0,routine_no_show=0)
    def req(self,flags):return [dict(request_id=i,request_day=0,urgent=v,show_uniform=.5) for i,v in enumerate(flags)]
    def policy(self,**kw):return dict(name='test',reserved=0,release_days=-1,extra_slots=0,setup_cost_usd=0,priority=False,**kw)
    def test_fifo_capacity(self):
        m,r=simulate(self.c,self.policy(),self.req([0,0,0]),[0,0,0])
        self.assertEqual([x['wait_days'] for x in r],[0,0,1]);self.assertEqual(m['completed'],3)
    def test_reserved_not_double_counted(self):
        p=self.policy();p.update(reserved=1,priority=True)
        m,r=simulate(self.c,p,self.req([1,0]),[0,0,0])
        self.assertTrue(all(x['wait_days']==0 for x in r));self.assertEqual({x['slot_class'] for x in r},{'public','reserved'})
    def test_unused_reserve(self):
        p=self.policy();p['reserved']=1
        _,r=simulate(self.c,p,self.req([0,0]),[0,0,0]);self.assertEqual([x['wait_days'] for x in r],[0,1])
    def test_released_reserve(self):
        p=self.policy();p.update(reserved=1,release_days=0)
        _,r=simulate(self.c,p,self.req([0,0]),[0,0,0]);self.assertEqual([x['wait_days'] for x in r],[0,0])
    def test_no_show_separate_from_access(self):
        self.c['routine_no_show']=1
        m,_=simulate(self.c,self.policy(),self.req([0]),[0,0,0])
        self.assertEqual(m['routine_service'],1);self.assertEqual(m['completed'],0);self.assertEqual(m['no_shows'],1)
    def test_unbooked_denominator(self):
        self.c['calendar_days']=1
        m,_=simulate(self.c,self.policy(),self.req([0,0,0]),[0]);self.assertEqual(m['unbooked'],1);self.assertAlmostEqual(m['routine_service'],2/3)
    def test_absence_respects_capacity(self):
        m,r=simulate(self.c,self.policy(),self.req([0,0,0]),[2,2,2]);self.assertEqual(m['booked'],0);self.assertEqual(len(r),3)
    def test_deterministic_requests(self):
        a=generate(self.c,100);b=generate(self.c,100);self.assertEqual(a,b)
    def test_poisson_boundary(self):
        self.assertEqual(poisson(random.Random(1),0),0)
        with self.assertRaises(ValueError):poisson(random.Random(1),-1)
    def test_invalid_reserve(self):
        p=self.policy();p['reserved']=3
        with self.assertRaises(ValueError):simulate(self.c,p,self.req([0]),[0,0,0])
if __name__=='__main__':unittest.main()
