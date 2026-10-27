from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parents[1]
NUMERIC=['revenue','cogs','ar','inventory','ap','cfo','capex','prior_ar','prior_inventory','prior_ap']
def analyze(df):
    x=df.copy()
    for c in NUMERIC:x[c]=pd.to_numeric(x[c],errors='raise')
    if x[['revenue','cogs']].le(0).any().any():raise ValueError('Revenue and COGS must be positive')
    if x[['ar','inventory','ap','prior_ar','prior_inventory','prior_ap']].lt(0).any().any():raise ValueError('Negative balance')
    x['avg_ar']=(x.ar+x.prior_ar)/2
    x['avg_inventory']=(x.inventory+x.prior_inventory)/2
    x['avg_ap']=(x.ap+x.prior_ap)/2
    x['dso']=365*x.avg_ar/x.revenue
    x['dio']=365*x.avg_inventory/x.cogs
    x['dpo']=365*x.avg_ap/x.cogs
    x['ccc']=x.dso+x.dio-x.dpo
    x['fcf']=x.cfo-x.capex
    x['fcf_margin']=x.fcf/x.revenue
    x['gross_margin']=(x.revenue-x.cogs)/x.revenue
    return x
def scenario(row,dso_days=0,dio_days=0,dpo_days=0,realization=1.):
    if any(v<0 for v in (dso_days,dio_days,dpo_days)) or not 0<=realization<=1:raise ValueError('Invalid scenario')
    return realization*(row.revenue/365*dso_days+row.cogs/365*(dio_days+dpo_days))
def scenario_detail(row,dso_days,dio_days,dpo_days,realization,implementation_cost_musd,annual_carry_rate):
    if implementation_cost_musd<0 or annual_carry_rate<0:raise ValueError('Invalid cost/rate')
    gross=scenario(row,dso_days,dio_days,dpo_days,realization)
    return dict(gross_release_musd=gross,implementation_cost_musd=implementation_cost_musd,net_first_year_liquidity_musd=gross-implementation_cost_musd,annual_financing_benefit_musd=gross*annual_carry_rate,net_first_year_value_musd=gross*annual_carry_rate-implementation_cost_musd)
ASSUMPTIONS=[('Conservative',1,.5,.5,.5,150,.04),('Base',2,1,1,.7,350,.05),('Stretch',3,2,2,.8,800,.06)]
def audit_snapshot(snapshot,audit):
    """Validate source values at full reported USD precision, not truncated integer millions."""
    if snapshot.ticker.duplicated().any():raise ValueError('Duplicate company')
    if audit.duplicated(['ticker','field']).any():raise ValueError('Duplicate XBRL field')
    if len(audit)!=len(snapshot)*len(NUMERIC):raise ValueError('XBRL audit incomplete')
    expected={(str(r.ticker),str(r.field)):int(r.value_usd) for r in audit.itertuples()}
    for row in snapshot.itertuples():
        for field in NUMERIC:
            key=(str(row.ticker),field)
            if key not in expected or round(float(getattr(row,field))*1e6)!=expected[key]:
                raise ValueError(f'XBRL audit mismatch: {key}')
    return True

if __name__=='__main__':
    raw=pd.read_csv(BASE/'data/firecrawl_snapshot.csv',dtype={'cik':str})
    audit_snapshot(raw,pd.read_csv(BASE/'data/xbrl_audit.csv'))
    data=analyze(raw)
    data.to_csv(BASE/'data/metrics.csv',index=False)
    apple=data.loc[data.ticker=='AAPL'].iloc[0]
    results=[]
    for label,dso,dio,dpo,fraction,cost,carry in ASSUMPTIONS:
        results.append({'scenario':label,'dso_reduction':dso,'dio_reduction':dio,'dpo_extension':dpo,'realization':fraction,'implementation_cost_musd':cost,'annual_carry_rate':carry,**scenario_detail(apple,dso,dio,dpo,fraction,cost,carry)})
    pd.DataFrame(results).to_csv(BASE/'data/scenarios.csv',index=False)
    print(data[['ticker','dso','dio','dpo','ccc','fcf','fcf_margin']].round(3).to_string(index=False))
    print(pd.DataFrame(results).round(2).to_string(index=False))
