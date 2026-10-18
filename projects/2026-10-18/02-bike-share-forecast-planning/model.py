"""Forecast realized rentals with only information available before target day."""
from datetime import date
import math, statistics

def features(rows,i):
    if i<28:raise ValueError('28 lagged days required')
    # Deliberately exclude contemporaneous weather, casual and registered counts.
    day=date.fromisoformat(rows[i]['dteday']);doy=day.timetuple().tm_yday
    past=[int(r['cnt']) for r in rows[i-28:i]]
    return [1.,i/365,math.sin(2*math.pi*doy/365.25),math.cos(2*math.pi*doy/365.25),int(rows[i]['holiday']),*map(float,[day.weekday()==d for d in range(6)]),float(past[-1]),float(past[-7]),statistics.mean(past[-7:]),statistics.mean(past)]

def solve_linear(a,b):
    n=len(b);a=[list(row)+[b[i]] for i,row in enumerate(a)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda j:abs(a[j][i]));a[i],a[pivot]=a[pivot],a[i]
        if abs(a[i][i])<1e-12:raise ValueError('Singular linear system')
        factor=a[i][i];a[i]=[x/factor for x in a[i]]
        for j in range(n):
            if j==i:continue
            factor=a[j][i];a[j]=[x-factor*y for x,y in zip(a[j],a[i])]
    return [row[-1] for row in a]

def fit(rows,end,alpha):
    x=[features(rows,i) for i in range(28,end)];y=[float(rows[i]['cnt']) for i in range(28,end)]
    if not x:raise ValueError('No training rows')
    p=len(x[0]);mu=[0.]+[statistics.mean(row[j] for row in x) for j in range(1,p)];sd=[1.]+[statistics.pstdev(row[j] for row in x) or 1. for j in range(1,p)]
    z=[[(v-mu[j])/sd[j] for j,v in enumerate(row)] for row in x]
    xtx=[[sum(row[j]*row[k] for row in z)+(alpha if j==k and j>0 else 0) for k in range(p)] for j in range(p)]
    xty=[sum(row[j]*target for row,target in zip(z,y)) for j in range(p)]
    return dict(mu=mu,sd=sd,beta=solve_linear(xtx,xty),train_end_exclusive=end)

def predict(fitted,rows,i):
    if fitted['train_end_exclusive']>i:raise ValueError('Future data in training')
    x=features(rows,i)
    return max(0.,sum(b*(v-m)/s for b,v,m,s in zip(fitted['beta'],x,fitted['mu'],fitted['sd'])))

def quantile(values,q,finite_sample=False):
    if not values or not 0<=q<=1:raise ValueError('Invalid quantile')
    ordered=sorted(values);rank=math.ceil((len(values)+1 if finite_sample else len(values))*q)
    return ordered[min(len(values)-1,max(0,rank-1))]

def decision_cost(actual,capacity,under,over):
    if min(actual,capacity,under,over)<0:raise ValueError('Negative cost/capacity input')
    return max(actual-capacity,0)*under+max(capacity-actual,0)*over

def run_forecasts(rows,models,start):
    fits={};records=[]
    for i in range(start,len(rows)):
        day=rows[i]['dteday'];month=day[:7]
        for name in models:
            train_end=i-1
            if name=='seasonal_naive':pred=float(rows[i-7]['cnt'])
            elif name=='weekday_mean':pred=statistics.mean(int(rows[i-k]['cnt']) for k in [7,14,21,28])
            else:
                if (name,month) not in fits:fits[name,month]=fit(rows,i,float(name.split('_')[1]))
                f=fits[name,month];pred=predict(f,rows,i);train_end=f['train_end_exclusive']-1
            records.append(dict(date=day,index=i,model=name,actual=int(rows[i]['cnt']),prediction=pred,error=int(rows[i]['cnt'])-pred,train_end_index=train_end,latest_target_lag_index=i-1))
    return records
