"""Exact, finite-scenario, multiple-choice resilience capital allocation.

Standard library only. NPV is modeled social value, not utility cash profit.
"""
import itertools
import math


def validate(config):
    if config['budget_musd'] < 0 or config['crew_limit'] < 0:
        raise ValueError('Budget and crew limits must be nonnegative')
    if config['discount_rate'] < 0 or config['life_years'] < 1:
        raise ValueError('Invalid discount rate or asset life')
    if config['value_per_customer_hour_usd'] < 0 or config['budget_reserve_factor'] < 1:
        raise ValueError('Invalid outage valuation or budget reserve')
    if len({d['state'] for d in config['districts']}) != len(config['districts']):
        raise ValueError('Duplicate district')
    if not config['scenarios'] or not config['districts']:
        raise ValueError('At least one district and scenario required')
    if config['minimum_critical_districts'] < 0:
        raise ValueError('Invalid critical-district floor')
    for d in config['districts']:
        if d['customers'] <= 0 or d['cost_factor'] <= 0:
            raise ValueError('Invalid district size/cost')
    for p in config['interventions']:
        if p['capex_musd'] <= 0 or p['crew'] < 0 or p['annual_opex_musd'] < 0:
            raise ValueError('Invalid intervention cost')
        if not all(0 <= p[k] <= 1 for k in ['normal_reduction', 'event_reduction']):
            raise ValueError('Effectiveness must lie in [0,1]')
    for s in config['scenarios']:
        if not 0 <= s['efficacy'] <= 1 or s['capex_factor'] <= 0:
            raise ValueError('Invalid scenario efficacy or cost')
        if s['capex_factor'] > config['budget_reserve_factor']:
            raise ValueError('Scenario cost exceeds budget reserve assumption')
        if s['event_factor'] < 0 or s['normal_factor'] < 0 or s['delay_years'] < 0:
            raise ValueError('Invalid scenario exposure or delay')


def intervention_value(district, option, scenario, benchmark, config):
    """USD millions, discounted years 1..life; zero annual benefit before service.

    All-event minus no-major-event SAIDI is an analytical contrast, not a
    physical cause decomposition; both are reported-system indices.
    """
    y = str(scenario['year'])
    routine = benchmark['normal_'+y] * scenario['normal_factor']
    event_proxy = max(0.0, benchmark['all_'+y] - benchmark['normal_'+y]) * scenario['event_factor']
    minutes = (routine*option['normal_reduction'] + event_proxy*option['event_reduction']) * scenario['efficacy']
    hours = minutes*district['customers']/60
    annual_benefit = hours*config['value_per_customer_hour_usd']*scenario.get('value_factor',1)/1e6
    annual_opex = option['annual_opex_musd']*district['cost_factor']
    factor = sum((1+config['discount_rate'])**(-t) for t in range(1,config['life_years']+1) if t > scenario['delay_years'])
    capex = option['capex_musd']*district['cost_factor']*scenario['capex_factor']
    return dict(npv_musd=(annual_benefit-annual_opex)*factor-capex,
                annual_customer_hours_avoided=hours, annual_benefit_musd=annual_benefit,
                annual_opex_musd=annual_opex, capex_musd=capex)


def build_options(config, benchmarks):
    validate(config)
    groups=[]
    for district in config['districts']:
        choices=[dict(state=district['state'], intervention='none', reserve_musd=0., crew=0, critical=0, values=[0.]*len(config['scenarios']))]
        for option in config['interventions']:
            values=[intervention_value(district,option,s,benchmarks[district['state']],config)['npv_musd'] for s in config['scenarios']]
            choices.append(dict(state=district['state'],intervention=option['name'],reserve_musd=round(option['capex_musd']*district['cost_factor']*config['budget_reserve_factor'],6),crew=option['crew'],critical=int(district['critical']),values=values))
        groups.append(choices)
    return groups


def evaluate(plan):
    return dict(reserve_musd=sum(p['reserve_musd'] for p in plan),
                crew=sum(p['crew'] for p in plan),critical=sum(p['critical'] for p in plan),
                values=[sum(p['values'][s] for p in plan) for s in range(len(plan[0]['values']))])


def feasible(totals, config, budget=None):
    return (totals['reserve_musd'] <= (config['budget_musd'] if budget is None else budget)+1e-8
            and totals['crew'] <= config['crew_limit']
            and totals['critical'] >= config['minimum_critical_districts'])


def solve(groups, config, budget=None, objective='robust', scenario_index=None):
    """Enumerate every multiple-choice plan, proving the finite-model optimum.

    Deterministic tie break: score, lower reserve, fewer crews, earlier product.
    Complexity O((K+1)^D * D * S); 3^10=59,049 choices in this case.
    """
    if objective not in ['robust','equal_weight','scenario']:
        raise ValueError('Unknown objective')
    if objective=='scenario' and scenario_index is None:
        raise ValueError('scenario_index required')
    best=None; rank=None; count=0; feasible_count=0
    for plan in itertools.product(*groups):
        count+=1
        totals=evaluate(plan)
        if not feasible(totals,config,budget): continue
        feasible_count+=1
        values=totals['values']
        score=min(values) if objective=='robust' else (sum(values)/len(values) if objective=='equal_weight' else values[scenario_index])
        candidate=(round(score,10),-totals['reserve_musd'],-totals['crew'])
        if rank is None or candidate>rank:
            rank=candidate
            best=dict(plan=list(plan),totals=totals,score=score)
    if best is None: raise ValueError('No feasible allocation under constraints')
    best.update(enumerated=count,feasible_count=feasible_count)
    return best


def greedy(groups,config):
    # Enforce the critical floor first, then add options by equal-weight NPV/reserve.
    selected=[g[0] for g in groups]
    options=sorted([(i,p) for i,g in enumerate(groups) for p in g[1:]],key=lambda ip:sum(ip[1]['values'])/len(ip[1]['values'])/ip[1]['reserve_musd'],reverse=True)
    for phase in ['critical','all']:
        for i,p in options:
            if selected[i]['intervention']!='none': continue
            if phase=='critical' and (not p['critical'] or sum(x['critical'] for x in selected)>=config['minimum_critical_districts']): continue
            if phase=='all' and sum(p['values'])<=0: continue
            proposed=selected.copy(); proposed[i]=p; t=evaluate(proposed)
            if t['reserve_musd']<=config['budget_musd']+1e-8 and t['crew']<=config['crew_limit']:
                selected=proposed
    t=evaluate(selected)
    return dict(plan=selected,totals=t,score=min(t['values']),feasible=feasible(t,config))


def independent_equal_weight_dp(groups,config):
    """Independent scalar DP oracle using integer micro-million budget units.

    State: (budget, crew, critical count capped at floor), value: best total score.
    No plan enumeration or solve/evaluate functions used here.
    """
    floor=config['minimum_critical_districts']; states={(0,0,0):0.}
    limit=round(config['budget_musd']*1e6)
    for group in groups:
        next_states={}
        for (cost,crew,critical),score in states.items():
            for p in group:
                nc=cost+round(p['reserve_musd']*1e6); nt=crew+p['crew']; nk=min(floor,critical+p['critical'])
                if nc>limit or nt>config['crew_limit']: continue
                key=(nc,nt,nk); v=score+sum(p['values'])/len(p['values'])
                next_states[key]=max(v,next_states.get(key,-math.inf))
        states=next_states
    return max(v for (cost,crew,k),v in states.items() if k>=floor)
