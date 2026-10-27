from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from scripts.analysis import analyze,scenario_detail,ASSUMPTIONS,audit_snapshot
ROOT=Path(__file__).parent
GROUPS={"AAPL":"Devices & systems","DELL":"Devices & systems","HPQ":"Devices & systems","CSCO":"Enterprise technology","MSFT":"Enterprise technology","NVDA":"Semiconductors","AMD":"Semiconductors","INTC":"Semiconductors","QCOM":"Semiconductors","TXN":"Semiconductors","IBM":"Enterprise technology","AMZN":"Platform & logistics","LRCX":"Semiconductor equipment","KLAC":"Semiconductor equipment","ADI":"Semiconductors"}
GROUP_ORDER=['Devices & systems','Semiconductors','Semiconductor equipment','Enterprise technology','Platform & logistics']
st.set_page_config(page_title='SEC Working Capital | CFO Advisory',layout='wide')
st.title('SEC Working Capital — 15-Company CFO Advisory')
st.caption('15 companies • SEC 10-K XBRL • FY2025–FY2026 • dollar values in millions • refreshed October 27, 2026')
raw=pd.read_csv(ROOT/'data/firecrawl_snapshot.csv',dtype={'cik':str})
audit=pd.read_csv(ROOT/'data/xbrl_audit.csv')
audit_snapshot(raw,audit)
df=analyze(raw)
df['peer_group']=df.ticker.map(GROUPS)
df['capex_intensity']=df.capex/df.revenue
st.info('All 150 modeled source inputs reconcile to accession-matched SEC 10-K companyconcept values. The ratios are analyst-derived. Compare within groups; do not interpret cross-sector CCC as an efficiency ranking.')
selected_groups=st.multiselect('Peer groups',GROUP_ORDER,default=GROUP_ORDER)
eligible=df[df.peer_group.isin(selected_groups)]
selected_tickers=st.multiselect('Companies',eligible.ticker.tolist(),default=eligible.ticker.tolist())
view=eligible[eligible.ticker.isin(selected_tickers)]
if view.empty:
    st.warning('Select at least one company.')
    st.stop()
st.subheader('Company financial scorecard')
show=['company','ticker','peer_group','fiscal_end','revenue','dso','dio','dpo','ccc','fcf','fcf_margin','gross_margin','capex_intensity']
st.dataframe(view[show].round(3).sort_values(['peer_group','ticker']),hide_index=True,use_container_width=True)
st.subheader('Ratio drivers')
c1,c2=st.columns(2)
with c1:
    st.plotly_chart(px.bar(view,x='ticker',y=['dso','dio','dpo'],barmode='group',title='Working-capital components (days)'),use_container_width=True)
with c2:
    st.plotly_chart(px.bar(view,x='ticker',y='ccc',color='peer_group',title='Cash conversion cycle (days)'),use_container_width=True)
c3,c4=st.columns(2)
with c3:st.plotly_chart(px.scatter(view,x='gross_margin',y='ccc',size='revenue',color='peer_group',hover_name='company',title='Different operating models: gross margin vs CCC'),use_container_width=True)
with c4:st.plotly_chart(px.scatter(view,x='capex_intensity',y='fcf_margin',size='revenue',color='peer_group',hover_name='company',title='Capital intensity vs free cash flow margin'),use_container_width=True)
st.subheader('Within-group comparisons')
summary=view.groupby('peer_group',as_index=False).agg(companies=('ticker','size'),median_ccc=('ccc','median'),median_dso=('dso','median'),median_dio=('dio','median'),median_dpo=('dpo','median'),median_fcf_margin=('fcf_margin','median'))
st.dataframe(summary.round(2),hide_index=True,use_container_width=True)
st.caption('Unweighted cohort medians are descriptive. Groups with one constituent have no statistical peer distribution.')
st.subheader('Apple scenario decision laboratory')
st.caption('Illustrative one-time liquidity release, not profit or a causal estimate.')
apple=df.loc[df.ticker=='AAPL'].iloc[0]
a,b,c,d=st.columns(4)
dso=a.slider('Reduce DSO (days)',0.,5.,2.,.5)
dio=b.slider('Reduce DIO (days)',0.,5.,1.,.5)
dpo=c.slider('Extend DPO (days)',0.,5.,1.,.5)
real=d.slider('Realization fraction',0.,1.,.7,.05)
e,f=st.columns(2)
cost=e.number_input('One-time implementation ($m)',min_value=0.,value=350.,step=25.)
rate=f.slider('Annual financing rate',0.,.15,.05,.005)
s=scenario_detail(apple,dso,dio,dpo,real,cost,rate)
k1,k2,k3=st.columns(3)
k1.metric('Gross liquidity release',f"${s['gross_release_musd']:,.0f}m")
k2.metric('Net first-year liquidity',f"${s['net_first_year_liquidity_musd']:,.0f}m")
k3.metric('First-year financing benefit less cost',f"${s['net_first_year_value_musd']:,.0f}m")
with st.expander('Sensitivity matrix'):
    hm=pd.DataFrame([{'DSO reduction':q,'Realization':r,'Gross liquidity ($m)':round(scenario_detail(apple,q,dio,dpo,r,cost,rate)['gross_release_musd'])} for q in [0,1,2,3,4,5] for r in [.4,.6,.8,1.]])
    st.plotly_chart(px.density_heatmap(hm,x='DSO reduction',y='Realization',z='Gross liquidity ($m)',text_auto=True),use_container_width=True)
st.subheader('Scenario assumptions')
st.dataframe(pd.DataFrame([{'scenario':label,**scenario_detail(apple,dd,ii,pp,rr,cc,cr)} for label,dd,ii,pp,rr,cc,cr in ASSUMPTIONS]).round(2),use_container_width=True,hide_index=True)
with st.expander('Source filings (15)'):
    for r in df.itertuples():st.markdown(f'- [{r.company} — FY end {r.fiscal_end}]({r.source})')
st.warning('Business models, fiscal dates, supplier programs and accounting classification vary. Cross-group rankings are not actionable targets. No causal claim or investment recommendation.')
