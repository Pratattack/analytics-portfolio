'use strict';
const data=JSON.parse(document.getElementById('project-data').textContent);
const semi=data.kind==='semi';const $=id=>document.getElementById(id);
const usd=v=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(v);
const num=x=>Number(x);
function calc(){
 $('error').textContent='';$('scenario').replaceChildren();
 const aInput=$('assumptionA'),bInput=$('assumptionB');
 if(aInput.value.trim()===''||bInput.value.trim()===''||!aInput.checkValidity()||!bInput.checkValidity()){$('error').textContent='Enter finite values within the stated input limits.';return;}
 const a=num(aInput.value),b=num(bInput.value);
 if(!Number.isFinite(a)||!Number.isFinite(b)){$('error').textContent='Enter finite values within the stated input limits.';return;}
 const r=data.latest.find(r=>r.ticker===$('issuer').value);let values,description;
 if(semi){
  if(r.status==='STALE_OR_GAPPED'){$('error').textContent=`${r.ticker}: current coherent data are unavailable. Latest admitted period ${r.end}; scenario blocked.`;return;}
  const candidate=$('basis').value==='candidate';
  const planning=(candidate?Math.max(num(r.forecast),num(r.upper90)):num(r.inventory))*(1+b/100);
  values=[['Planning inventory balance',planning],['Change from admitted balance',planning-num(r.inventory)],['Quarterly carrying cost',planning*a/400]];
  description=`${r.ticker} · balance date ${r.end} · ${candidate?'Rejected-model diagnostic, not approved for planning.':'Last-balance baseline; buffer and carrying cost are assumptions.'} This is inventory funding exposure, not measured cash required or realized savings.`;
 }else{
  const cfo=num(r.cfo)*(1+a/100),capex=num(r.capex)*b/100;
  values=[['Conditional buyback capacity',Math.max(0,cfo-capex-num(r.dividends))],['Residual after observed cash returns',cfo-capex-num(r.dividends)-num(r.buybacks)],['Assumed capital expenditure',capex]];
  description=`${r.ticker} · FY ${r.end.slice(0,4)} base · Conditional capacity after dividends, before acquisitions, other financing, liquidity and safety constraints. It is not a buyback authorization.`;
 }
 const p=document.createElement('p');p.textContent=description;$('scenario').appendChild(p);
 const cards=document.createElement('div');cards.className='cards';
 values.forEach(([label,value])=>{const c=document.createElement('div');c.className='card';const l=document.createElement('div');l.className='label';l.textContent=label;const v=document.createElement('div');v.className='value scenario-value';v.dataset.value=String(value);v.textContent=usd(value);c.append(l,v);cards.append(c);});$('scenario').appendChild(cards);
}
function table(){
 const q=$('search').value.toLowerCase().trim();const rows=data.latest.filter(r=>(r.ticker+' '+(r.status||'annual')).toLowerCase().includes(q));
 const headings=semi?['Issuer','Admitted period','Inventory at cost','Days proxy','Gate']:['Issuer','Annual base','CFO','Capex','Cash returns','Residual'];
 $('decisions').tHead.innerHTML='';const h=document.createElement('tr');headings.forEach(x=>{const th=document.createElement('th');th.scope='col';th.textContent=x;h.appendChild(th);});$('decisions').tHead.appendChild(h);
 const body=$('decisions').tBodies[0];body.replaceChildren();
 rows.forEach(r=>{const values=semi?[r.ticker,r.end,usd(num(r.inventory)),num(r.inventory_days_proxy).toFixed(1),r.status]:[r.ticker,r.end,usd(num(r.cfo)),usd(num(r.capex)),usd(num(r.dividends)+num(r.buybacks)),usd(num(r.distribution_gap))];const tr=document.createElement('tr');values.forEach((x,i)=>{const td=document.createElement('td');td.textContent=x;if(i>1)td.className='num';tr.appendChild(td);});body.appendChild(tr);});
 $('count').textContent=rows.length?`${rows.length} issuer records. Dates and exclusions are part of the decision.`:'No issuers match. Clear the search to recover.';
}
$('calculate').addEventListener('click',calc);$('issuer').addEventListener('change',calc);if(semi)$('basis').addEventListener('change',calc);
$('reset').addEventListener('click',()=>{$('issuer').selectedIndex=0;$('assumptionA').value=semi?'10':'0';$('assumptionB').value=semi?'0':'100';if(semi)$('basis').value='baseline';$('search').value='';document.querySelector('.scroll').scrollLeft=0;table();calc();});
$('search').addEventListener('input',table);['assumptionA','assumptionB'].forEach(id=>$(id).addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();calc();}}));
table();calc();
