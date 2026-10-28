const a=require('node:assert/strict');const {fuelBudget:f}=require('./outputs/calculator.js');
let r=f(4,100000,.1,.2);a.ok(Math.abs(r.budget-440000)<1e-8);a.equal(r.actual,480000);a.ok(Math.abs(r.shortfall-40000)<1e-8);a.equal(r.unused,0);
r=f(4,100000,.1,-.2);a.equal(r.shortfall,0);a.ok(Math.abs(r.unused-120000)<1e-8);
for(const v of [[0,1,0,0],[4,-1,0,0],[4,1,-.1,0],[4,1,0,-1],[NaN,1,0,0]])a.throws(()=>f(...v),RangeError);
console.log('11 fuel calculator arithmetic and boundary checks passed');
