"""Retrospective expanding-window recession classification, with twelve-month label embargo."""
import json,csv,sqlite3
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import rankdata
from common import ROOT,CREDIT,dump,csvout,digest,readcsv

def objective(beta,X,y,penalty):
 z=X@beta
 loss=np.logaddexp(0,z).sum()-y@z+.5*penalty*(beta[1:]@beta[1:])
 grad=X.T@(expit(z)-y)+penalty*np.r_[0,beta[1:]]
 return loss,grad

def fit_predict(X,y,x,penalty):
 mu=X.mean(axis=0);sd=X.std(axis=0);sd=np.where(sd<1e-10,1,sd)
 A=np.column_stack([np.ones(len(X)),(X-mu)/sd]);b=np.r_[1,(x-mu)/sd]
 opt=minimize(objective,np.zeros(A.shape[1]),args=(A,y,penalty),jac=True,method='L-BFGS-B',options={'maxiter':300,'ftol':1e-12,'gtol':1e-7})
 if not opt.success and np.linalg.norm(opt.jac)>1e-4:raise ValueError(opt.message)
 return float(expit(b@opt.x))

def auc(y,p):
 pos=y==1;n=pos.sum();m=(~pos).sum()
 return float((rankdata(p)[pos].sum()-n*(n+1)/2)/(n*m)) if n and m else None

def metrics(y,p,threshold=.5):
 pred=p>=threshold
 return {'n':len(y),'positive_months':int(y.sum()),'brier':float(np.mean((p-y)**2)),'log_loss':float(-np.mean(y*np.log(np.clip(p,1e-12,1))+(1-y)*np.log(np.clip(1-p,1e-12,1)))),'roc_auc':auc(y,p),'tp':int(np.sum(pred&(y==1))),'fp':int(np.sum(pred&(y==0))),'fn':int(np.sum(~pred&(y==1))),'tn':int(np.sum(~pred&(y==0)))}

def make_panel():
 p=ROOT/CREDIT/'data';manifest=json.loads((p/'manifest.json').read_text());assert digest(p/'monthly.csv')==manifest['projection_sha256']
 rows=readcsv((p/'monthly.csv'));dates=[x['observation_date'] for x in rows];assert len(set(dates))==len(dates)
 arr=np.array([[float(r[k]) if r[k] not in ('','.','NA') else np.nan for k in ['BAA10YM','GS10','TB3MS','USREC']] for r in rows]);panel=[]
 for i in range(4,len(rows)-12):
  if dates[i]<'1970-01-01':continue
  # All feature months precede origin; target excludes contemporaneous recession state.
  if not np.isfinite(arr[i-4:i+13]).all():continue
  assert arr[i+1:i+13,3].max() in (0,1)
  panel.append(dict(date=dates[i],feature_month=dates[i-1],label_end=dates[i+12],curve=float(arr[i-1,1]-arr[i-1,2]),spread=float(arr[i-1,0]),spread_change=float(arr[i-1,0]-arr[i-4,0]),y=int(arr[i+1:i+13,3].max())))
 return panel

def forecasts(panel,model,penalty,start,end):
 cols=['curve'] if model=='curve' else ['curve','spread','spread_change'];out=[]
 for r in panel:
  if not start<=r['date']<=end:continue
  train=[x for x in panel if x['label_end']<=r['date'] and x['date']<r['date']]
  assert train and max(x['label_end'] for x in train)<=r['date']
  X=np.array([[x[k] for k in cols] for x in train]);y=np.array([x['y'] for x in train]);x=np.array([r[k] for k in cols]);prob=fit_predict(X,y,x,penalty)
  out.append(dict(date=r['date'],y=r['y'],probability=prob,unconditional=float(y.mean()),n_train=len(train),last_training_origin=train[-1]['date'],last_training_label=train[-1]['label_end']))
 return out

def block_interval(d,block=24,reps=2000):
 rng=np.random.default_rng(26026);n=len(d);means=[]
 for _ in range(reps):
  starts=rng.integers(0,n,size=int(np.ceil(n/block)));idx=np.concatenate([(s+np.arange(block))%n for s in starts])[:n];means.append(float(np.mean(d[idx])))
 return [float(x) for x in np.quantile(means,[.025,.975])]

def analyze():
 panel=make_panel();out=ROOT/CREDIT/'outputs';tuning=[];selected={}
 for model in ['curve','credit']:
  for penalty in [.1,1.,10.]:
   f=forecasts(panel,model,penalty,'2000-01-01','2006-12-01');y=np.array([x['y'] for x in f]);p=np.array([x['probability'] for x in f]);tuning.append(dict(model=model,penalty=penalty,brier=float(np.mean((p-y)**2)),months=len(y)))
  selected[model]=min([x for x in tuning if x['model']==model],key=lambda x:(x['brier'],-x['penalty']))['penalty']
 cal=forecasts(panel,'credit',selected['credit'],'2000-01-01','2006-12-01');cy=np.array([x['y'] for x in cal]);cp=np.array([x['probability'] for x in cal]);thresholds=[]
 for cost in [1,3,5,10]:
  grid=np.linspace(.05,.95,19);v=[float(np.sum((cp>=t)&(cy==0))+cost*np.sum((cp<t)&(cy==1))) for t in grid];t=float(grid[np.argmin(v)]);thresholds.append(dict(false_negative_cost=cost,threshold=t,calibration_loss=min(v)))
 threshold=next(x['threshold'] for x in thresholds if x['false_negative_cost']==5)
 a=forecasts(panel,'curve',selected['curve'],'2008-01-01','2023-12-01');b=forecasts(panel,'credit',selected['credit'],'2008-01-01','2023-12-01');assert [x['date'] for x in a]==[x['date'] for x in b]
 results=[dict(**x,curve_probability=z['probability'],candidate_probability=x['probability']) for z,x in zip(a,b)];y=np.array([x['y'] for x in b]);p=np.array([x['probability'] for x in b]);q=np.array([x['probability'] for x in a]);u=np.array([x['unconditional'] for x in b]);delta=(p-y)**2-(q-y)**2
 interval=block_interval(delta);unconditional_delta=(p-y)**2-(u-y)**2;unconditional_interval=block_interval(unconditional_delta);positive_episodes=int(sum(1 for i,x in enumerate(y) if x and (i==0 or y[i-1]==0)))
 sens=[]
 for block in [12,24,36]:sens.append(dict(kind='block_interval',setting=block,n=len(y),delta_brier=float(delta.mean()),low=block_interval(delta,block)[0],high=block_interval(delta,block)[1]))
 mask=np.array([not '2019-01-01'<=x['date']<='2020-12-01' for x in b]);sens.append(dict(kind='exclude_pandemic_origins',setting='2019-2020',n=int(mask.sum()),delta_brier=float(delta[mask].mean()),low=None,high=None))
 for s,e in [('2008-01-01','2015-12-01'),('2016-01-01','2023-12-01')]:
  m=np.array([s<=x['date']<=e for x in b]);sens.append(dict(kind='subperiod',setting=s[:4]+'-'+e[:4],n=int(m.sum()),delta_brier=float(delta[m].mean()),low=None,high=None))
 report={'panel_months':len(panel),'test_months':len(y),'target':'Any NBER recession month in t+1 through t+12; prior-month features','train_start':'1970-01','tuning_origins':'2000-01 to 2006-12; labels through 2007-12','test_origins':'2008-01 to 2023-12; labels through 2024-12','selected_penalties':selected,'threshold_5_to_1':threshold,'candidate':metrics(y,p,threshold),'curve_baseline':metrics(y,q,threshold),'expanding_unconditional':metrics(y,u,threshold),'delta_brier':float(delta.mean()),'delta_brier_block24_interval':interval,'delta_brier_vs_unconditional':float(unconditional_delta.mean()),'delta_vs_unconditional_block24_interval':unconditional_interval,'positive_target_runs_in_test':positive_episodes,'promotion_gate':bool(interval[1]<0 and unconditional_interval[1]<0 and positive_episodes>=3),'promotion_requires':'Upper descriptive block intervals below zero against BOTH baselines AND at least three distinct positive target runs; no real-time adoption without vintage/publication-delay replay','interpretation':'Revised-data retrospective classification, not a live forecast, causal signal or validated trading strategy.'}
 csvout(out/'panel.csv',panel);csvout(out/'tuning.csv',tuning);csvout(out/'test_predictions.csv',results);csvout(out/'thresholds.csv',thresholds);csvout(out/'sensitivity.csv',sens)
 db=sqlite3.connect(':memory:');db.execute('CREATE TABLE forecasts(date TEXT,y INT,p REAL,q REAL)');db.executemany('INSERT INTO forecasts VALUES(?,?,?,?)',[(x['date'],x['y'],x['probability'],x['curve_probability']) for x in results]);year=db.execute('SELECT substr(date,1,4),count(*),sum(y),avg((p-y)*(p-y)),avg((q-y)*(q-y)) FROM forecasts GROUP BY 1').fetchall();csvout(out/'sql_annual_scores.csv',[dict(year=x[0],months=x[1],positives=x[2],candidate_brier=x[3],curve_brier=x[4]) for x in year]);dump(out/'metrics.json',report);print(CREDIT,report,flush=True)
 return report
if __name__=='__main__':analyze()
