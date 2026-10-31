from pathlib import Path
import argparse,json,hashlib,urllib.request
ROOT=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);a=p.parse_args();a.cache.mkdir(parents=True,exist_ok=True)
 seen=set()
 for x in json.loads((ROOT/'data/source_manifest.json').read_text()):
  if x['url'] in seen:continue
  seen.add(x['url']);r=urllib.request.urlopen(urllib.request.Request(x['url'],headers={'User-Agent':'PortfolioResearch/1.0 public-data analysis'}),timeout=120);v=r.read();(a.cache/x['file']).write_bytes(v);print(x['file'],'matches pinned original' if hashlib.sha256(v).hexdigest()==x['sha256'] else 'changed upstream; retained separately, do not overwrite pinned inputs')
if __name__=='__main__':main()
