'use strict';
function fuelBudget(price,gallons,reserve,stress){
 if(![price,gallons,reserve,stress].every(Number.isFinite)||price<=0||gallons<=0||reserve<0||stress<=-1)throw new RangeError('Invalid scenario');
 const base=price*gallons,budget=base*(1+reserve),actual=base*(1+stress);
 return {base,budget,actual,shortfall:Math.max(0,actual-budget),unused:Math.max(0,budget-actual)};
}
if(typeof module!=='undefined')module.exports={fuelBudget};
if(typeof document!=='undefined'){
 const form=document.querySelector('#budget');const money=v=>v.toLocaleString('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0});
 function update(){const result=document.querySelector('#result');if(!form.checkValidity()){result.textContent='Enter values within the stated ranges.';document.querySelector('#explain').textContent='';return;}
 const v=['price','gallons','reserve','stress'].map(id=>Number(document.getElementById(id).value));const r=fuelBudget(v[0],v[1],v[2]/100,v[3]/100);
 result.textContent=`Budget: ${money(r.budget)} | Stress cost: ${money(r.actual)}`;document.querySelector('#explain').textContent=`Base cost ${money(r.base)}. Shortfall ${money(r.shortfall)}. Unused budget ${money(r.unused)}. These are hypothetical costs, not company results or savings.`;}
 form.addEventListener('input',update);form.addEventListener('submit',e=>e.preventDefault());update();
}
