"""Auditable loss-development and refinancing models. No investment recommendation."""
import math
from statistics import median


def finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be finite')
    return float(value)


def chain_ladder(rows, cutoff, method='volume', tail=1.0, omit=None):
    """Cumulative paid data {(accident_year, valuation_year): value}; no data beyond cutoff."""
    if method not in ['volume', 'median']: raise ValueError('Unknown development method')
    if not 1 <= finite(tail, 'Tail factor') <= 1.5: raise ValueError('Tail factor outside [1, 1.5]')
    data = {(ay, vy): finite(v, 'Cumulative paid') for (ay, vy), v in rows.items() if vy <= cutoff}
    if any(v < 0 or ay > vy for (ay, vy), v in data.items()): raise ValueError('Invalid paid triangle')
    years = sorted({ay for ay, _ in data})
    if len(years) < 5: raise ValueError('At least five accident years are required')
    max_age = max(vy - ay for ay, vy in data)
    factors, support = {}, {}
    for age in range(max_age):
        pairs = [(data[(ay, ay + age)], data[(ay, ay + age + 1)]) for ay in years
                 if ay != omit and (ay, ay + age) in data and (ay, ay + age + 1) in data
                 and data[(ay, ay + age)] > 0]
        if not pairs: raise ValueError(f'No development support at age {age}')
        if any(b < a for a, b in pairs): raise ValueError('Decreasing cumulative paid violates selected model gate')
        factors[age] = sum(b for a, b in pairs) / sum(a for a, b in pairs) if method == 'volume' else median(b/a for a, b in pairs)
        support[age] = len(pairs)
    estimates = []
    for ay in years:
        observed = sorted((vy, v) for (a, vy), v in data.items() if a == ay)
        vy, latest = observed[-1]
        factor = math.prod(factors[age] for age in range(vy-ay, max_age)) * tail
        ultimate = latest * factor
        next_paid = latest * factors[vy-ay] if vy-ay < max_age else latest
        estimates.append(dict(accident_year=ay, valuation_year=vy, latest_paid=latest,
                              ultimate=ultimate, unpaid=ultimate-latest, next_paid=next_paid))
    return dict(factors=factors, support=support, estimates=estimates,
                unpaid=sum(r['unpaid'] for r in estimates), ultimate=sum(r['ultimate'] for r in estimates))


def cash_path(record, rollover=1.0, cfo_decline=0.0, spread_bps=0.0,
              maintenance_share=.10, issuance_fee=.01, cash_floor_share=.10, recovery_after=5):
    """Five annual periods, fixed disclosed maturities; incremental spread costs, no new maturities."""
    assumptions = dict(rollover=rollover, cfo_decline=cfo_decline, spread_bps=spread_bps,
                       maintenance_share=maintenance_share, issuance_fee=issuance_fee, cash_floor_share=cash_floor_share)
    for k, v in assumptions.items(): finite(v, k)
    if not 0 <= rollover <= 1 or not 0 <= cfo_decline <= .6 or not 0 <= spread_bps <= 1000:
        raise ValueError('Rollover, CFO decline or spread outside supported range')
    if not 0 <= maintenance_share <= .5 or not 0 <= issuance_fee <= .1 or not 0 <= cash_floor_share <= 1:
        raise ValueError('Maintenance, fee or cash floor outside supported range')
    if isinstance(recovery_after,bool) or not isinstance(recovery_after,int) or not 1 <= recovery_after <= 5:
        raise ValueError('Shock duration must be an integer from one to five years')
    cfo, distribution, opening = (finite(record[k], k) for k in ['cfo', 'distributions', 'cash'])
    maturities = record['maturities']
    if cfo <= 0 or distribution < 0 or opening < 0 or len(maturities) != 5 or any(finite(m, 'Maturity') < 0 for m in maturities):
        raise ValueError('Invalid financial inputs')
    floor = cash_floor_share*cfo
    cash, outstanding_refinanced, rows = opening, 0.0, []
    for year, maturity in enumerate(maturities, 1):
        operating = cfo*(1-(cfo_decline if year<=recovery_after else 0))-distribution-maintenance_share*cfo
        incremental_interest = (outstanding_refinanced + .5*rollover*maturity)*spread_bps/10000
        fee = rollover*maturity*issuance_fee
        principal_cash = (1-rollover)*maturity
        cash += operating-principal_cash-fee-incremental_interest
        outstanding_refinanced += rollover*maturity
        rows.append(dict(year=2025+year, maturity=maturity, operating_cash_after_distribution_and_assumed_capex=operating,
                         principal_cash=principal_cash, incremental_interest=incremental_interest,
                         issuance_fee=fee, closing_cash=cash, cash_floor=floor, shortfall=max(0, floor-cash)))
    return rows


def required_rollover(record, **assumptions):
    """Exact intersection of five affine cash constraints in the common rollover fraction."""
    zero = cash_path(record, rollover=0, **assumptions)
    one = cash_path(record, rollover=1, **assumptions)
    lower, upper = 0.0, 1.0
    binding = None
    for a, b in zip(zero, one):
        slope = b['closing_cash']-a['closing_cash']
        gap = a['cash_floor']-a['closing_cash']
        if abs(slope) < 1e-8:
            if gap > 1e-6: return dict(feasible=False, minimum_rollover=None, binding_year=a['year'], required_liquidity=max(r['shortfall'] for r in one))
        elif slope > 0:
            threshold = gap/slope
            if threshold > lower: lower, binding = threshold, a['year']
        else: upper = min(upper, gap/slope)
    feasible = lower <= upper+1e-10 and lower <= 1+1e-10 and upper >= 0
    return dict(feasible=feasible, minimum_rollover=max(0, min(1, lower)) if feasible else None,
                binding_year=binding, required_liquidity=max(r['shortfall'] for r in one),
                unconstrained_lower_bound=lower)
