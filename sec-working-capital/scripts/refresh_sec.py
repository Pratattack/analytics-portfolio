"""Fetch full SEC CompanyFacts. Never overwrite the reviewed Firecrawl snapshot."""
import json,os,time
from pathlib import Path
import requests
CIKS={'AAPL':'0000320193','DELL':'0001571996','MSFT':'0000789019'}
root=Path(__file__).resolve().parents[1]/'data'/'sec_raw'
agent=os.environ.get('SEC_USER_AGENT')
if not agent or '@' not in agent:
    raise SystemExit("Set SEC_USER_AGENT='Researcher Name contact@example.com'")
root.mkdir(parents=True,exist_ok=True)
for ticker,cik in CIKS.items():
    url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
    response=requests.get(url,headers={'User-Agent':agent,'Accept-Encoding':'gzip, deflate'},timeout=60)
    response.raise_for_status()
    obj=response.json()
    assert str(obj['cik']).zfill(10)==cik
    (root/f'{ticker}.json').write_text(json.dumps(obj))
    print(ticker,len(response.content),url)
    time.sleep(.2)
