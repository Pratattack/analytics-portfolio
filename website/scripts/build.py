"""Build source-preserving project outputs, then apply the approved portfolio theme."""
from pathlib import Path
import argparse
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--projects-source',type=Path,required=True)
 parser.add_argument('--only-slugs',nargs='+')
 args=parser.parse_args()
 build_args=['--projects-source',str(args.projects_source.resolve())]
 if args.only_slugs:
  build_args.extend(['--only-slugs',*args.only_slugs])
 home=ROOT/'dist/index.html';prior=home.read_bytes();template=ROOT/'designs/charcoal/index.html'
 try:
  home.write_bytes(template.read_bytes())
  subprocess.run([sys.executable,str(ROOT/'scripts/build_charcoal.py'),*build_args],cwd=ROOT,check=True)
  subprocess.run([sys.executable,str(ROOT/'designs/persona3/build.py')],cwd=ROOT,check=True)
  subprocess.run([sys.executable,str(ROOT/'designs/persona3/build_site.py')],cwd=ROOT,check=True)
 except Exception:
  home.write_bytes(prior);raise
if __name__=='__main__':main()
