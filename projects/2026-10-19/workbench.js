'use strict';
const data = JSON.parse(document.querySelector('#data').textContent);
const $ = id => document.getElementById(id);
const number = id => {const text=$(id).value.trim();const n=Number(text);if(!text || !Number.isFinite(n))throw Error('Enter a finite number for every required assumption.');return n;};
const usd = n => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const fmt = (n,d=2) => Number(n).toLocaleString('en-US',{maximumFractionDigits:d,minimumFractionDigits:d});
function table(headers, rows){
  $('head').replaceChildren();$('body').replaceChildren();const tr=document.createElement('tr');
  headers.forEach(s=>{const th=document.createElement('th');th.textContent=s;th.scope='col';tr.append(th);});$('head').append(tr);
  rows.forEach(row=>{const tr=document.createElement('tr');row.forEach(value=>{const td=document.createElement('td');td.textContent=String(value);tr.append(td);});$('body').append(tr);});
}
function cards(values){$('results').replaceChildren();const list=document.createElement('div');list.className='cards';values.forEach(([label,value])=>{const box=document.createElement('div');box.className='card';const l=document.createElement('div');l.textContent=label;const v=document.createElement('div');v.className='value';v.textContent=value;box.append(l,v);list.append(box);});$('results').append(list);}
function airline(){
  const slots=number('slots'),cap=number('cap'),price=number('price'),fraction=number('fraction')/100,sitecost=number('sitecost');
  if(!Number.isInteger(slots)||slots<1||slots>20)throw Error('Investigation slots must be an integer from 1 to 20.');
  if(!Number.isInteger(cap)||cap<1||cap>4)throw Error('Airport capacity must be an integer from 1 to 4.');
  if(price<=0||fraction<0||fraction>1||sitecost<0)throw Error('Use a positive minute cost, 0–100% recoverability, and nonnegative site cost.');
  const search=$('search').value.trim().toUpperCase(), index=$('policy').value==='peer'?2:3;
  const candidates=data.sites.filter(r=>(r[0]+' '+r[1]).includes(search)).sort((a,b)=>b[index]-a[index]||(a[0]+a[1]).localeCompare(b[0]+b[1]));
  const counts={},selected=[];
  for(const r of candidates){if(r[index]>0 && (counts[r[1]]||0)<cap && selected.length<slots){selected.push(r);counts[r[1]]=(counts[r[1]]||0)+1;}}
  const observed=selected.filter(r=>r[4]!==null),signed=observed.reduce((s,r)=>s+r[4],0);
  const denominator=data.sites.reduce((s,r)=>s+(r[4]===null?0:Math.max(0,r[4])),0);
  const capture=denominator?100*observed.reduce((s,r)=>s+Math.max(0,r[4]),0)/denominator:0;
  const net=Math.max(0,signed)*price*fraction-selected.length*sitecost;
  cards([['Selected investigations',String(selected.length)],['2026 positive-excess capture',fmt(capture)+'%'],['Hypothetical net value',usd(net)]]);
  $('status').textContent=candidates.length?`${candidates.length} matching discovery sites; ${observed.length} selected sites have 2026 observations. Capture uses the complete original eligible pool, not only the search matches.`:'No sites match. Change the search or reset assumptions.';
  table(['Carrier','Airport','2024 score (minutes)','2026 signed excess','2026 months'],selected.map(r=>[r[0],r[1],fmt(r[index],0),r[4]===null?'Not observed':fmt(r[4],0),r[6]]));
}
function banking(){
  const balance=number('balance'),rate=number('rate')/100,cut=number('cut')/10000,share=number('share')/100,loss=number('loss')/100,replacement=number('replacement')/100,fixed=number('fixed');
  if(balance<0||rate<0||cut<0||cut>rate)throw Error('Use nonnegative balances and rates; the rate cut cannot exceed the current rate.');
  if(share<0||share>1||loss<0||loss>1||replacement<0||fixed<0)throw Error('Target share and attrition must be 0–100%; replacement rate and fixed cost must be nonnegative.');
  const targeted=balance*share,savings=targeted*(1-loss)*cut,extra=targeted*loss*(replacement-rate),net=savings-extra-fixed,denominator=cut+replacement-rate;
  const threshold=targeted>0&&denominator>0?(cut-fixed/targeted)/denominator:null;
  cards([['Hypothetical annual net',usd(net)],['Retained-balance savings',usd(savings)],['Break-even attrition',threshold===null?'Not defined':fmt(100*threshold)+'%']]);
  const banks=data.banks.filter(r=>$('bucket').value==='all'||r.asset_bucket===$('bucket').value);
  $('status').textContent=`Showing ${banks.length} of ${data.banks.length} selected review-queue banks, not all ${data.metrics.matched_screened_banks} cohort banks. All calculator inputs are hypothetical.`;
  table(['Certificate','Bank','Asset bucket','Proxy-rate contribution ($000)','Peer gap (bp)'],banks.map(r=>[r.cert,r.name,r.asset_bucket,fmt(r.proxy_rate_contribution_thousand_usd),fmt(r.peer_rate_gap_bp)]));
}
function render(){try{$('error').textContent='';data.kind==='airline'?airline():banking();}catch(error){$('error').textContent=error.message;$('results').replaceChildren();$('body').replaceChildren();$('status').textContent='Correct the assumptions to continue. No calculation is shown for invalid inputs.';}}
const m=data.metrics;
$('observed').textContent=data.kind==='airline'?`${m.source_rows.toLocaleString()} source rows; ${m.quarantined_rows} quarantined. Fixed priorities capture ${fmt(m.strict_diagnostic.positive_excess_capture_pct)}% of positive peer excess in Jan–Aug 2026. Prospective deployment is not approved.`:`${m.source_rows.toLocaleString()} bank-quarters; ${m.matched_screened_banks.toLocaleString()} screened banks. Observed quarterly expense change: ${usd(m.change_thousand_usd*1000)}. Source population is insured domestic banking; this is accounting attribution, not a causal estimate.`;
$('controls').addEventListener('submit',event=>event.preventDefault());$('controls').addEventListener('input',render);$('controls').addEventListener('change',render);$('controls').addEventListener('reset',()=>setTimeout(render,0));render();
