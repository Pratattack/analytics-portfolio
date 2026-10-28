'use strict';
const fs=require('node:fs'),path=require('node:path'),a=require('node:assert/strict');
const root=path.resolve(__dirname,'..');const {evaluateScenario,loanPayment}=require('../outputs/model.js');
const defaults=JSON.parse(fs.readFileSync(path.join(root,'data/default_assumptions.json'))),report=JSON.parse(fs.readFileSync(path.join(root,'data/report_estimates.json'))),fixtures=JSON.parse(fs.readFileSync(path.join(root,'outputs/parity_fixtures.json')));
let numbers=0;
function compare(actual,expected,label){
 if(typeof expected==='number'){a.equal(typeof actual,'number',label);a.ok(Number.isFinite(actual),label);a.ok(Math.abs(actual-expected)<=1e-5+Math.abs(expected)*1e-10,`${label}: ${actual} != ${expected}`);numbers++;}
 else if(Array.isArray(expected)){a.equal(actual.length,expected.length,label);expected.forEach((v,i)=>compare(actual[i],v,label+'['+i+']'));}
 else if(expected&&typeof expected==='object'){a.deepEqual(Object.keys(actual).sort(),Object.keys(expected).sort(),label);for(const k of Object.keys(expected))compare(actual[k],expected[k],label+'.'+k);}
 else a.equal(actual,expected,label);
}
fixtures.forEach((f,i)=>compare(evaluateScenario(f.config,defaults,report),f.result,'fixture '+i));
a.ok(Math.abs(loanPayment(100000,.06,30)-599.5505251527569)<1e-8);
for(const patch of [{loan_to_cost:1},{lottery_commission:.01},{ramp_months:0},{hard_cost:NaN},{scope:'bad'},{permit_delay_months:1.5}])a.throws(()=>evaluateScenario({...defaults,...patch},defaults,report));
console.log(JSON.stringify({parity_cases:fixtures.length,numerical_values_reconciled:numbers,invalid_input_cases:6,known_annuity_value:true}));
