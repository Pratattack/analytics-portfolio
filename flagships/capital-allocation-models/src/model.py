"""Independent financial calculations. USD millions except share prices and ratios."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FLOWS=['revenue','ebit','ebt','tax','net_income','cfo','cfi','cff','fx_cash','sbc','buybacks','sga','cogs','da','capex_other','cash_change','amort','capex_fleet','sales_fleet','gain_fleet','dep_fleet','impairment','dividends','owned_rental','rental','crocs_dtc','crocs_wholesale','hey_dtc','hey_wholesale']

def inputs(sym):
    d=json.loads((ROOT/f'data/{sym}_inputs.json').read_text());latest=d['interim']['2026'];prior=d['interim']['2025'];annual=d['historical']['2025'];ttm=dict(latest)
    for key in FLOWS:
        if all(x.get(key) is not None for x in [latest,prior,annual]):ttm[key]=annual[key]+latest[key]-prior[key]
    d['ttm']=ttm
    d['opening']={'cash':latest['cash'],'ar':latest['ar'],'inventory':latest['inventory'],'other_ca':latest['current_assets']-latest['cash']-latest['ar']-latest['inventory'],'ppe':latest['ppe'],'fleet':latest.get('fleet',0),'goodwill':latest['goodwill'],'intangibles':latest['intangibles'],'rou':latest['rou'],'debt':latest['debt_noncurrent']+(latest['debt_current'] or 0),'ap':latest['ap'],'equity':latest['equity'],'shares':d['market']['shares_millions']}
    b=d['opening'];b['other_nca']=latest['assets']-latest['current_assets']-b['ppe']-(b['fleet']or 0)-b['goodwill']-b['intangibles']-b['rou'];b['other_liab']=latest['liabilities']-b['debt']-b['ap'];b['finite']=d['latest_finite_intangibles'];b['indefinite']=b['intangibles']-b['finite']
    b['pool']=b['ppe']+b['finite'] if sym=='CROX' else b['ppe'];b['gross']=d.get('opening_fleet_gross_approx',0)
    d['globals']={'wacc':.10 if sym=='URI' else .11,'terminal_growth':.025 if sym=='URI' else .02,'min_cash':150 if sym=='URI' else 150,'leverage_limit':2.5 if sym=='URI' else 1.5,'terminal_roic':.10 if sym=='URI' else .15,'first_period_weight':11/12,'price':d['market']['price'],'share_price_growth':0,'new_asset_life':8.5 if sym=='URI' else 5,'salvage':.12 if sym=='URI' else 0,'first_year_principal':latest['debt_current'] or 0,'fixed_cost_fraction':.4,'other_cost_fraction':.75,'other_asset_life':5}
    ratio=lambda x,y:x/y
    drivers={
     'tax':{'base':[.25]*5 if sym=='URI' else [.20]*5,'down':[.25]*5 if sym=='URI' else [.22]*5,'up':[.25]*5 if sym=='URI' else [.18]*5,'basis':'Analyst normalized cash tax rate. No immediate cash refunds for losses.'},
     'interest':{'base':[.055]*5 if sym=='URI' else [.065]*5,'down':[.075]*5 if sym=='URI' else [.085]*5,'up':[.05]*5 if sym=='URI' else [.06]*5,'basis':'Analyst blended financing cost. Interest uses opening debt, with year-end financing timing.'},
     'dso':{'base':[365*latest['ar']/ttm['revenue']]*5,'down':[365*latest['ar']/ttm['revenue']+8]*5,'up':[365*latest['ar']/ttm['revenue']-3]*5,'basis':'Latest receivables / trailing revenue x 365. Scenario changes are assumptions.'},
     'dio':{'base':[365*latest['inventory']/ttm['cogs']]*5,'down':[365*latest['inventory']/ttm['cogs']+15]*5,'up':[365*latest['inventory']/ttm['cogs']-3]*5,'basis':'Latest inventory / trailing reported cost of revenue x 365; forecast cost denominator excludes D&A and disposal book cost.'},
     'dpo':{'base':[365*latest['ap']/ttm['cogs']]*5,'down':[365*latest['ap']/ttm['cogs']-5]*5,'up':[365*latest['ap']/ttm['cogs']+3]*5,'basis':'Latest payables / trailing reported cost of revenue x 365; forecast denominator follows forecast operating costs.'},
     'sbc':{'base':[ttm['sbc']/ttm['revenue']]*5,'down':[ttm['sbc']/ttm['revenue']]*5,'up':[ttm['sbc']/ttm['revenue']]*5,'basis':'Trailing reported stock compensation / revenue. Economic expense retained in DCF.'},
     'repurchases':{'base':[1500]*5 if sym=='URI' else [600]*5,'down':[750]*5 if sym=='URI' else [300]*5,'up':[2000]*5 if sym=='URI' else [800]*5,'basis':'Hypothetical annual repurchase ceiling, funded only after minimum cash and dividends.'},
     'dividends':{'base':[500]*5 if sym=='URI' else [0]*5,'down':[500]*5 if sym=='URI' else [0]*5,'up':[550]*5 if sym=='URI' else [0]*5,'basis':'Analyst distribution budget; not a future board declaration.'},
     'debt_sweep':{'base':[.5]*5 if sym=='URI' else [1]*5,'down':[1]*5,'up':[.5]*5 if sym=='URI' else [1]*5,'basis':'Fraction of remaining surplus directed to debt after the repurchase ceiling.'},
     'refinance':{'base':[1]*5,'down':[.75]*5,'up':[1]*5,'basis':'Hypothetical fraction of the repayment budget refinanced. Borrowing availability is not assured.'},
     'principal':{'base':[latest['debt_current']or 0,800,1500,1500,3000] if sym=='URI' else [0,100,850,0,350],'down':[latest['debt_current']or 0,800,1500,1500,3000] if sym=='URI' else [0,100,850,0,350],'up':[latest['debt_current']or 0,800,1500,1500,3000] if sym=='URI' else [0,100,850,0,350],'basis':'Repayment stress budget, not an instrument-level contractual maturity schedule. Year one uses latest current debt if disclosed; later years are analyst assumptions.'},
     'impairment':{'base':[0]*5,'down':[0]*5 if sym=='URI' else [200,0,0,0,0],'up':[0]*5,'basis':'Hypothetical noncash, nondeductible brand impairment. No forecast of an actual charge.'}}
    if sym=='URI':
     direct=ttm['rental']-(ttm['rental']-(annual['cogs']-annual['dep_fleet']-(annual['sales_fleet']-annual['gain_fleet']))) # replaced by exact reported rental operating cost below
     # Exact TTM direct rental cost is tagged separately in the filing extract.
     facts=json.loads((ROOT/'data/filing_facts.json').read_text())
     def directv(source,start,end):
      a=[x for x in facts if x['source_id']==source and x['name']=='us-gaap:DirectCostsOfLeasedAndRentedPropertyOrEquipment' and x.get('startdate')==start and x.get('enddate')==end and not x['dimensions']];return a[0]['value']/1e6
     d['base_direct_cost']=directv('URI-2025K','2025-01-01','2025-12-31')+directv('URI-2026Q3','2026-01-01','2026-09-30')-directv('URI-2026Q3','2025-01-01','2025-09-30')
     drivers.update({
      'productivity':{'base':[.03,.025,.02,.02,.02],'down':[-.08,-.04,0,.01,.02],'up':[.06,.05,.04,.03,.025],'basis':'Assumed change in rental yield after average OEC growth. Historical company productivity includes rate, time utilization and mix, not separately identifiable.'},
      'fleet_capex':{'base':[5350,5200,5200,5300,5400],'down':[4000,3500,3500,4000,4300],'up':[6000,6300,6600,6900,7200],'basis':'Cash fleet-purchase budget. First year is calibrated to 2026 cash-purchase guidance, not management guidance for these September-ending forecast periods.'},
      'other_capex':{'base':[400]*5,'down':[300]*5,'up':[450]*5,'basis':'Analyst cash investment in non-rental PPE; no future acquisition or intangible capitalization assumed.'},
      'disposal_book_rate':{'base':[(ttm['sales_fleet']-ttm['gain_fleet'])/latest['fleet']]*5,'down':[.055]*5,'up':[.04]*5,'basis':'Book value removed / opening net fleet. Base calibrated to trailing disposal proceeds less gains divided by latest net fleet.'},
      'disposal_accum':{'base':[.75]*5,'down':[.75]*5,'up':[.75]*5,'basis':'Analyst accumulated depreciation fraction on disposed original cost. Not disclosed by cohort.'},
      'sale_multiple':{'base':[ttm['sales_fleet']/(ttm['sales_fleet']-ttm['gain_fleet'])]*5,'down':[1.25]*5,'up':[1.9]*5,'basis':'Disposal proceeds / disposed net book value. Base trailing ratio, not an asset-level resale forecast.'},
      'legacy_dep':{'base':[ttm['dep_fleet']/latest['fleet']]*5,'down':[ttm['dep_fleet']/latest['fleet']]*5,'up':[ttm['dep_fleet']/latest['fleet']]*5,'basis':'Legacy annual depreciation rate on opening net book fleet. Cohort approximation calibrated to trailing D&A.'},
      'cost_inflation':{'base':[.03]*5,'down':[.04]*5,'up':[.025]*5,'basis':'Assumed inflation in the fixed 40% of rental operating costs.'},
      'maintenance':{'base':[0]*5,'down':[.02]*5,'up':[0]*5,'basis':'Additional rental operating cost as a revenue share. Scenario assumption; no estimated causal capex-to-maintenance relationship.'},
      'other_growth':{'base':[.03]*5,'down':[-.05,0,.02,.02,.02],'up':[.05]*5,'basis':'Growth in ancillary rental revenue and other non-rental revenue.'},
      'sga_rate':{'base':[ttm['sga']/ttm['revenue']]*5,'down':[ttm['sga']/ttm['revenue']+.01]*5,'up':[ttm['sga']/ttm['revenue']-.003]*5,'basis':'Reported trailing SG&A / revenue, including stock compensation.'}})
     d['legacy_ppe_dep_rate']=max(0,(ttm['da']-ttm['dep_fleet']-annual['amort'])/latest['ppe']);d['amort_budget']=[180,140,90,55,35]
    else:
     drivers.update({
      'crocs_dtc_growth':{'base':[.07,.06,.05,.04,.04],'down':[-.08,-.03,.01,.02,.03],'up':[.12,.10,.08,.06,.05],'basis':'Analyst growth path informed by disclosed DTC/channel trends; no customer-level conversion forecast.'},
      'crocs_wholesale_growth':{'base':[.02,.03,.03,.03,.03],'down':[-.10,-.05,0,.02,.02],'up':[.05,.05,.04,.04,.03],'basis':'Analyst wholesale revenue growth. Distributor inventory and consumer sell-through are not observed.'},
      'hey_dtc_growth':{'base':[.04,.05,.05,.04,.04],'down':[-.15,-.10,0,.02,.03],'up':[.10,.10,.08,.06,.05],'basis':'Analyst HEYDUDE DTC recovery scenario; growth is not assumed from one quarter alone.'},
      'hey_wholesale_growth':{'base':[.04,.05,.05,.04,.04],'down':[-.20,-.10,0,.02,.03],'up':[.12,.10,.08,.06,.05],'basis':'Analyst HEYDUDE wholesale scenario; no invented order-book data.'},
      'crocs_contribution':{'base':[.65]*5,'down':[.61]*5,'up':[.665]*5,'basis':'Analyst contribution margin before allocated D&A and SG&A. Calibrated to published brand gross margins plus aggregate D&A allocation, not a reported brand cash margin.'},
      'hey_contribution':{'base':[.46,.47,.48,.48,.48],'down':[.40,.40,.42,.43,.44],'up':[.49,.50,.51,.51,.51],'basis':'Analyst contribution margin before allocated D&A and SG&A; brand-level D&A is not separately disclosed.'},
      'sga_rate':{'base':[.38,.378,.375,.375,.375],'down':[.40]*5,'up':[.375,.37,.365,.36,.36],'basis':'Analyst recurring SG&A excluding modeled D&A under the analytical expense-allocation convention. Stock compensation remains expensed.'},
      'other_capex':{'base':[80]*5,'down':[65]*5,'up':[100]*5,'basis':'Hypothetical annual PPE/software cash budget calibrated to management 2026 capex guidance, not future company guidance.'},
      'legacy_dep':{'base':[ttm['da']/b['pool']]*5,'down':[ttm['da']/b['pool']]*5,'up':[ttm['da']/b['pool']]*5,'basis':'Trailing total D&A / latest PPE plus finite intangible asset pool. Avoids inventing an undisclosed D&A allocation.'}})
    d['drivers']=drivers
    return d

def simulate(d,case='base',overrides=None):
    sym=d['ticker'];g=d['globals'];a={k:list(v[case])for k,v in d['drivers'].items()};a.update(overrides or {});b=dict(d['opening']);t=d['ttm'];out=[];prior_avg_gross=b['gross'];rental=t.get('owned_rental',0);anc=t.get('rental',0)-rental;other=t['revenue']-t.get('rental',0)-t.get('sales_fleet',0) if sym=='URI' else 0;channels={k:t[k]for k in ['crocs_dtc','crocs_wholesale','hey_dtc','hey_wholesale']} if sym=='CROX' else {}
    for i in range(5):
        x={k:float(v[i])for k,v in a.items()};v={'year':2027+i,'opening_cash':b['cash'],'opening_debt':b['debt'],'opening_equity':b['equity'],'opening_shares':b['shares']};fleet_capex=0;book_disposal=0;proceeds=0;gain=0;fleet_da=0;amort=0
        if sym=='URI':
            fleet_capex=x['fleet_capex'];book_disposal=b['fleet']*x['disposal_book_rate'];gross_disposal=book_disposal/(1-x['disposal_accum']);closing_gross=b['gross']+fleet_capex-gross_disposal;average_gross=(b['gross']+closing_gross)/2
            rental=rental*(average_gross/prior_avg_gross)*(1+x['productivity']);anc*=1+x['other_growth'];other*=1+x['other_growth'];proceeds=book_disposal*x['sale_multiple'];gain=proceeds-book_disposal
            fleet_da=min(b['fleet']+fleet_capex-book_disposal,max(0,(b['fleet']-book_disposal/2)*x['legacy_dep']+fleet_capex*(1-g['salvage'])/g['new_asset_life']/2))
            rental_total=rental+anc;revenue=rental_total+proceeds+other;direct=d['base_direct_cost']*g['fixed_cost_fraction']*math.prod(1+a['cost_inflation'][j]for j in range(i+1))+rental_total*(d['base_direct_cost']/t['rental'])*(1-g['fixed_cost_fraction'])+rental_total*x['maintenance'];other_cost=other*g['other_cost_fraction'];cash_cogs=direct+other_cost;cost_before_da=cash_cogs+book_disposal+revenue*x['sga_rate'];ppe_da=min(b['ppe']+x['other_capex'],b['ppe']*d['legacy_ppe_dep_rate']+x['other_capex']/g['other_asset_life']/2);amort=min(b['finite'],d['amort_budget'][i]);da=fleet_da+ppe_da+amort
            closing_fleet=b['fleet']+fleet_capex-book_disposal-fleet_da;closing_pool=b['ppe']+x['other_capex']-ppe_da;closing_finite=b['finite']-amort;closing_intangibles=b['indefinite']+closing_finite
            v.update(owned_rental=rental,ancillary=anc,other_revenue=other,book_disposal=book_disposal,gross_disposal=gross_disposal,closing_gross=closing_gross,average_gross=average_gross,disposal_proceeds=proceeds,fleet_capex=fleet_capex,fleet_da=fleet_da,ppe_da=ppe_da,amort=amort,closing_fleet=closing_fleet,closing_ppe=closing_pool,closing_finite=closing_finite,closing_intangibles=closing_intangibles)
        else:
            for k in channels:channels[k]*=1+x[k+'_growth']
            crocs=channels['crocs_dtc']+channels['crocs_wholesale'];hey=channels['hey_dtc']+channels['hey_wholesale'];revenue=crocs+hey;cash_cogs=crocs*(1-x['crocs_contribution'])+hey*(1-x['hey_contribution']);cost_before_da=cash_cogs+revenue*x['sga_rate'];da=min(b['pool']+x['other_capex'],b['pool']*x['legacy_dep']+x['other_capex']/g['new_asset_life']/2);closing_pool=b['pool']+x['other_capex']-da;closing_fleet=0;closing_intangibles=b['indefinite']-x['impairment'];v.update(channels,closing_ppe=closing_pool,closing_fleet=0,closing_intangibles=closing_intangibles)
        ebitda=revenue-cost_before_da;ebit_rec=ebitda-da;ebit=ebit_rec-x['impairment'];interest=b['debt']*x['interest'];pretax=ebit-interest;tax=max(0,pretax+x['impairment'])*x['tax'];net=pretax-tax;sbc=revenue*x['sbc'];ar=revenue*x['dso']/365;inventory=cash_cogs*x['dio']/365;ap=cash_cogs*x['dpo']/365;delta_nwc=(ar+inventory-ap)-(b['ar']+b['inventory']-b['ap']);cfo=net+da+sbc+x['impairment']-gain-delta_nwc;cfi=-fleet_capex-x['other_capex']+proceeds;pre_fin=b['cash']+cfo+cfi;repay=min(b['debt'],x['principal']);refi=repay*x['refinance'];cash_after=pre_fin-repay+refi;new_borrowing=max(0,g['min_cash']-cash_after);surplus=max(0,cash_after-g['min_cash']);div=min(x['dividends'],surplus);buy=min(x['repurchases'],max(0,surplus-div));sweep=min(b['debt']-repay+refi+new_borrowing,max(0,surplus-div-buy)*x['debt_sweep']);closing_debt=b['debt']-repay+refi+new_borrowing-sweep;cff=refi+new_borrowing-repay-sweep-div-buy;cash=pre_fin+cff;equity=b['equity']+net+sbc-div-buy;shares=b['shares']+sbc/g['price']-buy/g['price'];other_assets=b['other_ca']+b['goodwill']+b['rou']+b['other_nca'];assets=cash+ar+inventory+other_assets+closing_pool+closing_fleet+closing_intangibles;liabilities=closing_debt+ap+b['other_liab'];ufcf=ebit_rec-max(0,ebit_rec)*x['tax']+da-gain-delta_nwc-fleet_capex-x['other_capex']+proceeds
        v.update(revenue=revenue,cash_cogs=cash_cogs,operating_costs=cost_before_da,ebitda=ebitda,da=da,ebit_rec=ebit_rec,impairment=x['impairment'],ebit=ebit,interest=interest,pretax=pretax,tax=tax,net_income=net,sbc=sbc,ar=ar,inventory=inventory,ap=ap,delta_nwc=delta_nwc,cfo=cfo,cfi=cfi,cff=cff,closing_cash=cash,mandatory_repayment=repay,refinancing=refi,new_borrowing_required=new_borrowing,surplus=surplus,dividends=div,buybacks=buy,debt_sweep=sweep,closing_debt=closing_debt,closing_equity=equity,closing_shares=shares,assets=assets,liabilities=liabilities,balance_check=assets-liabilities-equity,ufcf=ufcf,net_leverage=(closing_debt-cash)/ebitda if ebitda>0 else None,eps=net/((b['shares']+shares)/2))
        assert abs(v['balance_check'])<1e-8,(sym,case,i,v['balance_check'])
        out.append(v);b.update(cash=cash,ar=ar,inventory=inventory,ap=ap,debt=closing_debt,equity=equity,shares=shares,fleet=closing_fleet,ppe=closing_pool,pool=closing_pool,intangibles=closing_intangibles)
        if sym=='URI':b.update(gross=closing_gross,finite=closing_finite);prior_avg_gross=average_gross
        else:b['indefinite']=closing_intangibles
    return out

def valuation(d,rows,wacc=None,growth=None,tax=None):
    g=d['globals'];w=g['wacc']if wacc is None else wacc;tg=g['terminal_growth']if growth is None else growth
    if w<=tg:raise ValueError('WACC must exceed terminal growth')
    tr=d['drivers']['tax']['base'][-1]if tax is None else tax
    first=g['first_period_weight'];pv=sum(r['ufcf']*(first if i==0 else 1)/(1+w)**(i+first)for i,r in enumerate(rows));terminal_ebit=rows[-1]['ebit_rec']*(1+tg);terminal_nopat=terminal_ebit*(1-tr);terminal_fcf=terminal_nopat*(1-tg/g['terminal_roic']);tv=terminal_fcf/(w-tg);pvtv=tv/(1+w)**(4+first);ev=pv+pvtv;netdebt=d['opening']['debt']-d['opening']['cash'];equity=ev-netdebt;market_ev=g['price']*d['market']['shares_millions']+netdebt;required_terminal_fcf=(market_ev-pv)*(1+w)**(4+first)*(w-tg);required_nopat=required_terminal_fcf/(1-tg/g['terminal_roic']);required_margin=required_nopat/(rows[-1]['revenue']*(1+tg)*(1-tr));return dict(ev=ev,equity=equity,per_share=equity/d['market']['shares_millions'],terminal_share=pvtv/ev,pv_cashflows=pv,terminal_value=tv,implied_terminal_ebit_margin=required_margin,market_ev=market_ev)

def main():
    for sym in ['URI','CROX']:
        d=inputs(sym);(ROOT/f'data/{sym}_model.json').write_text(json.dumps(d,indent=2)+'\n');result={}
        for case in ['base','down','up']:
            rows=simulate(d,case);result[case]={'forecast':rows,'valuation':valuation(d,rows,tax=d['drivers']['tax'][case][-1])}
        (ROOT/f'outputs/{sym}_reference.json').write_text(json.dumps(result,indent=2)+'\n');print(sym,[(k,round(v['forecast'][0]['revenue'],1),round(v['forecast'][0]['new_borrowing_required'],1),round(v['valuation']['per_share'],2))for k,v in result.items()])
if __name__=='__main__':main()
