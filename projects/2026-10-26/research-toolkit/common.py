from pathlib import Path
import json,csv,hashlib
ROOT=Path(__file__).resolve().parent.parent
CREDIT='credit-spread-recession-audit'
REST='restaurant-lease-operating-leverage'
def dump(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def csvout(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as f:
  if rows:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def readcsv(p):
 with p.open() as f:return list(csv.DictReader(f))
