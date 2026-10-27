import pandas as pd
from scripts.analysis import analyze,scenario
def test_metrics_identity():
    df=analyze(pd.DataFrame([dict(revenue=365,cogs=365,ar=10,prior_ar=10,inventory=20,prior_inventory=20,ap=30,prior_ap=30,cfo=100,capex=40)]))
    r=df.iloc[0]
    assert (r.dso,r.dio,r.dpo,r.ccc,r.fcf)==(10,20,30,0,60)
def test_scenario():
    assert scenario(pd.Series({'revenue':365,'cogs':365}),2,1,3,.5)==3
