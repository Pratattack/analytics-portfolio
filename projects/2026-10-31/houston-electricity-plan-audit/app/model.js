/* Independent implementation checked against Python results. */
(function(root){
'use strict';
function bill(p,q,days=30,normalized=false){
 if(!Number.isFinite(q)||q<=0||!Number.isFinite(days)||days<1||days>31)throw Error('Invalid usage or billing days');
 const delivery=normalized?6.5333:p.delivery_cents;
 const fixed=(normalized?4.9:p.delivery_dollars)*(p.prepaid?Math.min(days/30,1):1);
 let credit=0;
 if(p.credit_rule==='gte'&&q>=p.credit_threshold)credit=p.credit_dollars;
 if(p.credit_rule==='lte'&&q<=p.credit_threshold)credit=p.credit_dollars*Math.min(days/30,1);
 const total=q*(p.energy_cents+delivery)/100+p.base_dollars+days*p.daily_dollars+fixed-credit;
 return{total,credit,effective_cents:total/q*100};
}
function twelveCycles(p,usage){
 if(usage.length!==12||p.term_months<12)throw Error('Contract does not cover horizon');
 const rows=usage.map(q=>bill(p,q,30,true));
 return{total:rows.reduce((s,x)=>s+x.total,0),credits:rows.reduce((s,x)=>s+x.credit,0),credit_cycles:rows.filter(x=>x.credit>0).length};
}
const api={bill,twelveCycles};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ContractModel=api;
})(typeof globalThis!=='undefined'?globalThis:this);
