from pathlib import Path
import json,csv,hashlib
ROOT=Path(__file__).resolve().parents[1]
FACTS=json.loads((ROOT/'data/filing_facts.json').read_text())
MAN={s['id']:s for s in json.loads((ROOT/'data/filing_manifest.json').read_text())}
lineage=[]
def fact(sym,tag,year,dims=(),period='annual',optional=False):
    end=f'{year}-12-31' if period=='annual' else f'{year}-09-30'
    start=f'{year}-01-01'
    names=tag if isinstance(tag,list) else [tag]
    wanted=sorted(dims)
    rows=[x for x in FACTS if x['source_id'].startswith(sym) and x['name'] in names and x.get('instant',x.get('enddate'))==end and (not x.get('startdate') or x['startdate']==start) and sorted(v[1] for v in x['dimensions'])==wanted]
    rows.sort(key=lambda x:('2026Q3' not in x['source_id'] if period!='annual' else '2025K' not in x['source_id'],names.index(x['name'])))
    if not rows:
        if tag=='us-gaap:OperatingLeaseLiability':
            a=fact(sym,'us-gaap:OperatingLeaseLiabilityCurrent',year,period=period,optional=True)
            b=fact(sym,'us-gaap:OperatingLeaseLiabilityNoncurrent',year,period=period,optional=True)
            if a is not None and b is not None:return a+b
        # Comparative XBRL facts can explicitly report zero without a tagged inline cell.
        if tag=='us-gaap:LongTermDebtCurrent':
            cf=json.loads((ROOT/f'data/raw/{sym}-companyfacts.json').read_text())['facts']['us-gaap']['LongTermDebtCurrent']['units']['USD']
            candidates=[x for x in cf if x['end']==end and x['filed']<='2026-11-01']
            if candidates:
                x=sorted(candidates,key=lambda x:x['filed'])[-1]
                lineage.append(dict(company=sym,metric=tag,period=end,start='',value_usd=x['val'],context='SEC companyfacts comparative',dimensions='[]',source_id=x['accn'],source_url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{1334036:010d}.json',source_sha256=hashlib.sha256((ROOT/f'data/raw/{sym}-companyfacts.json').read_bytes()).hexdigest()))
                return x['val']/1e6
        if optional:return None
        raise ValueError((sym,tag,year,dims,period))
    first=rows[0];dupes=[x for x in rows if x['source_id']==first['source_id'] and x['name']==first['name']]
    assert len({round(x['value'],5) for x in dupes})==1,(sym,tag,'conflicting contexts')
    s=MAN[first['source_id']];lineage.append(dict(company=sym,metric=tag if isinstance(tag,str) else '|'.join(tag),period=end,start=first.get('startdate',''),value_usd=first['value'],context=first['context'],dimensions=json.dumps(first['dimensions']),source_id=first['source_id'],source_url=s['url'],source_sha256=s['sha256']))
    return first['value']/1e6

def prepare(sym):
    out={'ticker':sym,'company':'United Rentals' if sym=='URI' else 'Crocs','historical':{},'interim':{}}
    tags={'revenue':'us-gaap:Revenues' if sym=='URI' else 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax','assets':'us-gaap:Assets','cash':'us-gaap:CashAndCashEquivalentsAtCarryingValue','ar':'us-gaap:AccountsReceivableNetCurrent','inventory':'us-gaap:InventoryNet','current_assets':'us-gaap:AssetsCurrent','goodwill':'us-gaap:Goodwill','intangibles':'us-gaap:FiniteLivedIntangibleAssetsNet' if sym=='URI' else 'us-gaap:IntangibleAssetsNetExcludingGoodwill','rou':'us-gaap:OperatingLeaseRightOfUseAsset','liabilities':'us-gaap:Liabilities','current_liabilities':'us-gaap:LiabilitiesCurrent','ap':'us-gaap:AccountsPayableCurrent','lease':'us-gaap:OperatingLeaseLiability','lease_current':'us-gaap:OperatingLeaseLiabilityCurrent','debt_current':'us-gaap:DebtCurrent' if sym=='URI' else 'us-gaap:LongTermDebtCurrent','debt_noncurrent':'us-gaap:LongTermDebtAndCapitalLeaseObligations' if sym=='URI' else 'us-gaap:LongTermDebtNoncurrent','equity':'us-gaap:StockholdersEquity','ebit':'us-gaap:OperatingIncomeLoss','ebt':'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest','tax':'us-gaap:IncomeTaxExpenseBenefit','net_income':'us-gaap:NetIncomeLoss','cfo':'us-gaap:NetCashProvidedByUsedInOperatingActivities','cfi':'us-gaap:NetCashProvidedByUsedInInvestingActivities','cff':'us-gaap:NetCashProvidedByUsedInFinancingActivities','fx_cash':'us-gaap:EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents','sbc':'us-gaap:ShareBasedCompensation','buybacks':'us-gaap:PaymentsForRepurchaseOfCommonStock','sga':'us-gaap:SellingGeneralAndAdministrativeExpense','cogs':'us-gaap:CostOfRevenue' if sym=='URI' else 'us-gaap:CostOfGoodsAndServicesSold','da':'uri:DepreciationAndAmortizationExcludingFinancingCostsAndDiscounts' if sym=='URI' else 'us-gaap:DepreciationDepletionAndAmortization','amort':'us-gaap:AmortizationOfIntangibleAssets','capex_other':'uri:PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets' if sym=='URI' else 'us-gaap:PaymentsToAcquirePropertyPlantAndEquipment','shares':'us-gaap:CommonStockSharesOutstanding'}
    for year,period in [(2023,'annual'),(2024,'annual'),(2025,'annual'),(2025,'ytd'),(2026,'ytd')]:
        d={key:fact(sym,tag,year,period=period,optional=period!='annual') for key,tag in tags.items()}
        d['cash_change']=fact(sym,'us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',year,period=period,optional=period!='annual')
        if sym=='URI':
            d['fleet']=fact(sym,'us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization',year,['uri:RentalEquipmentMember'],period,optional=period=='ytd' and year==2025)
            d['fleet_gross']=fact(sym,'us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetBeforeAccumulatedDepreciationAndAmortization',year,['uri:RentalEquipmentMember'],period,optional=period!='annual')
            d['ppe']=fact(sym,'us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization',year,['uri:PropertyPlantandEquipmentEquipmentNotLeasedToOtherPartyMember'],period,optional=period=='ytd' and year==2025)
            for key,tag in [('capex_fleet','uri:PaymentsToAcquirePropertySubjectToOrAvailableForOperatingLease'),('sales_fleet','uri:ProceedsFromSaleOfPropertySubjectToOrAvailableForOperatingLease'),('gain_fleet','uri:GainLossOnSaleOfPropertySubjectToOrAvailableForOperatingLeaseNet'),('dep_fleet','us-gaap:CostOfGoodsAndServicesSoldDepreciationAndAmortization'),('dividends','us-gaap:PaymentsOfDividends')]:d[key]=fact(sym,tag,year,period=period)
            for key,member in [('owned_rental','uri:OwnedEquipmentRentalsMember'),('rental','uri:EquipmentRentalRevenueMember')]:d[key]=fact(sym,'us-gaap:Revenues',year,[member],period)
        else:
            d['ppe']=fact(sym,'us-gaap:PropertyPlantAndEquipmentNet',year,period=period,optional=period=='ytd' and year==2025)
            for key,brand,channel in [('crocs_dtc','crox:CrocsBrandSegmentMember','us-gaap:SalesChannelDirectlyToConsumerMember'),('crocs_wholesale','crox:CrocsBrandSegmentMember','crox:SalesChannelThroughIntermediaryWholesaleMember'),('hey_dtc','crox:HEYDUDEBrandSegmentMember','us-gaap:SalesChannelDirectlyToConsumerMember'),('hey_wholesale','crox:HEYDUDEBrandSegmentMember','crox:SalesChannelThroughIntermediaryWholesaleMember')]:d[key]=fact(sym,tags['revenue'],year,[brand,channel],period)
            d['impairment']=fact(sym,'us-gaap:AssetImpairmentCharges',year,period=period,optional=True)
        out['historical' if period=='annual' else 'interim'][str(year)]=d
    source=[x for x in FACTS if x['source_id']==sym+'-2026Q3' and x['name']=='dei:EntityCommonStockSharesOutstanding'][0]
    out['market']={'price':1170.05 if sym=='URI' else 150.52,'price_date':'2026-10-30','shares_millions':source['value']/1e6,'shares_date':source['instant'],'price_source':f'https://stockanalysis.com/stocks/{sym.lower()}/history/','price_corroboration':'https://chartexchange.com/symbol/nyse-uri/historical/' if sym=='URI' else 'https://www.quiverquant.com/stock/CROX/historical-prices/','note':'Prices corroborated across two vendors. Financial balances are latest reported September 30, not contemporaneous October 30 balances.'}
    out['latest_finite_intangibles']=fact(sym,'us-gaap:FiniteLivedIntangibleAssetsNet',2026,period='ytd') if sym=='URI' else sum(fact(sym,'us-gaap:FiniteLivedIntangibleAssetsNet',2026,[m],period='ytd') for m in ['us-gaap:SoftwareAndSoftwareDevelopmentCostsMember','us-gaap:CustomerRelationshipsMember','us-gaap:IntellectualPropertyMember'])
    out['latest_amort_schedule']=[fact(sym,tag,2025)for tag in ['us-gaap:FiniteLivedIntangibleAssetsAmortizationExpenseNextTwelveMonths','us-gaap:FiniteLivedIntangibleAssetsAmortizationExpenseYearTwo','us-gaap:FiniteLivedIntangibleAssetsAmortizationExpenseYearThree','us-gaap:FiniteLivedIntangibleAssetsAmortizationExpenseYearFour','us-gaap:FiniteLivedIntangibleAssetsAmortizationExpenseYearFive']]
    if sym=='CROX':
        out['latest_ppe_gross']=fact(sym,'us-gaap:AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment',2026,period='ytd')+out['interim']['2026']['ppe']
        out['historical_depreciation']={str(y):fact(sym,'us-gaap:Depreciation',y) for y in [2023,2024,2025]}
    else:out['opening_fleet_gross_approx']=25000
    return out

def main():
    for sym in ['URI','CROX']:
        d=prepare(sym);(ROOT/f'data/{sym}_inputs.json').write_text(json.dumps(d,indent=2)+'\n');print(sym,'prepared')
    with (ROOT/'data/source_lineage.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(lineage[0]));w.writeheader();w.writerows(lineage)
if __name__=='__main__':main()
