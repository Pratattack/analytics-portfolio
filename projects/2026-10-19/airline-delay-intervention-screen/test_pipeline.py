import csv,itertools,json,math,random,unittest
from collections import defaultdict,Counter
from pathlib import Path
import pipeline as p
import io,gzip,zipfile
def read_csv(path):
    text=gzip.decompress(path.read_bytes()).decode() if path.suffix==".gz" else zipfile.ZipFile(path).read("Airline_Delay_Cause.csv").decode("utf-8-sig") if path.suffix==".zip" else path.read_text(encoding="utf-8-sig")
    return csv.DictReader(io.StringIO(text))

class Methods(unittest.TestCase):
    def test_excluded_self_peer_hand_case(self):
        cfg=json.loads((p.BASE/'config.json').read_text());row=p.load(cfg)[1][0]
        rows=[]
        for i,minutes in enumerate([100,200,300,400]):
            r=dict(row,year=2024,month=1,airport='TEST',carrier=str(i),arr_flights=1000.,carrier_delay=float(minutes));rows.append(r)
        db=p.warehouse(rows);result=[dict(x) for x in db.execute('SELECT * FROM peer_screen ORDER BY carrier')]
        self.assertEqual(len(result),4);self.assertAlmostEqual(result[0]['peer_minutes_per_flight'],.3)
        self.assertAlmostEqual(result[0]['excess_minutes'],-200);self.assertAlmostEqual(result[3]['excess_minutes'],200)
    def test_single_carrier_and_sparse_peers_rejected(self):
        cfg=json.loads((p.BASE/'config.json').read_text());row=p.load(cfg)[1][0]
        for size in [1,2,3]:
            db=p.warehouse([dict(row,airport='TEST',carrier=str(i),arr_flights=1000) for i in range(size)])
            self.assertEqual(db.execute('SELECT count(*) FROM peer_screen').fetchone()[0],0)
    def test_partition_cap_matches_exhaustive_oracle(self):
        cohort={(str(i),airport):{'score':v} for i,(airport,v) in enumerate([('A',10),('A',9),('B',8),('B',4),('C',3),('D',-1)])}
        picked=p.select(cohort,'score',3,1)
        feasible=[]
        for n in range(4):
            for s in itertools.combinations(cohort,n):
                if max(Counter(k[1] for k in s).values(),default=0)<=1:feasible.append(sum(cohort[k]['score'] for k in s))
        self.assertEqual(sum(cohort[k]['score'] for k in picked),max(feasible));self.assertEqual(len(picked),3)
    def test_economics_hand_case_and_input_bounds(self):
        r=p.scenario(10000,50,.2,10000,5);self.assertEqual(r['modeled_net_usd'],50000);self.assertEqual(r['break_even_recoverable_fraction'],.1)
        self.assertEqual(p.scenario(-100,50,.2,10000,5)['modeled_net_usd'],-50000)
        self.assertIsNone(p.scenario(0,50,.2,10000,5)['break_even_recoverable_fraction'])
        with self.assertRaises(AssertionError):p.scenario(1,10,1.1,1,1)
    def test_source_lineage_and_independent_peer_reconciliation(self):
        raw=list(read_csv(p.BASE/'data/raw/bts_export.zip'))
        cfg=json.loads((p.BASE/'config.json').read_text());_,valid,issues=p.load(cfg)
        quarantine={r['source_row'] for r in issues};good={r['source_row'] for r in valid}
        self.assertFalse(quarantine&good);self.assertEqual(good|quarantine,set(range(2,len(raw)+2)))
        total=defaultdict(lambda:[0.,0.,0])
        for r in valid:
            t=total[(r['year'],r['month'],r['airport'])];t[0]+=r['arr_flights'];t[1]+=r['carrier_delay'];t[2]+=1
        output=list(read_csv(p.BASE/'outputs/source_audited_peer_rows.csv.gz'))
        for row in output:
            source=raw[int(row['source_row'])-2]
            for field in p.NUM:self.assertEqual(float(row[field]),float(source[field]))
            self.assertEqual(row['carrier'],source['carrier']);self.assertEqual(row['airport'],source['airport'])
            n,m,c=total[(int(row['year']),int(row['month']),row['airport'])];f=float(row['arr_flights']);v=float(row['carrier_delay'])
            self.assertAlmostEqual(float(row['peer_minutes_per_flight']),(m-v)/(n-f),places=9)
            self.assertAlmostEqual(float(row['excess_minutes']),v-f*(m-v)/(n-f),places=6)
        self.assertEqual(len(output),sum(1 for r in valid if total[(r['year'],r['month'],r['airport'])][2]-1>=3 and total[(r['year'],r['month'],r['airport'])][0]-r['arr_flights']>=1000))
    def test_discovery_only_selection_and_policy_reconciliation(self):
        rows=list(read_csv(p.BASE/'outputs/source_audited_peer_rows.csv.gz'))
        groups=defaultdict(list)
        for r in rows:
            if r['year']=='2024' and int(r['month'])<=8:groups[(r['carrier'],r['airport'])].append(r)
        pool={k:g for k,g in groups.items() if len(g)>=6 and sum(float(r['arr_flights']) for r in g)>=1000}
        ordered=sorted(pool,key=lambda k:(-sum(float(r['excess_minutes']) for r in pool[k]),k));picked=[];counts=Counter()
        for k in ordered:
            if sum(float(r['excess_minutes']) for r in pool[k])>0 and counts[k[1]]<2 and len(picked)<10:picked.append(k);counts[k[1]]+=1
        selected=list(read_csv(p.BASE/'outputs/investigation_shortlist.csv'));self.assertEqual(picked,[(r['carrier'],r['airport']) for r in selected])
        test=defaultdict(float)
        for r in rows:
            if r['year']=='2026':test[(r['carrier'],r['airport'])]+=float(r['excess_minutes'])
        capture=100*sum(max(0,test[k]) for k in picked)/sum(max(0,test[k]) for k in pool)
        metrics=json.loads((p.BASE/'outputs/metrics.json').read_text());self.assertAlmostEqual(capture,metrics['strict_diagnostic']['positive_excess_capture_pct'])
        self.assertFalse(metrics['prospective_deployment_gate'])
    def test_bootstrap_optimized_equals_independent_expanded_samples(self):
        rows=[{'year':2026,'month':m,'carrier':c,'airport':'A','excess_minutes':v+m,'arr_flights':100,'carrier_delay':100} for m in range(1,9) for c,v in [('X',20),('Y',10),('Z',-20)]]
        cfg={'bootstrap_seed':1,'bootstrap_replicates':20,'months':list(range(1,9))};pool=[('X','A'),('Y','A'),('Z','A')];actual=p.bootstrap(rows,pool[:1],pool[1:2],pool,2026,cfg)
        rng=random.Random(1);answers=[]
        for _ in range(20):
            draw=[]
            for __ in range(4):
                s=rng.randrange(8);draw.extend([s+1,(s+1)%8+1])
            expanded=[r for m in draw for r in rows if r['month']==m]
            a=p.evaluate(expanded,pool[:1],pool,2026,cfg['months']);b=p.evaluate(expanded,pool[1:2],pool,2026,cfg['months']);answers.append(a['positive_excess_capture_pct']-b['positive_excess_capture_pct'])
        answers.sort()
        for a,b in zip(actual,[answers[0],answers[19]]):self.assertAlmostEqual(a,b)

if __name__=='__main__':unittest.main()
