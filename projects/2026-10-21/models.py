"""Auditable finance models. USD throughout; no investment recommendations."""
import math
import numpy as np

def ridge_fit(X,y,penalty):
 X=np.asarray(X,float);y=np.asarray(y,float);p=np.eye(X.shape[1])*penalty;p[0,0]=0
 return np.linalg.solve(X.T@X+p,X.T@y)

def inventory_features(rows,i):
 a,b,c=rows[i],rows[i-1],rows[i-4]
 angle=2*math.pi*(int(a['end'][5:7])-1)/12
 return [1,math.log(a['inventory']/b['inventory']),math.log(a['cost']/b['cost']),math.log(a['inventory']/c['inventory']),math.sin(angle),math.cos(angle)]

def inventory_scenario(base,forecast,upper,annual_carry_pct,buffer_pct):
 vals=[base,forecast,upper,annual_carry_pct,buffer_pct]
 if not all(math.isfinite(v) for v in vals) or min(base,forecast,upper)<=0 or not (0<=annual_carry_pct<=40 and 0<=buffer_pct<=50):raise ValueError('Invalid scenario inputs')
 planning=max(forecast,upper)*(1+buffer_pct/100)
 return {'planning_inventory':planning,'incremental_balance':planning-base,'quarterly_carry_cost':planning*annual_carry_pct/400}

def rail_scenario(cfo,capex,dividends,buybacks,cfo_shock_pct,capex_pct):
 if not all(math.isfinite(v) for v in [cfo,capex,dividends,buybacks,cfo_shock_pct,capex_pct]) or cfo<=0 or min(capex,dividends,buybacks)<0 or not (-60<=cfo_shock_pct<=20 and 80<=capex_pct<=150):raise ValueError('Invalid scenario inputs')
 cash=cfo*(1+cfo_shock_pct/100);reinvestment=capex*capex_pct/100
 capacity=max(0,cash-reinvestment-dividends)
 return {'buyback_capacity':capacity,'distribution_gap':cash-reinvestment-dividends-buybacks,'capex_budget':reinvestment}

def fixed_asset_return(op_income,previous,current,tax_pct):
 if min(previous,current)<=0 or not 0<=tax_pct<=50:raise ValueError('Invalid asset-return inputs')
 return op_income*(1-tax_pct/100)/((previous+current)/2)
