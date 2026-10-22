"""Conditional decision functions. Scenario inputs are NOT observations or forecasts."""
import math

def check(values,bounds):
 for k,(lo,hi) in bounds.items():
  v=values[k]
  if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError(f'{k} must be finite and between {lo} and {hi}')

def land_option(k,d,value_ratio=1.05,up=1.25,down=.75,p=.5,rate=.1,extension=.02,refund=0):
 check(locals(),{'k':(1,1e14),'d':(0,1e14),'value_ratio':(0,3),'up':(1,2),'down':(0,1),'p':(0,1),'rate':(0,.5),'extension':(0,.5),'refund':(0,1)})
 # Deposit is sunk. Refundable recovery is an assumed alternative payoff, not a second acquisition payment.
 v=k*value_ratio;a=d*refund;now=max(v-k,a);wait=(p*max(v*up-k,a)+(1-p)*max(v*down-k,a))/(1+rate)-extension*k
 return {'exercise_now':v-k,'abandon_now':a,'best_now':now,'wait':wait,'wait_advantage':wait-now,'max_extension_rate':((p*max(v*up-k,a)+(1-p)*max(v*down-k,a))/(1+rate)-now)/k,'action':'wait' if wait>now+1e-6 else ('exercise' if v-k>a+1e-6 else 'abandon'),'exercise_threshold_ratio':1+a/k}

def recovery(r,rr,re,oi,cost_growth=0,recovery_growth=0,budget=0,target_margin=.15):
 check(locals(),{'r':(1,1e14),'rr':(1,1e14),'re':(0,1e14),'oi':(-1e14,1e14),'cost_growth':(-.5,.5),'recovery_growth':(-.5,.5),'budget':(0,1e12),'target_margin':(0,1)})
 b=r-rr
 if b<=0:raise ValueError('Revenue less reimbursements must be positive')
 p=oi-rr+re;scenario=p+rr*(1+recovery_growth)-re*(1+cost_growth)-budget
 required=(target_margin*b+budget-p+re*(1+cost_growth))/rr-1
 return {'net_revenue':b,'profit_ex_recovery':p,'recovery_balance':rr-re,'reported_margin':oi/r,'ex_recovery_margin':p/b,'scenario_op_income':scenario,'scenario_margin':scenario/b,'required_recovery_growth':required,'budget_headroom':p+rr*(1+recovery_growth)-re*(1+cost_growth)-target_margin*b,'gate':'meets assumed income floor' if scenario>=target_margin*b-1e-6 else 'below assumed income floor'}
