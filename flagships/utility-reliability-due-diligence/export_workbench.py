"""Create an offline workbench from the same audited API resources."""
from pathlib import Path
import json
from app import resources
from analysis import read_panel
ROOT=Path(__file__).resolve().parent
def main():
    review,metrics=resources()
    history=[{k:r[k] for k in ['year','utility_id','state','standard','customers','saidi_normal']} for r in read_panel() if (r['customers'] or 0)>0]
    data=json.dumps(dict(review=review,metrics=metrics,history=history),ensure_ascii=True,allow_nan=False).replace('</','<\\/')
    replacement='''const OFFLINE=DATA_PLACEHOLDER;
async function request(url){
const u=new URL(url,'https://offline.invalid');const p=u.searchParams;
if(u.pathname==='/api/status')return OFFLINE.metrics;
if(u.pathname==='/api/utilities'){const rows=OFFLINE.review.filter(r=>(!p.get('state')||r.state===p.get('state'))&&(!p.get('ownership')||r.ownership===p.get('ownership'))&&(!p.get('q')||(r.utility_name+' '+r.utility_id).toLowerCase().includes(p.get('q').toLowerCase())));return {rows,states:[...new Set(OFFLINE.review.map(r=>r.state))].sort(),ownerships:[...new Set(OFFLINE.review.map(r=>r.ownership))].sort(),view_year:OFFLINE.metrics.decision_view_year}}
const row=OFFLINE.review.find(r=>r.utility_id===p.get('utility_id')&&r.state===p.get('state'));if(!row)throw Error('Select an eligible utility-state row');
if(u.pathname==='/api/history')return {rows:OFFLINE.history.filter(r=>r.utility_id===Number(row.utility_id)&&r.state===row.state),decision_view_year:OFFLINE.metrics.decision_view_year,quarantined_years:OFFLINE.metrics.quarantined_years};
if(u.pathname==='/api/scenario'){const reduction=Number(p.get('reduction')),value=Number(p.get('hour_value')),opex=Number(p.get('opex')),rate=Number(p.get('rate')),years=Number(p.get('years')),capex=Number(p.get('capex'));if(![reduction,value,opex,rate,years,capex].every(Number.isFinite)||reduction<0||reduction>1||value<0||opex<0||rate<0||!Number.isInteger(years)||years<1||years>100||capex<0)throw Error('Invalid scenario assumptions');const hours=Number(row.saidi_normal)*Number(row.customers)*reduction/60;let factor=0;for(let t=1;t<=years;t++)factor+=1/(1+rate)**t;const threshold=(hours*value-opex)*factor;return {break_even_upfront_cost_usd:threshold,proposed_capex_usd:capex,conditional_surplus_usd:threshold-capex,annual_customer_hours_avoided_proxy:hours,warning:'Hypothetical social-value screen; effectiveness and outage valuation are assumptions, not EIA estimates. No investment recommendation or utility cash-flow valuation.'}}
throw Error('Unknown endpoint')}
'''.replace('DATA_PLACEHOLDER',data)
    page=(ROOT/'index.html').read_text()
    original="async function request(url){const r=await fetch(url);const v=await r.json();if(!r.ok)throw Error(v.error||'Request failed');return v}"
    if original not in page:raise ValueError('Client API boundary changed; update exporter')
    page=page.replace(original,replacement).replace('EIA DATA · ANALYST WORKBENCH · SOURCE TRACEABLE','EIA DATA · OFFLINE ANALYST WORKBENCH · SOURCE TRACEABLE')
    (ROOT/'outputs/workbench.html').write_text(page)
    print('Offline workbench exported')
if __name__=='__main__':main()
