import numpy as np
from scipy.optimize import linprog

def cvar(losses,alpha=.9):
 x=np.asarray(losses,dtype=float)
 if x.ndim!=1 or len(x)==0 or not np.isfinite(x).all() or not 0<alpha<1:raise ValueError('Invalid historical loss sample')
 z=float(np.sort(x)[min(len(x)-1,int(np.floor(alpha*len(x))))]);return z+float(np.maximum(x-z,0).mean()/(1-alpha))

def evaluate(returns,net,hedges,cost_bps=15):
 r=np.asarray(returns,dtype=float);net=np.asarray(net,dtype=float);h=np.asarray(hedges,dtype=float)
 if r.ndim!=2 or r.shape[1]!=len(net) or len(h)!=len(net) or not np.isfinite(r).all() or not np.isfinite(net).all() or not np.isfinite(h).all() or np.any(h<0) or np.any(h>1) or not np.isfinite(cost_bps) or cost_bps<0:raise ValueError('Invalid exposure or hedge assumptions')
 cost=float(np.sum(np.abs(net)*h)*cost_bps/10000);losses=r@(net*(1-h))+cost
 return dict(losses=losses.tolist(),cvar90=cvar(losses),worst=float(losses.max()),mean=float(losses.mean()),cost=cost,hedged_notional=float(np.sum(np.abs(net)*h)))

def fit(returns,net,coverage_cap=.5,cost_bps=15,alpha=.9):
 r=np.asarray(returns,dtype=float);net=np.asarray(net,dtype=float);n,m=r.shape
 if not 0<=coverage_cap<=1 or not np.isfinite(r).all() or n<12 or m!=len(net) or cost_bps<0:raise ValueError('Invalid fitting inputs')
 # h: currency hedge fractions, z: empirical tail threshold, u: scenario excess costs.
 base=r@net;coef=-r*net+cost_bps/10000*np.abs(net);A=np.zeros((n+1,m+1+n));A[:n,:m]=coef;A[:n,m]=-1;A[:n,m+1:]=-np.eye(n);A[n,:m]=np.abs(net);b=np.r_[-base,coverage_cap*np.abs(net).sum()];objective=np.r_[np.zeros(m),1,np.repeat(1/((1-alpha)*n),n)]
 res=linprog(objective,A_ub=A,b_ub=b,bounds=[(0,1)]*m+[(None,None)]+[(0,None)]*n,method='highs')
 if not res.success:raise ValueError(res.message)
 assert np.all(res.x[:m]>=-1e-7) and np.all(res.x[:m]<=1+1e-7)
 h=np.clip(res.x[:m],0,1);assert np.abs(net)@h<=coverage_cap*np.abs(net).sum()+.01
 return h.tolist()
