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
if __name__=='__main__':main()
