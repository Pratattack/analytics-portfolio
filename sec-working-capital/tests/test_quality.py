from pathlib import Path
import pandas as pd
import pytest
from scripts.analysis import analyze,scenario,scenario_detail,audit_snapshot
ROOT=Path(__file__).resolve().parents[1]
RAW=pd.read_csv(ROOT/'data/firecrawl_snapshot.csv',dtype={'cik':str})
AUDIT=pd.read_csv(ROOT/'data/xbrl_audit.csv')
def test_audit_complete():assert audit_snapshot(RAW,AUDIT)
def test_exact_source_count():assert len(AUDIT)==30 and set(AUDIT.ticker)=={'AAPL','DELL','MSFT'}
def test_dell_capex_corrected():assert int(RAW.loc[RAW.ticker=='DELL','capex'].iloc[0])==2633
def test_unique_sources():assert not AUDIT.duplicated(['ticker','field']).any()
def test_expected_accession():assert AUDIT.groupby('ticker').accession.nunique().eq(1).all()
def test_python_derived_identity():
    x=analyze(RAW)
    assert (x.ccc-(x.dso+x.dio-x.dpo)).abs().max()<1e-10
    assert (x.fcf-(x.cfo-x.capex)).abs().max()<1e-10
def test_wrong_source_caught():
    bad=RAW.copy();bad.loc[bad.ticker=='DELL','capex']=2630
    with pytest.raises(ValueError):audit_snapshot(bad,AUDIT)
@pytest.mark.parametrize('realization',[0,.5,1])
def test_realization_monotonic(realization):
    a=analyze(RAW).query('ticker=="AAPL"').iloc[0]
    assert scenario(a,1,1,1,realization)==pytest.approx(realization*scenario(a,1,1,1,1))
def test_scenario_investment_case():
    a=analyze(RAW).query('ticker=="AAPL"').iloc[0]
    s=scenario_detail(a,2,1,1,.7,350,.05)
    assert s['net_first_year_liquidity_musd']==pytest.approx(s['gross_release_musd']-350)
    assert s['net_first_year_value_musd']==pytest.approx(s['gross_release_musd']*.05-350)
@pytest.mark.parametrize('kwargs',[{'dso_days':-1},{'realization':1.1}])
def test_invalid_scenarios(kwargs):
    a=analyze(RAW).iloc[0]
    with pytest.raises(ValueError):scenario(a,**kwargs)
