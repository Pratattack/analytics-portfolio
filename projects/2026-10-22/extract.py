"""Context-exact source selection. Missing values remain missing; rounded narrative duplicates are audited."""
import json,gzip,hashlib,csv
from datetime import date
from config import ROOT,CUTOFF,LAND,HOTEL

def write_csv(p,rows,fields=None):
 p.parent.mkdir(parents=True,exist_ok=True);fields=fields or list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def duration(f):return (date.fromisoformat(f['end'])-date.fromisoformat(f['start'])).days+1 if f['start'] else 0
def precision(f):return 999 if f['decimals']=='INF' else int(f['decimals'])
def tolerance(f):return 0 if f['decimals']=='INF' else .5*10**(-int(f['decimals']))

def select(fs,tags,dims,start,end,variants):
 for tag in tags:
  a=[f for f in fs if f['tag']==tag and f['dimensions']==dims and f['start']==start and f['end']==end and f['unit'].upper()=='ISO4217:USD']
  if not a:continue
  a.sort(key=lambda f:(-precision(f),f['element_index']));best=a[0]
  for other in a[1:]:
   if abs(best['value']-other['value'])>tolerance(best)+tolerance(other)+.01:raise ValueError(f'Contradictory same-scope values {tag} {start} {end}')
   if best['value']!=other['value']:variants.append({'tag':tag,'end':end,'chosen':best['value'],'other':other['value'],'other_decimals':other['decimals'],'reason':'Overlapping declared rounding intervals; highest precision retained'})
  return best
 return None
PRODUCT='srt:ProductOrServiceAxis'
def product(member):return {PRODUCT:member}

def specs(t):
 if t=='MAR':return {'revenue':(['us-gaap:Revenues'],{}),'reimb_revenue':(['us-gaap:Revenues'],product('mar:ReimbursementsMember')),'reimb_expense':(['us-gaap:CostOfRevenue'],product('mar:ReimbursementsMember')),'op_income':(['us-gaap:OperatingIncomeLoss'],{}),'fee_revenue':(['us-gaap:Revenues'],product('mar:FeeServiceMember'))}
 if t=='HLT':return {'revenue':(['us-gaap:Revenues','us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'],{}),'reimb_revenue':(['us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'],product('hlt:ReimbursementRevenueMember')),'reimb_expense':(['hlt:ReimbursedExpenses','hlt:OtherExpensesFromManagedAndFranchisedProperties'],{}),'op_income':(['us-gaap:OperatingIncomeLoss'],{})}
 if t=='CHH':return {'revenue':(['us-gaap:Revenues'],{}),'reimb_revenue':(['us-gaap:Revenues'],product('chh:RevenueForReimbursableCostsFromFranchisedAndManagedPropertiesMember')),'reimb_expense':(['us-gaap:CostOfGoodsAndServicesSold'],product('chh:RevenueForReimbursableCostsFromFranchisedAndManagedPropertiesMember')),'op_income':(['us-gaap:OperatingIncomeLoss'],{}),'fee_revenue':(['us-gaap:Revenues'],product('chh:FranchiseAndManagementFeesMember'))}

def run(project):
 root=ROOT/project;manifest=json.loads((root/'data/source_manifest.json').read_text());lineage=[];exclusions=[];variants=[];candidates=[]
 def use(m,metric,f,record):
  lineage.append({'ticker':m['ticker'],'record':record,'metric':metric,'source_file':m['file'],'source_url':m['url'],'filed':m['filed'],'accession':m['accession'],'cell_index':f['element_index'],'tag':f['tag'],'context':f['context'],'start':f['start'],'end':f['end'],'dimensions':json.dumps(f['dimensions'],sort_keys=True),'value_usd':f['value']})
 for m in manifest:
  assert m['filed']<=CUTOFF
  archive=(root/'data/raw'/m['file']).read_bytes();assert hashlib.sha256(archive).hexdigest()==m['archive_sha256'];b=gzip.decompress(archive);assert hashlib.sha256(b).hexdigest()==m['snapshot_sha256'];fs=json.loads(b);t=m['ticker'];local=[]
  if project==HOTEL:
   periods=sorted({(f['start'],f['end']) for f in fs if f['start'] and f['end']>='2018-01-01' and f['end']<=m['report_end'] and (350<=duration(f)<=380 or 75<=duration(f)<=105 or 175<=duration(f)<=195) and not f['dimensions'] and f['tag'] in ['us-gaap:Revenues','us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax']})
   for start,end in periods:
    d=(date.fromisoformat(end)-date.fromisoformat(start)).days+1;r={'ticker':t,'start':start,'end':end,'period':'annual' if d>=350 else ('half' if d>=175 else 'quarter'),'filed':m['filed'],'accession':m['accession']};used=[]
    for metric,(tags,dims) in (specs(t)|{'operating_costs':(['us-gaap:CostsAndExpenses','us-gaap:OperatingCostsAndExpenses'],{})}).items():
     f=select(fs,tags,dims,start,end,variants)
     # Explicit versioned schema aliases; NEVER use negated EBITDA bridge cells as revenue.
     if not f and metric=='reimb_expense' and t=='HLT':f=select(fs,['us-gaap:CostOfGoodsAndServicesSold'],product('hlt:CostofReimbursableExpenseMember'),start,end,variants)
     if not f and t=='CHH' and metric.startswith('reimb_'):f=select(fs,['us-gaap:Revenues'] if metric=='reimb_revenue' else ['us-gaap:CostOfGoodsAndServicesSold'],product('chh:OtherRevenuesFromFranchisedAndManagedPropertiesMember'),start,end,variants)
     if not f and metric=='fee_revenue':r[metric]=None;continue
     if not f:exclusions.append({'ticker':t,'source':m['file'],'start':start,'end':end,'reason':'missing comparable '+metric});break
     r[metric]=f['value'];used.append((metric,f))
    else:
     assert r['revenue']>r['reimb_revenue']>=0 and r['reimb_expense']>=0
     adjust=0
     if abs(r['revenue']-r['operating_costs']-r['op_income'])>=1:
      extra={'CHH':[('gain_disposition',['chh:GainLossOnDispositionOfBusinessAndSaleOfProperties'],1),('impairment',['us-gaap:ImpairmentOfLongLivedAssetsHeldForUse'],-1)],'HLT':[('gain_disposition',['us-gaap:GainLossOnDispositionOfAssets1'],1)]}.get(t,[])
      for name,tags,sign in extra:
       f=select(fs,tags,{},start,end,variants)
       if f:adjust+=sign*f['value'];used.append((name,f))
     r['operating_line_adjustments']=adjust;r['income_statement_residual']=r['revenue']-r['operating_costs']+adjust-r['op_income']
     assert abs(r['income_statement_residual'])<1, ('income statement fails',r)
     key=f'{t}|{start}|{end}';candidates.append((r,m,used,key));continue
  else:
   ends=sorted({f['end'] for f in fs if not f['start'] and f['end']>='2018-01-01'})
   for end in ends:
    if end>m['report_end']:continue
    scopes=[]
    if t in ('PHM','KBH'):
     axis='srt:ConsolidatedEntitiesAxis';other='us-gaap:ConsolidatedEntityExcludingVieMember' if t=='PHM' else 'kbh:NonVIELandOptionContractsAndOtherSimilarContractsMember'
     scopes=[('VIE',{axis:'us-gaap:VariableInterestEntityNotPrimaryBeneficiaryMember'}),('other',{axis:other}),('total',{})]
     dt='us-gaap:PurchaseOptionsLand' if t=='PHM' else 'kbh:CashDepositsOnLandOptionAndOtherSimilarContracts';pt='phm:RemainingPurchasePriceOfAllLandOptionAgreements' if t=='PHM' else 'kbh:AggregatePurchasePriceAssociatedWithLandOptionAndOtherSimilarContracts'
    else:
     scopes=[('committed',{}),('uncommitted',{}),('total',{})]
    for scope,dims in scopes:
     if t=='MTH':
      prefix={'committed':'mth:LandUnderPurchaseContractsNotRecordedRefundableCommitted','uncommitted':'mth:LandUnderPurchaseAndOptionContractsNotRecordedRefundableUncommitted','total':'us-gaap:LandUnderPurchaseOptionsNotRecorded'}[scope]
      dt={'committed':prefix+'CashDeposits','uncommitted':prefix+'CashDeposits','total':'mth:LandUnderOptionContractNotRecordedCashDeposits'}[scope];pt=prefix
     dep=select(fs,(['mth:LandUnderPurchaseAndOptionContractsCommittedCashDeposits',dt] if t=='MTH' and scope=='committed' else [dt]),dims,'',end,variants);price=select(fs,(['mth:LandUnderPurchaseAndOptionContractsCommitted',pt] if t=='MTH' and scope=='committed' else [pt]),dims,'',end,variants)
     if not dep or not price:
      if dep or price:exclusions.append({'ticker':t,'source':m['file'],'start':'','end':end,'reason':'incomplete '+scope+' deposit/price pair'})
      continue
     r={'ticker':t,'scope':scope,'end':end,'filed':m['filed'],'accession':m['accession'],'deposits':dep['value'],'disclosed_price':price['value'],'price_basis':'remaining' if t=='PHM' else 'aggregate','exposure_basis':'deposits_and_preacquisition' if t=='PHM' else 'cash_deposits','remaining_price':price['value'] if t=='PHM' else price['value']-dep['value']}
     assert r['deposits']>=0 and r['remaining_price']>0
     key=f'{t}|{scope}|{end}';used=[('deposits',dep),('disclosed_price',price)]
     # KBH separately discloses pre-acquisition costs: not included in cash deposits or credited against price.
     if scope=='total' and t=='KBH':
      f=select(fs,['kbh:AcquisitionCostsRelatedToLandOptionContractsAndOtherSimilarContracts'],{},'',end,variants)
      r['additional_preacquisition']=None if not f else f['value']
      if f:used.append(('additional_preacquisition',f))
     if t=='MTH' and scope=='committed':
      prefixes=['mth:LandUnderOptionContractsNotRecordedNonRefundableCommitted','mth:LandUnderPurchaseContractsNotRecordedNonRefundableCommitted','mth:LandUnderPurchaseContractsNotRecordedRefundableCommitted']
      ds=[select(fs,[x+'CashDeposits'],{},'',end,variants) for x in prefixes];ps=[select(fs,[x],{},'',end,variants) for x in prefixes]
      if all(ds) and all(ps):
       r['deposits']=sum(f['value'] for f in ds);r['disclosed_price']=sum(f['value'] for f in ps);r['remaining_price']=r['disclosed_price']-r['deposits'];used=[('deposits_component_'+str(i),f) for i,f in enumerate(ds)]+[('disclosed_price_component_'+str(i),f) for i,f in enumerate(ps)]
     candidates.append((r,m,used,key))
 # Latest available original disclosure of each historical scope is retained, not an as-known-then panel.
 chosen={}
 for r,m,used,key in candidates:
  if key not in chosen or (m['filed'],m['accession'])>(chosen[key][1]['filed'],chosen[key][1]['accession']):chosen[key]=(r,m,used,key)
 panel=[];revisions=[]
 for key,(r,m,used,_) in sorted(chosen.items()):
  panel.append(r)
  for metric,f in used:use(m,metric,f,key)
  for old,om,ou,ok in candidates:
   if ok==key and om['accession']!=m['accession']:
    fields=['revenue','reimb_revenue','reimb_expense','op_income'] if project==HOTEL else ['deposits','disclosed_price']
    for metric in fields:
     if old[metric]!=r[metric]:revisions.append({'record':key,'metric':metric,'older_value':old[metric],'chosen_value':r[metric],'older_filed':om['filed'],'chosen_filed':m['filed']})
 out=root/'outputs';write_csv(out/'panel.csv',panel);write_csv(out/'source_lineage.csv',lineage);write_csv(out/'exclusions.csv',exclusions,['ticker','source','start','end','reason']);write_csv(out/'rounded_duplicates.csv',variants,['tag','end','chosen','other','other_decimals','reason']);write_csv(out/'disclosure_revisions.csv',revisions,['record','metric','older_value','chosen_value','older_filed','chosen_filed'])
 print(project,len(panel),'records',len(lineage),'operands',len(exclusions),'exclusions',len(revisions),'revisions')
 return panel
if __name__=='__main__':
 for p in [LAND,HOTEL]:run(p)
