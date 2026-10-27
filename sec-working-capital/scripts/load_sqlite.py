import sqlite3
from pathlib import Path
import pandas as pd
from scripts.analysis import analyze,audit_snapshot
ROOT=Path(__file__).resolve().parents[1]
raw=pd.read_csv(ROOT/'data/firecrawl_snapshot.csv',dtype={'cik':str})
audit=pd.read_csv(ROOT/'data/xbrl_audit.csv')
audit_snapshot(raw,audit)
df=analyze(raw)
with sqlite3.connect(ROOT/'data/finance.db') as db:
    raw.to_sql('working_capital',db,if_exists='replace',index=False)
    sql=(ROOT/'sql/benchmark.sql').read_text()
    independent=pd.read_sql_query(sql,db)
    independent.to_csv(ROOT/'data/sql_metrics.csv',index=False)
    for r in independent.itertuples():
        py=df[df.ticker==r.ticker].iloc[0]
        assert abs(py.dso-r.dso_days)<.011 and abs(py.dio-r.dio_days)<.011
        assert abs(py.dpo-r.dpo_days)<.011 and abs(py.ccc-r.ccc_days)<.011
        assert py.fcf==r.fcf_musd
    print(independent.to_string(index=False))
