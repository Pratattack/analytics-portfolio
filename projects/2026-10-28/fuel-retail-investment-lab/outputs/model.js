/* Original scenario model. No external services, analytics or browser storage. */
'use strict';
function loanPayment(principal,annual,years){if(principal===0)return 0;const r=annual/12,n=years*12;return r===0?principal/n:principal*r/(1-Math.pow(1+r,-n));}
function checkConfig(c,defaults,report){
 if(Object.keys(c).sort().join('|')!==Object.keys(defaults).sort().join('|'))throw Error('Input schema mismatch');
 if(!Object.hasOwn(report.scenarios,c.report_scenario)||!['core','full'].includes(c.scope)||!['report','traffic'].includes(c.fuel_source))throw Error('Unknown scenario selection');
 for(const [k,v] of Object.entries(c))if(typeof defaults[k]==='number'&&(typeof v!=='number'||!Number.isFinite(v)||v<0))throw Error('Invalid '+k);
 for(const k of ['eligible_traffic_share','capture_rate','store_margin','deli_margin','pizza_margin','lottery_commission','nonfuel_card_fee','payroll_load','contingency_rate','loan_to_cost','annual_interest_rate','loan_fee_rate','ramp_start','wash_margin'])if(c[k]>1)throw Error('Fraction outside [0,1]: '+k);
 for(const k of ['construction_months','permit_delay_months','ramp_months','amortization_years'])if(!Number.isInteger(c[k]))throw Error('Whole number required: '+k);
 if(c.lottery_commission<.05)throw Error('Lottery commission is below the verified 5% minimum');
 if(c.loan_to_cost>.95||c.construction_months<1||c.construction_months>60||c.permit_delay_months>36||c.ramp_months<1||c.ramp_months>36||c.amortization_years<1||c.amortization_years>40||c.target_dscr<=0||c.target_dscr>5||c.hours_open_per_day>24||c.average_staff_on_duty>20||c.sales_multiplier>5||c.net_fuel_margin>5)throw Error('Input outside supported range');
}
function stabilized(c,defaults,report){
 checkConfig(c,defaults,report);const a=report.scenarios[c.report_scenario],z=c.sales_multiplier,w=c.scope==='full',days=365/12;
 const gallons=(c.fuel_source==='report'?a.fuel_gallons:c.aadt*c.eligible_traffic_share*c.capture_rate*c.gallons_per_transaction*days)*z;
 const store=a.store_sales*z,deli=a.deli_sales*z,pizza=a.pizza_sales*z,lottery=a.lottery_ticket_sales*z,wash=w?c.wash_sales_monthly*z:0;
 const fuel=gallons*c.net_fuel_margin,lotto=lottery*c.lottery_commission,storeGP=store*c.store_margin,deliGP=deli*c.deli_margin,pizzaGP=pizza*c.pizza_margin,washGP=wash*c.wash_margin;
 const nonfuel=store+deli+pizza+lottery+wash,retained=nonfuel-lottery+lotto,cogs=store*(1-c.store_margin)+deli*(1-c.deli_margin)+pizza*(1-c.pizza_margin)+wash*(1-c.wash_margin),fees=(store+deli+pizza+wash)*c.nonfuel_card_fee;
 const wage=c.hourly_wage*(1+c.payroll_load),labor=c.hours_open_per_day*days*c.average_staff_on_duty*wage+(w?c.wash_extra_labor_hours_monthly*wage:0),maintenance=c.maintenance_reserve_monthly+(w?c.wash_maintenance_monthly:0);
 const contribution=fuel+lotto+storeGP+deliGP+pizzaGP+washGP-fees,fixed=labor+c.fixed_opex_monthly+maintenance,cfads=contribution-fixed;
 const hard=c.hard_cost+(w?c.wash_hard_cost:0),contingency=hard*c.contingency_rate,budget=c.land_cost+c.soft_cost+hard+contingency,loan=budget*c.loan_to_cost,debt=loanPayment(loan,c.annual_interest_rate,c.amortization_years),dscr=debt===0?null:cfads/debt;
 const maxLoan=Math.max(0,cfads/c.target_dscr)/loanPayment(1,c.annual_interest_rate,c.amortization_years),maxEligible=c.loan_to_cost===0?null:maxLoan/c.loan_to_cost,requiredFuel=Math.max(0,fixed+c.target_dscr*debt-(contribution-fuel));
 const bridge=[['Reported nonfuel receipts',nonfuel],['Lottery transferred',-(lottery-lotto)],['Merchandise / wash cost',-cogs],['Net fuel contribution',fuel],['Nonfuel card fees',-fees],['Loaded labor',-labor],['Other fixed costs',-c.fixed_opex_monthly],['Maintenance reserve',-maintenance],['Cash before debt',cfads]];
 return {gallons,nonfuel_receipts:nonfuel,lottery_ticket_sales:lottery,lottery_commission:lotto,retained_nonfuel_receipts:retained,merchandise_cogs:cogs,card_fees:fees,net_fuel_contribution:fuel,store_contribution:storeGP,deli_contribution:deliGP,pizza_contribution:pizzaGP,wash_contribution:washGP,loaded_labor:labor,fixed_costs:c.fixed_opex_monthly,maintenance_reserve:maintenance,contribution,fixed_cash_cost:fixed,cfads,hard_budget:hard,contingency,eligible_budget:budget,loan,monthly_debt_service:debt,dscr,maximum_supported_loan:maxLoan,maximum_supported_eligible_budget:maxEligible,maximum_core_hard_cost:maxEligible===null?null:(maxEligible-c.land_cost-c.soft_cost)/(1+c.contingency_rate)-(w?c.wash_hard_cost:0),required_fuel_gallons:c.net_fuel_margin>0?requiredFuel/c.net_fuel_margin:(requiredFuel===0?0:null),required_sales_multiplier:contribution<=0?null:(fixed+c.target_dscr*debt)/contribution*z,bridge,illustrative_coverage_pass:debt===0?cfads>=0:dscr>=c.target_dscr};
}
function evaluateScenario(c,defaults,report){
 c={...c};const s=stabilized(c,defaults,report),period=c.construction_months+c.permit_delay_months,upfront=c.land_cost+c.soft_cost,fee=s.loan*c.loan_fee_rate;let balance=upfront*c.loan_to_cost,sponsor=upfront-balance+fee,devInterest=0,carryTotal=0;
 const months=[{month:0,phase:'closing',ramp:0,capex:upfront,loan_draw:balance,loan_balance:balance,construction_interest:0,carry:0,working_capital:0,cfads:0,debt_service:0,operating_cash_after_debt:0,sponsor_funding:sponsor,cumulative_sponsor_funding:sponsor}];
 for(let m=1;m<=period;m++){
  const spend=m>c.permit_delay_months?(s.hard_budget+s.contingency)/c.construction_months:0,draw=spend*c.loan_to_cost,interest=(balance+draw/2)*c.annual_interest_rate/12,carry=c.preopening_carry_monthly,funding=spend-draw+interest+carry;
  balance+=draw;sponsor+=funding;devInterest+=interest;carryTotal+=carry;
  months.push({month:m,phase:m<=c.permit_delay_months?'delay':'construction',ramp:0,capex:spend,loan_draw:draw,loan_balance:balance,construction_interest:interest,carry,working_capital:0,cfads:0,debt_service:0,operating_cash_after_debt:0,sponsor_funding:funding,cumulative_sponsor_funding:sponsor});
 }
 const opening=sponsor+c.working_capital;let opCum=0,minOp=0,y1CF=0,y1Debt=0;
 for(let m=1;m<=36;m++){
  const ramp=c.ramp_months===1?1:c.ramp_start+(1-c.ramp_start)*Math.min(m-1,c.ramp_months-1)/(c.ramp_months-1),cfads=s.contribution*ramp-s.fixed_cash_cost,interest=balance*c.annual_interest_rate/12,principal=Math.min(balance,Math.max(0,s.monthly_debt_service-interest)),debt=interest+principal,free=cfads-debt;
  balance=Math.max(0,balance-principal);opCum+=free;minOp=Math.min(minOp,opCum);if(m<=12){y1CF+=cfads;y1Debt+=debt;}
  const working=m===1?c.working_capital:0;
  months.push({month:period+m,operating_month:m,phase:'operations',ramp,capex:0,loan_draw:0,loan_balance:balance,construction_interest:0,carry:0,working_capital:working,cfads,debt_service:debt,operating_cash_after_debt:free,sponsor_funding:working-free,cumulative_sponsor_funding:opening-opCum});
 }
 return {config:c,steady:s,months,development_interest:devInterest,development_carry:carryTotal,loan_fee:fee,equity_at_opening:opening,peak_sponsor_funding_36m:opening-minOp,operating_deficit_funding_36m:-minOp,year1_cfads:y1CF,year1_debt_service:y1Debt,year1_dscr:y1Debt===0?null:y1CF/y1Debt,opening_month:period+1,overall_decision:'Not underwritten: site-specific evidence gates remain unverified'};
}
if(typeof module!=='undefined')module.exports={loanPayment,checkConfig,stabilized,evaluateScenario};
