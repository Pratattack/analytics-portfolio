'use strict';
function requiredRaise(inflation,hours,target){
  if(![inflation,hours,target].every(Number.isFinite)||inflation<=-1||hours<=-1||target<=-1)throw new RangeError('Invalid scenario');
  return (1+inflation)*(1+target)/(1+hours)-1;
}
if(typeof module!=='undefined')module.exports={requiredRaise};
if(typeof document!=='undefined'){
 const form=document.querySelector('#budget');
 function update(){const result=document.querySelector('#result');if(!form.checkValidity()){result.textContent='Enter values within the stated ranges.';document.querySelector('#explain').textContent='';return;}
 const values=['inflation','hours','target'].map(id=>Number(document.getElementById(id).value)/100);
 const r=requiredRaise(...values);result.textContent=`Required hourly pay change: ${(r*100).toFixed(2)}%`;
 document.querySelector('#explain').textContent=`A $30 hourly wage would become $${(30*(1+r)).toFixed(2)} under these assumptions. This is an illustration, not an observed wage.`;}
 form.addEventListener('input',update);form.addEventListener('submit',e=>e.preventDefault());update();
}
