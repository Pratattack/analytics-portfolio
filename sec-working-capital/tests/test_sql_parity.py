"""Independent SQLite calculation parity checks: catches integer truncation."""
import sqlite3
from pathlib import Path
import pandas as pd
from scripts.analysis import analyze
ROOT=Path(__file__).resolve().parents[1]
def test_sql_python_parity_fifteen_company_panel():
    raw=pd.read_csv(ROOT/'data/firecrawl_snapshot.csv')
    py=analyze(raw)
    with sqlite3.connect(':memory:') as db:
        raw.to_sql('working_capital',db,index=False)
        sql=pd.read_sql_query((ROOT/'sql/benchmark.sql').read_text(),db)
    assert set(sql.ticker)==set(py.ticker)==set(raw.ticker)
    for row in sql.itertuples():
        expected=py[py.ticker==row.ticker].iloc[0]
        for left,right in [('dso','dso_days'),('dio','dio_days'),('dpo','dpo_days'),('ccc','ccc_days')]:
            assert abs(float(expected[left])-float(getattr(row,right))) < .011
        assert int(expected.fcf)==int(row.fcf_musd)
