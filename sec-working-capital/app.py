from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from scripts.analysis import analyze,scenario
ROOT=Path(__file__).parent
st.set_page_config(page_title='Working Capital | CFO Advisory',layout='wide')
st.title('Working Capital | CFO Advisory')
st.warning('Exploratory SEC 10-K extracts; XBRL reconciliation outstanding. Dell and Microsoft HTML inputs truncated.')
df=analyze(pd.read_csv(ROOT/'data/firecrawl_snapshot.csv',dtype={'cik':str}))
st.dataframe(df[['company','fiscal_end','revenue','dso','dio','dpo','ccc','fcf']].round(2),hide_index=True)
st.plotly_chart(px.bar(df,x='ticker',y='ccc',title='Cash conversion cycle (days)'))
st.subheader('Apple: hypothetical liquidity scenario')
a=df[df.ticker=='AAPL'].iloc[0]
dso=st.slider('DSO reduction (days)',0.,5.,2.,.5)
dio=st.slider('DIO reduction (days)',0.,5.,1.,.5)
dpo=st.slider('DPO extension (days)',0.,5.,1.,.5)
realization=st.slider('Realization',0.,1.,.7,.05)
st.metric('Modeled gross cash release',f'${scenario(a,dso,dio,dpo,realization):,.0f}M')
st.caption('One-time theoretical cash release, not earnings; excludes implementation and supplier costs.')
