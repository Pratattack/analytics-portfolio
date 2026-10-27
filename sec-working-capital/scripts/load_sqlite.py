import sqlite3
from pathlib import Path
import pandas as pd
from scripts.analysis import analyze
ROOT=Path(__file__).resolve().parents[1]
df=analyze(pd.read_csv(ROOT/'data/firecrawl_snapshot.csv',dtype={'cik':str}))
with sqlite3.connect(ROOT/'data/finance.db') as db:
    df.to_sql('working_capital',db,if_exists='replace',index=False)
    print(pd.read_sql_query('SELECT ticker, ROUND(ccc,2) AS ccc_days, ROUND(fcf,0) AS fcf_musd FROM working_capital ORDER BY ccc',db))
