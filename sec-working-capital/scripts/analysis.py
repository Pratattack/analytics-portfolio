from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parents[1]
def analyze(df):
    x=df.copy()
    for c in ['revenue','cogs','ar','inventory','ap','cfo','capex','prior_ar','prior_inventory','prior_ap']:
        x[c]=pd.to_numeric(x[c],errors='raise')
    assert (x[['revenue','cogs']]>0).all().all()
    assert (x[['ar','inventory','ap','prior_ar','prior_inventory','prior_ap']]>=0).all().all()
    x['avg_ar']=(x.ar+x.prior_ar)/2
    x['avg_inventory']=(x.inventory+x.prior_inventory)/2
    x['avg_ap']=(x.ap+x.prior_ap)/2
    x['dso']=365*x.avg_ar/x.revenue
    x['dio']=365*x.avg_inventory/x.cogs
    x['dpo']=365*x.avg_ap/x.cogs
    x['ccc']=x.dso+x.dio-x.dpo
    x['fcf']=x.cfo-x.capex
    return x
def scenario(row,dso_days=0,dio_days=0,dpo_days=0,realization=1.0):
    assert all(v>=0 for v in (dso_days,dio_days,dpo_days))
    assert 0<=realization<=1
    return realization*(row.revenue/365*dso_days+row.cogs/365*(dio_days+dpo_days))
if __name__=='__main__':
    df=analyze(pd.read_csv(BASE/'data/firecrawl_snapshot.csv',dtype={'cik':str}))
    df.to_csv(BASE/'data/metrics.csv',index=False)
    print(df[['ticker','dso','dio','dpo','ccc','fcf']].round(2).to_string(index=False))
