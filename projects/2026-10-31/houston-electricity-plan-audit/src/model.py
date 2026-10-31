"""Contract arithmetic, not a behavioral or electricity demand forecast."""
from decimal import Decimal
from math import isfinite

COMMON_DELIVERY = {'cents': 6.5333, 'dollars': 4.9, 'as_of': '2026-10-04'}

def dec(x):
    return Decimal(str(x))

def bill(plan, kwh, days=30, normalized=False):
    if not isfinite(float(kwh)) or kwh <= 0 or not isfinite(float(days)) or not 1 <= days <= 31:
        raise ValueError('Usage must be positive and days must be between 1 and 31')
    q, d = dec(kwh), dec(days)
    delivery = COMMON_DELIVERY if normalized else {'cents':plan['delivery_cents'],'dollars':plan['delivery_dollars']}
    # Payless explicitly prorates the fixed delivery charge for shorter cycles.
    fixed_delivery = dec(delivery['dollars']) * (min(d/30, Decimal(1)) if plan['prepaid'] else 1)
    credit = Decimal(0)
    if plan['credit_rule'] == 'gte' and q >= dec(plan['credit_threshold']):
        credit = dec(plan['credit_dollars'])
    elif plan['credit_rule'] == 'lte' and q <= dec(plan['credit_threshold']):
        credit = dec(plan['credit_dollars']) * min(d/30, Decimal(1))
    total = q*(dec(plan['energy_cents'])+dec(delivery['cents']))/100 + dec(plan['base_dollars']) + d*dec(plan['daily_dollars']) + fixed_delivery - credit
    return {'total':float(total),'credit':float(credit),'effective_cents':float(total/q*100)}

def twelve_cycles(plan, usage):
    if len(usage)!=12 or plan['term_months']<12:
        raise ValueError('Requires 12 cycles and a contract covering the horizon')
    monthly=[bill(plan,q,normalized=True) for q in usage]
    return {'total':sum(x['total'] for x in monthly),'credits':sum(x['credit'] for x in monthly),'credit_cycles':sum(x['credit']>0 for x in monthly)}

def exit_fee(plan, elapsed_months):
    if not isinstance(elapsed_months,int) or elapsed_months<0:
        raise ValueError('Elapsed months must be a nonnegative integer')
    remaining=max(0,plan['term_months']-elapsed_months)
    return 0 if remaining==0 else plan['termination_flat']+remaining*plan['termination_per_remaining_month']
