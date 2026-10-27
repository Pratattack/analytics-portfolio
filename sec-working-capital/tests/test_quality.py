import pandas as pd
import pytest
from pathlib import Path
from scripts.analysis import analyze, scenario
DATA=Path(__file__).resolve().parents[1]/'data/firecrawl_snapshot.csv'

def test_input_is_complete_and_unique():
    df=pd.read_csv(DATA,dtype={'cik':str})
    assert set(df.ticker)=={'AAPL','DELL','MSFT'}
    assert not df.ticker.duplicated().any()
    assert df.cik.str.len().eq(10).all()
    assert df.fiscal_end.notna().all()

def test_accounting_math():
    df=analyze(pd.read_csv(DATA))
    assert (df.ccc.round(8)==(df.dso+df.dio-df.dpo).round(8)).all()
    assert (df.fcf==df.cfo-df.capex).all()
    assert df.loc[df.ticker=='AAPL','ccc'].iloc[0]<0

@pytest.mark.parametrize('days,realization',[(1,0),(1,1),(0,1)])
def test_scenario_bounds(days,realization):
    row=analyze(pd.read_csv(DATA)).iloc[0]
    value=scenario(row,days,days,days,realization)
    assert value>=0
    if days==0 or realization==0: assert value==0

def test_scenario_rejects_invalid_inputs():
    row=analyze(pd.read_csv(DATA)).iloc[0]
    with pytest.raises(AssertionError): scenario(row,-1,0,0,1)
    with pytest.raises(AssertionError): scenario(row,0,0,0,1.2)
