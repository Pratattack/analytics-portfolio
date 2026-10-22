"""Conservative original-current-period selection from SEC entity-wide standard facts."""
from pathlib import Path
from datetime import date
import json,gzip,hashlib,csv
ROOT=Path(__file__).resolve().parent
CUTOFF='2026-10-20' # completed prior day; exclude today's date-only filings
ALIASES={
'inventory':['InventoryNet'],
'cost':['CostOfRevenue','CostOfGoodsAndServicesSold','CostOfGoodsSold'],
'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet','SalesRevenueGoodsNet'],
'op_income':['OperatingIncomeLoss'],
'cfo':['NetCashProvidedByUsedInOperatingActivities'],
'capex':['PaymentsToAcquirePropertyPlantAndEquipment'],
'dividends':['PaymentsOfDividendsCommonStock','PaymentsOfDividends'],
'buybacks':['PaymentsForRepurchaseOfCommonStock'],
'ppe_net':['PropertyPlantAndEquipmentNet','PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization'],
'ppe_gross':['PropertyPlantAndEquipmentGross','PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetBeforeAccumulatedDepreciationAndAmortization'],
'cash':['CashAndCashEquivalentsAtCarryingValue'],
}
def days(a,b):return (date.fromisoformat(b)-date.fromisoformat(a)).days

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:p.write_text('');return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def source_rows(obj):
 out=[]
 for tag,concept in obj['facts'].get('us-gaap',{}).items():
  if tag not in {t for tags in ALIASES.values() for t in tags}:continue
  for i,f in enumerate(concept['units'].get('USD',[])):
   if f.get('form') in ('10-K','10-Q') and f.get('filed','9999')<=CUTOFF:
    out.append(dict(f,tag=tag,pointer=f"/facts/us-gaap/{tag}/units/USD/{i}"))
 return out

def pick(rows,metric,kind,end,accn=None,start=None,asof=CUTOFF):
 # Alias precedence explicit; contradictory duplicate contexts are rejected.
 for tag in ALIASES[metric]:
  fs=[f for f in rows if f['tag']==tag and f['end']==end and f['filed']<=asof and (accn is None or f['accn']==accn)]
  if kind=='instant':fs=[f for f in fs if 'start' not in f]
  else:
   lo,hi={'quarter':(75,105),'annual':(350,380),'ytd9':(255,290)}[kind]
   fs=[f for f in fs if 'start' in f and lo<=days(f['start'],f['end'])+1<=hi and (start is None or f['start']==start)]
  if fs:
   # Last known revision only when explicitly as-of selecting a Q4 operand.
   chosen_date=max(f['filed'] for f in fs) if accn is None else min(f['filed'] for f in fs)
   fs=[f for f in fs if f['filed']==chosen_date]
   vals={f['val'] for f in fs}
   if len(vals)!=1:raise ValueError('contradictory contexts '+metric+' '+end)
   return sorted(fs,key=lambda f:(f.get('start',''),f['accn'],f['pointer']))[0]
 return None

def run(project):
 root=ROOT/project; manifest=json.loads((root/'data/source_manifest.json').read_text());lineage=[];panel=[];issues=[];revisions=[]
 def use(ticker,metric,f,record,operand='direct'):
  lineage.append({'ticker':ticker,'record_end':record,'metric':metric,'operand':operand,'tag':f['tag'],'pointer':f['pointer'],'start':f.get('start',''),'end':f['end'],'filed':f['filed'],'accn':f['accn'],'value_usd':f['val']})
 for m in manifest:
  b=gzip.decompress((root/'data/raw'/f"{m['ticker']}.json.gz").read_bytes());assert hashlib.sha256(b).hexdigest()==m['sha256_uncompressed']
  obj=json.loads(b);assert obj['cik']==m['cik'];rows=source_rows(obj);t=m['ticker']
  anchor='inventory' if project.startswith('semiconductor') else 'ppe_net'
  ends=sorted({f['end'] for f in rows if f['tag'] in ALIASES[anchor] and f['end']>='2011-01-01' and 'start' not in f})
  for end in ends:
   candidates=sorted({(f['filed'],f['accn'],f['form']) for f in rows if f['tag'] in ALIASES[anchor] and f['end']==end and 0<days(end,f['filed'])<=120 and (project.startswith('semiconductor') or f['form']=='10-K')})
   if not candidates:continue
   filed,accn,form=candidates[0];record={'ticker':t,'end':end,'filed':filed,'accn':accn,'cik':m['cik'],'form':form}
   local=[]
   try:
    metrics=['inventory','cost','revenue'] if project.startswith('semiconductor') else ['ppe_net','ppe_gross','revenue','op_income','cfo','capex','dividends','buybacks']
    for metric in metrics:
     kind='instant' if metric in ('inventory','ppe_net','ppe_gross') else ('annual' if form=='10-K' else 'quarter')
     f=pick(rows,metric,kind,end,accn)
     if not f:
      if metric=='ppe_gross':record[metric]=None;continue
      raise ValueError('missing coherent '+metric)
     record[metric]=f['val'];local.append((metric,f,'direct'))
     if metric in ('ppe_net','ppe_gross'):record[metric+'_basis']='finance_lease_inclusive' if 'FinanceLease' in f['tag'] else 'reported_ppe'
     if project.startswith('semiconductor') and form=='10-K' and metric in ('cost','revenue'):
      operands=[g for g in rows if g['tag'] in ALIASES[metric] and g.get('start')==f['start'] and 255<=days(g['start'],g['end'])+1<=290 and 75<=days(g['end'],end)<=105 and g['filed']<=filed]
      if not operands:raise ValueError('missing nine-month operand '+metric)
      q3end=max(g['end'] for g in operands);g=pick(rows,metric,'ytd9',q3end,start=f['start'],asof=filed)
      if not g:raise ValueError('missing mapped nine-month operand')
      record[metric]=f['val']-g['val'];local[-1]=(metric,f,'annual_plus');local.append((metric,g,'ytd9_minus'))
    if record['revenue']<=0 or record[anchor]<=0:raise ValueError('nonpositive required balance/revenue')
    if project.startswith('semiconductor') and record['cost']<=0:raise ValueError('nonpositive derived cost')
    if not project.startswith('semiconductor') and (record['capex']<0 or record['dividends']<0 or record['buybacks']<0):raise ValueError('unexpected outflow sign')
   except ValueError as e:
    issues.append({'ticker':t,'end':end,'reason':str(e),'accn':accn});continue
   for metric,f,operand in local:
    use(t,metric,f,end,operand)
    later=[g for g in rows if g['tag']==f['tag'] and g['end']==f['end'] and g.get('start')==f.get('start') and g['filed']>f['filed']]
    if later:
     z=sorted(later,key=lambda g:(g['filed'],g['accn']))[-1]
     if z['val']!=f['val']:revisions.append({'ticker':t,'end':end,'metric':metric,'original':f['val'],'later':z['val'],'later_filed':z['filed'],'original_pointer':f['pointer'],'later_pointer':z['pointer']})
   panel.append(record)
 out=root/'outputs';write_csv(out/'panel.csv',panel);write_csv(out/'source_lineage.csv',lineage);write_csv(out/'exclusions.csv',issues);write_csv(out/'later_revision_audit.csv',revisions)
 print(project,len(panel),'records',len(lineage),'operands',len(issues),'exclusions',len(revisions),'revision differences')
 return panel
if __name__=='__main__':
 for p in ['semiconductor-inventory-funding','freight-rail-capital-review']:run(p)
