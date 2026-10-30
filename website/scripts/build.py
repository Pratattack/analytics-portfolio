"""Build source-preserving project outputs, then apply the approved portfolio theme."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
 home=ROOT/'dist/index.html';prior=home.read_bytes();template=ROOT/'designs/charcoal/index.html'
 try:
  home.write_bytes(template.read_bytes())
  subprocess.run([sys.executable,str(ROOT/'scripts/build_charcoal.py'),*sys.argv[1:]],cwd=ROOT,check=True)
  subprocess.run([sys.executable,str(ROOT/'designs/persona3/build.py')],cwd=ROOT,check=True)
  subprocess.run([sys.executable,str(ROOT/'designs/persona3/build_site.py')],cwd=ROOT,check=True)
 except Exception:
  home.write_bytes(prior);raise
if __name__=='__main__':main()
