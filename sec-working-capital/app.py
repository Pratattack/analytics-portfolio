from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from scripts.analysis import analyze,scenario_detail,ASSUMPTIONS,audit_snapshot
ROOT=Path(__file__).parent
st.set_page_config(page_title='SEC Working Capital | CFO Advisory',layout='wide')
st.title('SEC Working Capital | CFO Advisory')
st.caption('Apple FY2025 vs Dell and Microsoft FY2026 • USD millions • SEC XBRL reconciled October 2026')
raw=pd.read_csv(ROOT/'data/firecrawl_snapshot.csv',dtype={'cik':str})
audit=pd.read_csv(ROOT/'data/xbrl_audit.csv')
audit_snapshot(raw,audit)
df=analyze(raw)
st.info('Selected 10-K values reconciled with US-GAAP XBRL companyconcept facts. Peers have different operating models, fiscal years and payment classifications.')
st.subheader('Liquidity scorecard')
st.dataframe(df[['company','fiscal_end','revenue','dso','dio','dpo','ccc','fcf','fcf_margin','gross_margin']].round(3),hide_index=True,use_container_width=True)
l,r=st.columns(2)
with l:st.plotly_chart(px.bar(df,x='ticker',y=['dso','dio','dpo'],barmode='group',title='Working-capital days'),use_container_width=True)
with r:st.plotly_chart(px.bar(df,x='ticker',y='ccc',title='Cash conversion cycle (days)'),use_container_width=True)
st.plotly_chart(px.bar(df,x='ticker',y='fcf_margin',title='Free cash flow margin'),use_container_width=True)
st.subheader('Apple scenario laboratory')
st.caption('The one-time release is not recurring earnings. All scenario assumptions are hypothetical.')
a=df.loc[df.ticker=='AAPL'].iloc[0]
a1,a2,a3,a4=st.columns(4)
dso=a1.slider('Reduce DSO (days)',0.,5.,2.,.5)
dio=a2.slider('Reduce DIO (days)',0.,5.,1.,.5)
dpo=a3.slider('Extend DPO (days)',0.,5.,1.,.5)
realization=a4.slider('Realization fraction',0.,1.,.7,.05)
b1,b2=st.columns(2)
cost=b1.number_input('Implementation cost ($m)',min_value=0.,value=350.,step=25.)
carry=b2.slider('Annual financing benefit rate',0.,.15,.05,.005)
s=scenario_detail(a,dso,dio,dpo,realization,cost,carry)
x,y,z=st.columns(3)
x.metric('Gross one-time release',f"${s['gross_release_musd']:,.0f}m")
y.metric('Net first-year liquidity',f"${s['net_first_year_liquidity_musd']:,.0f}m")
z.metric('First-year financing benefit less cost',f"${s['net_first_year_value_musd']:,.0f}m")
with st.expander('Sensitivity analysis'):
    heat=pd.DataFrame([{'DSO reduction':d,'Realization':r,'Gross release ($m)':round(scenario_detail(a,d,dio,dpo,r,cost,carry)['gross_release_musd'])} for d in (0,1,2,3,4,5) for r in (.4,.6,.8,1.)])
    st.plotly_chart(px.density_heatmap(heat,x='DSO reduction',y='Realization',z='Gross release ($m)',text_auto=True,title='Sensitivity at selected DIO/DPO settings'),use_container_width=True)
st.subheader('Board scenarios')
st.dataframe(pd.DataFrame([{'Scenario':label,**scenario_detail(a,d,i,p,real,c,rate)} for label,d,i,p,real,c,rate in ASSUMPTIONS]).round(2),hide_index=True,use_container_width=True)
st.subheader('SEC filing provenance')
for _,row in df.iterrows():st.markdown(f'- [{row.company} {row.fiscal_end}]({row.source})')
st.warning('Scenario results are exploratory; compare peers cautiously. Supplier concessions, customer quality, stockout risks and future financing needs require additional diligence.')
