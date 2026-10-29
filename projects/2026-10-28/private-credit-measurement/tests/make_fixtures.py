import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import stress,ROOT
rows=json.loads((ROOT/'data/vehicle_balance_sheets.json').read_text());fixtures=[dict(args=[l,e,f],expected=stress(rows,l,e,f)) for l in [0,.1,.5,1] for e in [0,.2,.8] for f in [.25,.5]]
(ROOT/'outputs/parity_fixtures.json').write_text(json.dumps(fixtures,allow_nan=False)+'\n')
