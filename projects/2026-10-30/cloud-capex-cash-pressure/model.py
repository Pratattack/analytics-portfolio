from pathlib import Path
import pandas as pd,numpy as np,json
ROOT=Path(__file__).parent
TAGS={'cfo':'NetCashProvidedByUsedInOperatingActivities','capex':'PaymentsToAcquirePropertyPlantAndEquipment'}
def paired(facts,symbol,start,end,accession=None):
 by={}
 for metric,tag in TAGS.items():
  rows=facts[symbol]['facts'][tag]['units']['USD'];candidates={}
  for x in rows:
   if x.get('start')!=start or x.get('end')!=end or x.get('filed','9999')>'2026-10-30' or x.get('form') not in ['10-K','10-Q'] or (accession and x['accn']!=accession):continue
   if not accession and pd.Timestamp(x['filed'])>pd.Timestamp(end)+pd.Timedelta(days=120):continue
   key=x['accn'];candidates.setdefault(key,[]).append(x)
  by[metric]=candidates
 common=set(by['cfo'])&set(by['capex'])
 if not common:raise ValueError(f'No paired filing {symbol} {start} {end}')
 acc=max(common,key=lambda a:(by['cfo'][a][0]['filed'],a));answer={}
 for metric in TAGS:
  rows=by[metric][acc];assert len({x['val'] for x in rows})==1,'Conflicting same-period source facts';answer[metric]=rows[0]
 return answer

def build_panel(facts):
 rows=[];lineage=[];exceptions=[]
 for symbol in ['MSFT','GOOGL','META']:
  for dt in pd.date_range('2019-03-31','2026-09-30',freq='QE'):
   end=dt.date().isoformat();year=dt.year
   start=pd.Timestamp(year if symbol!='MSFT' or dt.month>=7 else year-1,7 if symbol=='MSFT' else 1,1)
   try:
    if dt+pd.Timedelta(days=1)==start+pd.DateOffset(years=1):parts=[('annual',1,paired(facts,symbol,start.date().isoformat(),end))]
    else:
     current=paired(facts,symbol,start.date().isoformat(),end);prior=paired(facts,symbol,(start-pd.DateOffset(years=1)).date().isoformat(),(dt-pd.DateOffset(years=1)).date().isoformat(),accession=current['cfo']['accn']);annual=paired(facts,symbol,(start-pd.DateOffset(years=1)).date().isoformat(),(start-pd.Timedelta(days=1)).date().isoformat());parts=[('annual',1,annual),('current_ytd',1,current),('prior_ytd',-1,prior)]
    result={metric:sum(sign*pair[metric]['val'] for _,sign,pair in parts) for metric in TAGS};assert result['capex']>0
    rows.append(dict(symbol=symbol,end=end,period_start=(dt-pd.DateOffset(years=1)+pd.Timedelta(days=1)).date().isoformat(),cfo=result['cfo'],capex=result['capex'],cash_after_capex=result['cfo']-result['capex'],capex_to_cfo=result['capex']/result['cfo']))
    for role,sign,pair in parts:
     for metric,x in pair.items():lineage.append(dict(symbol=symbol,ttm_end=end,role=role,coefficient=sign,metric=metric,tag=TAGS[metric],start=x['start'],end=x['end'],value=x['val'],filed=x['filed'],accession=x['accn'],form=x['form'],unit='USD',source_url='https://www.sec.gov/Archives/edgar/data/'+str(facts[symbol]['cik'])+'/'+x['accn'].replace('-','')+'/'))
   except (ValueError,AssertionError,KeyError) as exc:exceptions.append(dict(symbol=symbol,end=end,reason=str(exc)))
 return pd.DataFrame(rows),pd.DataFrame(lineage),exceptions

def stress(cfo,capex,cfo_shock=0,capex_growth=.1,other_uses=0,retained_target=20e9):
 if not all(np.isfinite(x) for x in [cfo,capex,cfo_shock,capex_growth,other_uses,retained_target]) or cfo<=0 or capex<=0 or not 0<=cfo_shock<=1 or capex_growth<-.99 or other_uses<0 or retained_target<0:raise ValueError('Invalid scenario inputs')
 new_cfo=cfo*(1-cfo_shock);new_capex=capex*(1+capex_growth);retained=new_cfo-new_capex-other_uses
 return dict(stressed_cfo=new_cfo,stressed_capex=new_capex,retained=retained,gap_to_target=retained-retained_target,maximum_capex_growth=(new_cfo-other_uses-retained_target)/capex-1,maximum_cfo_decline=1-(new_capex+other_uses+retained_target)/cfo)
