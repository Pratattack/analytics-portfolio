"""Business-day booking queue simulation; no clinical decision-making."""
import math, random, statistics

def poisson(rng,lam):
    if lam<0:raise ValueError('Negative arrival rate')
    if lam==0:return 0
    threshold=math.exp(-lam);p=1.;k=0
    while p>threshold:k+=1;p*=rng.random()
    return k-1

def generate(config,seed,demand_factor=1.,absence_chance=.08):
    rng=random.Random(seed);requests=[];capacity=[]
    for day in range(config['calendar_days']):
        capacity.append(3 if rng.random()<absence_chance else 0)
        if day>=config['arrival_days']:continue
        seasonal=1+.08*math.sin(2*math.pi*day/60)
        count=poisson(rng,config['mean_daily_requests']*demand_factor*seasonal)
        for _ in range(count):
            urgent=rng.random()<config['urgent_fraction']
            requests.append(dict(request_id=len(requests),request_day=day,urgent=int(urgent),show_uniform=rng.random()))
    return requests,capacity

def simulate(config,policy,requests,absence):
    slots=config['base_slots']+policy['extra_slots'];horizon=config['calendar_days']
    if slots<policy['reserved'] or config['booking_window']<1:raise ValueError('Invalid capacity/window')
    calendar=[[] for _ in range(horizon)];public_usage=[0]*horizon;pending=[];records=[];offset=0
    for day in range(horizon):
        while offset<len(requests) and requests[offset]['request_day']==day:
            pending.append(dict(requests[offset]));offset+=1
        if policy['priority']:
            pending.sort(key=lambda r:(-r['urgent'],r['request_day'],r['request_id']))
        else:pending.sort(key=lambda r:(r['request_day'],r['request_id']))
        remaining=[]
        for r in pending:
            booked=None;booked_class=None
            for target in range(day,min(horizon,day+config['booking_window'])):
                available=max(0,slots-absence[target]);used=len(calendar[target]);reserved=min(available,policy['reserved'])
                released=policy['release_days']>=0 and target-day<=policy['release_days']
                used_public=public_usage[target];used_reserved=used-used_public
                if used>=available:continue
                if r['urgent'] and used_reserved<reserved:booked_class='reserved'
                elif used_public<available-reserved:booked_class='public'
                elif released and used_reserved<reserved:booked_class='reserved'
                else:continue
                booked=target;break
            if booked is None:remaining.append(r);continue
            wait=booked-r['request_day'];p_no=config['urgent_no_show'] if r['urgent'] else config['routine_no_show']
            record=dict(request_id=r['request_id'],request_day=r['request_day'],urgent=r['urgent'],appointment_day=booked,wait_days=wait,completed=int(r['show_uniform']>=p_no),in_cohort=int(config['warmup_days']<=r['request_day']<config['evaluation_end_day']),slot_class=booked_class)
            calendar[booked].append(record);records.append(record)
            if booked_class=='public':public_usage[booked]+=1
        pending=remaining
    # Unbooked requests remain in the denominator; do not hide right-censoring.
    for r in pending:
        records.append(dict(request_id=r['request_id'],request_day=r['request_day'],urgent=r['urgent'],appointment_day=-1,wait_days=-1,completed=0,in_cohort=int(config['warmup_days']<=r['request_day']<config['evaluation_end_day']),slot_class='none'))
    cohort=[r for r in records if r['in_cohort']]
    def within(flag,target):
        group=[r for r in cohort if r['urgent']==flag]
        return sum(0<=r['wait_days']<=target for r in group)/len(group) if group else 0.
    booked=[r for r in cohort if r['wait_days']>=0]
    eval_days=config['evaluation_end_day']-config['warmup_days']
    result=dict(requests=len(cohort),booked=len(booked),unbooked=len(cohort)-len(booked),completed=sum(r['completed'] for r in cohort),no_shows=sum(not r['completed'] for r in booked),mean_booked_wait=statistics.mean(r['wait_days'] for r in booked) if booked else 0.,urgent_service=within(1,config['urgent_wait_target']),routine_service=within(0,config['routine_wait_target']),incremental_capacity_cost=policy['extra_slots']*config['extra_slot_cost_usd']*eval_days+policy['setup_cost_usd'],scheduled_cohort_days=eval_days)
    # Capacity audit independently reconstructs all calendar occupancy.
    assert all(len(visits)<=max(0,slots-absence[d]) for d,visits in enumerate(calendar))
    assert all(public_usage[d]==sum(r['slot_class']=='public' for r in visits) for d,visits in enumerate(calendar))
    assert len(records)==len(requests)==len({r['request_id'] for r in records})
    return result,records
