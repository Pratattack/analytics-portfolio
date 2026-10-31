'use strict';
const D=JSON.parse(document.getElementById('dataset').textContent),M=ContractModel;
const byId=Object.fromEntries(D.plans.map(p=>[p.id,p])),el=id=>document.getElementById(id);
const money=v=>v.toLocaleString('en-US',{style:'currency',currency:'USD'});
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let monthlyRows=[],scenarioRows=[];
function chosen(){return D.plans.filter(p=>(!el('october').checked||p.efl_date>='2026-10-01')&&(!p.prepaid||el('prepaid').checked));}
function validUsage(v){return Number.isFinite(v)&&v>=250&&v<=4500;}
function monthly(){
 const q=Number(el('usage').value);if(!validUsage(q)){el('usage').setAttribute('aria-invalid','true');el('monthly-status').textContent='Enter usage between 250 and 4,500 kWh.';el('ranking').innerHTML='';monthlyRows=[];return;}el('usage').removeAttribute('aria-invalid');el('usage-slider').value=q;
 const norm=el('basis').value==='normalized';el('basis-note').textContent=norm?'Common basis: $4.90 per cycle plus 6.5333 cents/kWh. Historical energy terms remain historical.':'As-issued basis: each label retains its original delivery charges. Different dates are not directly comparable current offers.';
 const rows=chosen().map(p=>({p,b:M.bill(p,q,30,norm)})).sort((a,b)=>a.b.total-b.b.total);
 el('monthly-status').textContent=`${rows.length} selected contracts at ${q.toLocaleString()} kWh. Research sample only; all costs exclude taxes and nonrecurring fees.`;
 monthlyRows=rows.map(({p,b})=>({plan:p.name,provider:p.provider,efl_date:p.efl_date,kwh:q,delivery_basis:norm?'common_october':'as_issued',cost_dollars:b.total,credit_dollars:b.credit,term_months:p.term_months}));
 el('ranking').innerHTML=rows.map(({p,b})=>`<tr><td><strong>${esc(p.name)}</strong><small>${esc(p.provider)} · ${p.efl_date}${p.efl_date<'2026-10-01'?' · HISTORICAL':''}</small></td><td class="money">${money(b.total)}</td><td>${b.effective_cents.toFixed(2)}¢/kWh</td><td>${money(b.credit)}</td><td>${p.term_months} months<small>${p.prepaid?'Prepaid':'Postpaid'}</small></td></tr>`).join('');scenario();
}
function curve(){
 const svg=el('curve'),left=70,right=875,top=20,bottom=340;
 const x=q=>left+(q-250)/(4500-250)*(right-left),y=v=>bottom-v/900*(bottom-top);
 let s='<title id="curve-title">Monthly cost curves with a bill credit threshold</title><desc id="curve-desc">The credit plan drops at 1,000 kWh and crosses the basic plan again near 3,871 kWh. Contracts have different durations.</desc>';
 for(const v of [0,200,400,600,800])s+=`<line x1="${left}" x2="${right}" y1="${y(v)}" y2="${y(v)}" stroke="#34465e"/><text x="60" y="${y(v)+5}" fill="#b2c3d8" text-anchor="end" font-size="14">$${v}</text>`;
 for(const q of [500,1000,2000,3000,4000])s+=`<text x="${x(q)}" y="365" fill="#b2c3d8" text-anchor="middle" font-size="14">${q.toLocaleString()}</text>`;
 for(const [id,color,segments] of [['discount-basic-36','#65c9ff',[[250,4500]]],['discount-credit-12','#ffd38b',[[250,999],[1000,4500]]]]){
  for(const [a,b] of segments){const pts=[];for(let q=a;q<b;q+=10)pts.push(`${x(q)},${y(M.bill(byId[id],q,30,true).total)}`);pts.push(`${x(b)},${y(M.bill(byId[id],b,30,true).total)}`);s+=`<polyline points="${pts.join(' ')}" fill="none" stroke="${color}" stroke-width="3"/>`;}
 }
 s+=`<line x1="${x(1000)}" x2="${x(1000)}" y1="${top}" y2="${bottom}" stroke="#b2c3d8" stroke-dasharray="4 6"/><text x="${x(1000)+10}" y="38" fill="#ffd38b" font-size="14">Credit begins</text><text x="470" y="395" text-anchor="middle" fill="#b2c3d8" font-size="14">Electricity per billing cycle (kWh)</text>`;svg.innerHTML=s;
}
function setProfile(){let p=D.profiles.find(p=>p.id===el('profile').value)||D.profiles[0];el('profile-inputs').innerHTML=p.usage.map((q,i)=>`<label for="cycle-${i}">Cycle ${i+1}<input id="cycle-${i}" type="number" min="250" max="4500" step="1" value="${q}"></label>`).join('');el('profile-inputs').querySelectorAll('input').forEach(x=>x.addEventListener('input',scenario));scenario();}
function scenario(){
 const inputs=[...el('profile-inputs').querySelectorAll('input')];if(!inputs.length)return;const usage=inputs.map(x=>Number(x.value));let valid=true;inputs.forEach((x,i)=>{if(!validUsage(usage[i])){x.setAttribute('aria-invalid','true');valid=false;}else x.removeAttribute('aria-invalid');});
 if(!valid){el('scenario-status').textContent='Each cycle must contain 250 to 4,500 kWh.';el('scenario-ranking').innerHTML='';scenarioRows=[];return;}
 const rows=chosen().filter(p=>p.term_months>=12).map(p=>({p,b:M.twelveCycles(p,usage)})).sort((a,b)=>a.b.total-b.b.total);
 el('scenario-status').textContent=`${usage.reduce((a,b)=>a+b,0).toLocaleString()} kWh across 12 hypothetical 30-day cycles. ${rows.length} contracts cover the horizon. Common October delivery charges are used here regardless of the monthly basis selector.`;
 scenarioRows=rows.map(({p,b})=>({plan:p.name,provider:p.provider,efl_date:p.efl_date,total_kwh:usage.reduce((a,b)=>a+b,0),hypothetical_cost_dollars:b.total,credit_cycles:b.credit_cycles,credit_dollars:b.credits,usage_kwh:usage.join('|')}));
 el('scenario-ranking').innerHTML=rows.map(({p,b})=>`<tr><td>${esc(p.name)}<small>${p.term_months} months · ${p.efl_date}${p.efl_date<'2026-10-01'?' · HISTORICAL':''}</small></td><td class="money">${money(b.total)}</td><td>${b.credit_cycles}/12</td><td>${money(b.credits)}</td></tr>`).join('');
}
function csv(rows,name){if(!rows.length)return;const keys=Object.keys(rows[0]),quote=v=>'"'+String(v).replace(/"/g,'""')+'"';const blob=new Blob([[keys,...rows.map(r=>keys.map(k=>r[k]))].map(r=>r.map(quote).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
el('usage').addEventListener('input',monthly);el('usage-slider').addEventListener('input',()=>{el('usage').value=el('usage-slider').value;monthly();});['basis','october','prepaid'].forEach(id=>el(id).addEventListener('change',monthly));
el('profile').innerHTML=D.profiles.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('');el('profile').addEventListener('change',setProfile);
el('sources').innerHTML=D.plans.map(p=>{const s=D.sources.find(s=>s.id===p.source_id);return `<h3>${esc(p.provider)}: ${esc(p.name)}</h3><p class="small"><a href="${esc(s.url)}" target="_blank" rel="noopener">Provider label, ${p.efl_date}</a> · Pricing: page 1 · ${p.term_months} months</p><p class="small">${esc(p.requirements)} ${esc(p.notes)} Standard early exit charge: ${p.termination_flat?money(p.termination_flat):money(p.termination_per_remaining_month)+' per remaining month'}. Applicable move exceptions require provider verification.</p>`;}).join('');
el('export-monthly').addEventListener('click',()=>csv(monthlyRows,'monthly-comparison.csv'));el('export-scenario').addEventListener('click',()=>csv(scenarioRows,'hypothetical-scenario.csv'));setProfile();monthly();curve();
