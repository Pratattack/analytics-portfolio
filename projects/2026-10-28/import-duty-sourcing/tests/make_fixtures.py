import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analyze import sourcing,ROOT
import pandas as pd
pairs=pd.read_csv(ROOT/'outputs/eligible_sourcing_pairs.csv');fixtures=[dict(args=[b,s,float(x.source_fixed_basket_duty_ratio),float(x.alternative_fixed_basket_duty_ratio),p,f],expected=sourcing(b,s,float(x.source_fixed_basket_duty_ratio),float(x.alternative_fixed_basket_duty_ratio),p,f)) for x in pairs.head(8).itertuples() for b,s,p,f in [(10000000,.25,.02,50000),(1000000,0,0,100),(1000000,1,-.02,0)]]
(ROOT/'outputs/parity_fixtures.json').write_text(json.dumps(fixtures,allow_nan=False)+'\n')
