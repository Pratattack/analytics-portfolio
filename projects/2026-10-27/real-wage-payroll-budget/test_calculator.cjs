const a=require('node:assert/strict');const {requiredRaise:r}=require('./outputs/calculator.js');
const near=(x,y)=>a.ok(Math.abs(x-y)<1e-12);
near(r(0,0,0),0);near(r(.04,0,.01),.0504);near(r(.04,-.02,.01),1.0504/.98-1);near(r(-.02,0,0),-.02);
for(const values of [[NaN,0,0],[0,-1,0],[0,0,-1]])a.throws(()=>r(...values),RangeError);
console.log('7 wage calculator identity and boundary checks passed');
