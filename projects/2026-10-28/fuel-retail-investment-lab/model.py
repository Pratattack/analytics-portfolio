"""Scenario underwriting, not an appraisal or a statement of actual project returns.

All costs, margins, financing and ramp assumptions are explicit and editable.
No probabilities are inferred from the source risk matrix.
"""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent
REPORT=json.loads((ROOT/'data/report_estimates.json').read_text())
DEFAULT=json.loads((ROOT/'data/default_assumptions.json').read_text())

def payment(principal,annual_rate,years):
    if principal==0:return 0.
    months=years*12
    return principal/months if annual_rate==0 else principal*(annual_rate/12)/(1-(1+annual_rate/12)**(-months))

def validate(c):
    if set(c)!=set(DEFAULT):raise ValueError('Assumption keys do not match schema')
    if c['report_scenario'] not in REPORT['scenarios']:raise ValueError('Unknown sales case')
    if c['scope'] not in ['core','full']:raise ValueError('Unknown scope')
    if c['fuel_source'] not in ['report','traffic']:raise ValueError('Unknown fuel volume method')
    for k,v in c.items():
        if isinstance(DEFAULT[k],(int,float)):
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:raise ValueError('Invalid '+k)
    for k in ['eligible_traffic_share','capture_rate','store_margin','deli_margin','pizza_margin','lottery_commission','nonfuel_card_fee','payroll_load','contingency_rate','loan_to_cost','annual_interest_rate','loan_fee_rate','ramp_start','wash_margin']:
        if c[k]>1:raise ValueError('Fraction outside [0,1]: '+k)
    if c['lottery_commission']<.05:raise ValueError('Lottery commission is below the verified 5% minimum')
    if c['loan_to_cost']>.95:raise ValueError('Debt share exceeds supported scenario range')
    for k in ['construction_months','permit_delay_months','ramp_months','amortization_years']:
        if c[k]!=int(c[k]):raise ValueError('Whole number required: '+k)
    if not 1<=c['construction_months']<=60 or not 0<=c['permit_delay_months']<=36 or not 1<=c['ramp_months']<=36:raise ValueError('Unsupported timeline')
    if not 1<=c['amortization_years']<=40:raise ValueError('Unsupported loan term')
    if not 0<c['target_dscr']<=5:raise ValueError('Invalid coverage threshold')
    if c['hours_open_per_day']>24 or c['average_staff_on_duty']>20:raise ValueError('Unsupported staffing')
    if c['sales_multiplier']>5 or c['net_fuel_margin']>5:raise ValueError('Unsupported sales or margin')
    if c['loan_to_cost']==0 and c['target_dscr']<=0:raise ValueError('Invalid target')
    return c

def steady(c):
    validate(c)
    s=REPORT['scenarios'][c['report_scenario']]
    scale=c['sales_multiplier'];wash=c['scope']=='full';days=365/12
    gallons=(s['fuel_gallons'] if c['fuel_source']=='report' else c['aadt']*c['eligible_traffic_share']*c['capture_rate']*c['gallons_per_transaction']*days)*scale
    store=s['store_sales']*scale;deli=s['deli_sales']*scale;pizza=s['pizza_sales']*scale;lottery=s['lottery_ticket_sales']*scale
    wash_sales=c['wash_sales_monthly']*scale if wash else 0.
    fuel=gallons*c['net_fuel_margin'];lotto=lottery*c['lottery_commission']
    store_gp=store*c['store_margin'];deli_gp=deli*c['deli_margin'];pizza_gp=pizza*c['pizza_margin'];wash_gp=wash_sales*c['wash_margin']
    nonfuel=store+deli+pizza+lottery+wash_sales;retained=nonfuel-lottery+lotto
    cogs=store*(1-c['store_margin'])+deli*(1-c['deli_margin'])+pizza*(1-c['pizza_margin'])+wash_sales*(1-c['wash_margin'])
    fees=(store+deli+pizza+wash_sales)*c['nonfuel_card_fee']
    loaded_wage=c['hourly_wage']*(1+c['payroll_load'])
    labor=c['hours_open_per_day']*days*c['average_staff_on_duty']*loaded_wage+(c['wash_extra_labor_hours_monthly']*loaded_wage if wash else 0)
    maintenance=c['maintenance_reserve_monthly']+(c['wash_maintenance_monthly'] if wash else 0)
    contribution=fuel+lotto+store_gp+deli_gp+pizza_gp+wash_gp-fees
    fixed=labor+c['fixed_opex_monthly']+maintenance
    cfads=contribution-fixed
    hard=c['hard_cost']+(c['wash_hard_cost'] if wash else 0)
    contingency=hard*c['contingency_rate'];budget=c['land_cost']+c['soft_cost']+hard+contingency
    loan=budget*c['loan_to_cost'];debt=payment(loan,c['annual_interest_rate'],c['amortization_years'])
    dscr=None if debt==0 else cfads/debt
    maximum_loan=max(0,cfads/c['target_dscr'])/payment(1.,c['annual_interest_rate'],c['amortization_years'])
    max_eligible=None if c['loan_to_cost']==0 else maximum_loan/c['loan_to_cost']
    nonfuel_contribution=contribution-fuel
    required_fuel=max(0,fixed+c['target_dscr']*debt-nonfuel_contribution)
    breakeven_gallons=(required_fuel/c['net_fuel_margin']) if c['net_fuel_margin']>0 else (0. if required_fuel==0 else None)
    min_sales_scale=None if contribution<=0 else (fixed+c['target_dscr']*debt)/contribution*scale
    max_hard=None if max_eligible is None else (max_eligible-c['land_cost']-c['soft_cost'])/(1+c['contingency_rate'])-(c['wash_hard_cost'] if wash else 0)
    # Cash reconciliation: face-value receipts are not treated as retained retailer income.
    bridge=[('Reported nonfuel receipts',nonfuel),('Lottery transferred',-(lottery-lotto)),('Merchandise / wash cost',-cogs),('Net fuel contribution',fuel),('Nonfuel card fees',-fees),('Loaded labor',-labor),('Other fixed costs',-c['fixed_opex_monthly']),('Maintenance reserve',-maintenance),('Cash before debt',cfads)]
    assert abs(sum(v for _,v in bridge[:-1])-cfads)<1e-7
    return dict(gallons=gallons,nonfuel_receipts=nonfuel,lottery_ticket_sales=lottery,lottery_commission=lotto,retained_nonfuel_receipts=retained,merchandise_cogs=cogs,card_fees=fees,net_fuel_contribution=fuel,store_contribution=store_gp,deli_contribution=deli_gp,pizza_contribution=pizza_gp,wash_contribution=wash_gp,loaded_labor=labor,fixed_costs=c['fixed_opex_monthly'],maintenance_reserve=maintenance,contribution=contribution,fixed_cash_cost=fixed,cfads=cfads,hard_budget=hard,contingency=contingency,eligible_budget=budget,loan=loan,monthly_debt_service=debt,dscr=dscr,maximum_supported_loan=maximum_loan,maximum_supported_eligible_budget=max_eligible,maximum_core_hard_cost=max_hard,required_fuel_gallons=breakeven_gallons,required_sales_multiplier=min_sales_scale,bridge=bridge,illustrative_coverage_pass=(cfads>=0 if debt==0 else dscr>=c['target_dscr']))

def evaluate(c):
    c=dict(validate(dict(c)));s=steady(c);period=c['construction_months']+c['permit_delay_months'];rows=[]
    upfront=c['land_cost']+c['soft_cost'];loan_balance=upfront*c['loan_to_cost'];loan_fee=s['loan']*c['loan_fee_rate']
    sponsor=upfront-loan_balance+loan_fee
    rows.append(dict(month=0,phase='closing',ramp=0,capex=upfront,loan_draw=loan_balance,loan_balance=loan_balance,construction_interest=0,carry=0,working_capital=0,cfads=0,debt_service=0,operating_cash_after_debt=0,sponsor_funding=sponsor,cumulative_sponsor_funding=sponsor))
    construction_spend=s['hard_budget']+s['contingency'];development_interest=0;carry_total=0;opening_equity=None
    for month in range(1,period+1):
        spend=construction_spend/c['construction_months'] if month>c['permit_delay_months'] else 0
        draw=spend*c['loan_to_cost'];interest=(loan_balance+draw/2)*c['annual_interest_rate']/12
        loan_balance+=draw;carry=c['preopening_carry_monthly'];funding=spend-draw+interest+carry
        development_interest+=interest;carry_total+=carry;sponsor+=funding
        rows.append(dict(month=month,phase='delay' if month<=c['permit_delay_months'] else 'construction',ramp=0,capex=spend,loan_draw=draw,loan_balance=loan_balance,construction_interest=interest,carry=carry,working_capital=0,cfads=0,debt_service=0,operating_cash_after_debt=0,sponsor_funding=funding,cumulative_sponsor_funding=sponsor))
    assert abs(loan_balance-s['loan'])<1e-6
    # Working capital is funded once, at opening. It is not counted as an expense.
    sponsor+=c['working_capital'];opening_equity=sponsor;operating_cumulative=0;lowest_operating=0;year1_cfads=0;year1_debt=0
    for opmonth in range(1,37):
        ramp=1. if c['ramp_months']==1 else c['ramp_start']+(1-c['ramp_start'])*min(opmonth-1,c['ramp_months']-1)/(c['ramp_months']-1)
        cfads=s['contribution']*ramp-s['fixed_cash_cost'];interest=loan_balance*c['annual_interest_rate']/12
        principal=min(loan_balance,max(0,s['monthly_debt_service']-interest));debt=interest+principal;loan_balance=max(0,loan_balance-principal)
        free=cfads-debt;operating_cumulative+=free;lowest_operating=min(lowest_operating,operating_cumulative)
        if opmonth<=12:year1_cfads+=cfads;year1_debt+=debt
        working=c['working_capital'] if opmonth==1 else 0.
        rows.append(dict(month=period+opmonth,operating_month=opmonth,phase='operations',ramp=ramp,capex=0,loan_draw=0,loan_balance=loan_balance,construction_interest=0,carry=0,working_capital=working,cfads=cfads,debt_service=debt,operating_cash_after_debt=free,sponsor_funding=working-free,cumulative_sponsor_funding=opening_equity-operating_cumulative))
    peak_need=opening_equity-lowest_operating
    return dict(config=c,steady=s,months=rows,development_interest=development_interest,development_carry=carry_total,loan_fee=loan_fee,equity_at_opening=opening_equity,peak_sponsor_funding_36m=peak_need,operating_deficit_funding_36m=-lowest_operating,year1_cfads=year1_cfads,year1_debt_service=year1_debt,year1_dscr=None if year1_debt==0 else year1_cfads/year1_debt,opening_month=period+1,overall_decision='Not underwritten: site-specific evidence gates remain unverified')

if __name__=='__main__':
    r=evaluate(DEFAULT);print(json.dumps({k:v for k,v in r.items() if k not in ['months','config']},indent=2,allow_nan=False))
