"""Rebuild the evidence tables, SQLite database, charts and findings."""
from pathlib import Path
import sys,json,csv,sqlite3,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import bill,twelve_cycles,COMMON_DELIVERY
ROOT=Path(__file__).resolve().parents[1]

def save_csv(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    plans=json.loads((ROOT/'data/plans.json').read_text());profiles=json.loads((ROOT/'data/scenarios.json').read_text())['profiles']
    manifest=json.loads((ROOT/'data/source_manifest.json').read_text());sources={s['id']:s for s in manifest}
    audits=[];curves=[];scenario=[];threshold=[]
    for p in plans:
        s=sources[p['source_id']]
        assert s['status']=='downloaded' and len(s['sha256'])==64
        raw=ROOT/f"data/raw/{s['id']}.pdf"
        if raw.exists():
            assert s['sha256']==hashlib.sha256(raw.read_bytes()).hexdigest()
        for q,expected in zip([500,1000,2000],p['published_cents']):
            b=bill(p,q);delta=b['effective_cents']-expected
            audits.append(dict(plan_id=p['id'],source_id=p['source_id'],source_page=1,kwh=q,published_cents=expected,rebuilt_cents=b['effective_cents'],difference_cents=delta,within_rounding=abs(delta)<=0.05000001))
        for q in range(250,3001):
            b=bill(p,q,normalized=True);curves.append(dict(plan_id=p['id'],kwh=q,bill_dollars=b['total'],credit_dollars=b['credit']))
        if p['credit_rule']!='none':
            t=p['credit_threshold'];a=bill(p,t-1,normalized=True);b=bill(p,t,normalized=True);c=bill(p,t+1,normalized=True)
            threshold.append(dict(plan_id=p['id'],threshold_kwh=t,bill_below=a['total'],bill_at=b['total'],bill_above=c['total'],change_below_to_at=b['total']-a['total'],change_at_to_above=c['total']-b['total']))
        if p['term_months']>=12:
            for profile in profiles:
                b=twelve_cycles(p,profile['usage'])
                scenario.append(dict(plan_id=p['id'],profile_id=profile['id'],total_kwh=sum(profile['usage']),cost_dollars=b['total'],credit_dollars=b['credits'],credit_cycles=b['credit_cycles']))
    assert all(x['within_rounding'] for x in audits),'Published-price reconciliation failed'
    save_csv('published_price_audit.csv',audits);save_csv('cost_curves.csv',curves);save_csv('scenario_results.csv',scenario);save_csv('threshold_audit.csv',threshold)
    con=sqlite3.connect(ROOT/'results/audit.sqlite')
    con.executescript('DROP TABLE IF EXISTS plans; DROP TABLE IF EXISTS price_audit; DROP TABLE IF EXISTS scenarios; CREATE TABLE plans (id TEXT PRIMARY KEY, provider TEXT, name TEXT, efl_date TEXT, term_months INTEGER, source_id TEXT, credit_rule TEXT, threshold_kwh REAL); CREATE TABLE price_audit (plan_id TEXT, kwh REAL, published_cents REAL, rebuilt_cents REAL, difference_cents REAL, within_rounding INTEGER); CREATE TABLE scenarios (plan_id TEXT, profile_id TEXT, total_kwh REAL, cost_dollars REAL, credit_dollars REAL, credit_cycles INTEGER);')
    con.executemany('INSERT INTO plans VALUES (?,?,?,?,?,?,?,?)',[(p['id'],p['provider'],p['name'],p['efl_date'],p['term_months'],p['source_id'],p['credit_rule'],p['credit_threshold']) for p in plans])
    con.executemany('INSERT INTO price_audit VALUES (?,?,?,?,?,?)',[(a['plan_id'],a['kwh'],a['published_cents'],a['rebuilt_cents'],a['difference_cents'],a['within_rounding']) for a in audits])
    con.executemany('INSERT INTO scenarios VALUES (?,?,?,?,?,?)',[tuple(x.values()) for x in scenario]);con.commit()
    findings={'plan_count':len(plans),'provider_count':len(set(p['provider'] for p in plans)),'reconciled_prices':len(audits),'max_abs_rounding_difference_cents':max(abs(a['difference_cents']) for a in audits),'source_attempts':len(manifest),'downloaded_pdfs':sum(s['status']=='downloaded' for s in manifest),'common_delivery':COMMON_DELIVERY,'browser_qa':'Not performed: user excludes browser operation.','status':'Approved release snapshot: 31 October 2026'}
    for p in plans:
        if p['id']=='discount-credit-12':
            a=twelve_cycles(p,profiles[0]['usage']);b=twelve_cycles(p,profiles[1]['usage']);findings['equal_total_comparison']={'plan_id':p['id'],'total_kwh':12000,'steady_cost':a['total'],'uneven_cost':b['total'],'difference':b['total']-a['total'],'steady_credit_cycles':a['credit_cycles'],'uneven_credit_cycles':b['credit_cycles']}
            findings['threshold']=next(t for t in threshold if t['plan_id']==p['id'])
    # Exact analytical crossing, valid only in the >=1000-kWh segment.
    basic=next(p for p in plans if p['id']=='discount-basic-36');credit=next(p for p in plans if p['id']=='discount-credit-12')
    findings['crossing_kwh']=credit['credit_dollars']/((credit['energy_cents']-basic['energy_cents'])/100)
    (ROOT/'results/findings.json').write_text(json.dumps(findings,indent=2)+'\n')
    from charts import make_charts
    make_charts(plans,profiles)
    print(json.dumps(findings,indent=2))

if __name__=='__main__':main()
