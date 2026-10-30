"""Re-download pinned official inputs into a separate cache; never overwrite the published snapshot."""
from pathlib import Path
import argparse,hashlib,json,urllib.request
ROOT=Path(__file__).parent
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--cache',type=Path,required=True);args=parser.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
 for source in manifest:
  target=args.cache/source['file'];request=urllib.request.Request(source['url'],headers={'User-Agent':'PortfolioResearch public economics research'})
  data=urllib.request.urlopen(request,timeout=120).read();target.write_bytes(data);match=hashlib.sha256(data).hexdigest()==source['sha256'];print(source['file'], 'matches pinned snapshot' if match else 'CHANGED upstream; retained separately, do not overwrite pinned inputs')
 # Reconstruct the selected bulk observations and compare values to the release input.
 import pandas as pd
 ids=set(pd.read_csv(ROOT/'data/series.csv',dtype=str).series_id)
 d=pd.read_csv(args.cache/'jolts-data.txt',sep='\t',dtype=str).fillna('');d.columns=d.columns.str.strip();d=d.map(lambda x:x.strip());d=d[d.series_id.isin(ids)&(d.year.astype(int)>=2015)&d.period.str.match(r'M(0[1-9]|1[0-2])')];d['value']=pd.to_numeric(d.value,errors='raise');d.to_csv(args.cache/'selected-observations.csv',index=False)
 pinned=pd.read_csv(ROOT/'data/observations.csv').fillna('');candidate=pd.read_csv(args.cache/'selected-observations.csv').fillna('');pd.testing.assert_frame_equal(pinned.reset_index(drop=True),candidate.reset_index(drop=True));print('Selected observations reproduce exactly.')
if __name__=='__main__':main()
