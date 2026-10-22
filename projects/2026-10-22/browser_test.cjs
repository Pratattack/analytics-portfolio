'use strict';
const {chromium,firefox,webkit}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert');
const root=__dirname,evidence=path.join(root,'browser_evidence');fs.mkdirSync(evidence,{recursive:true});
const projects=['homebuilder-land-option-diligence','hotel-reimbursement-economics'];
function close(a,b){assert(Math.abs(a-b)<=Math.max(.01,Math.abs(b)*1e-11),`${a} != ${b}`)}
async function run(){const results=[];const engines=process.env.BROWSER_ENGINE?[process.env.BROWSER_ENGINE]:['chromium','firefox','webkit'];
for(const name of engines){const browser=await({chromium,firefox,webkit}[name]).launch({headless:true,args:name==='chromium'?['--no-sandbox']:[]});
for(const project of projects)for(const view of [{name:'desktop',width:1440,height:1000},{name:'mobile',width:390,height:844}]){const context=await browser.newContext({viewport:{width:view.width,height:view.height},deviceScaleFactor:1});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));const land=project.startsWith('homebuilder');
try{
await page.goto('file://'+path.join(root,project,'outputs/app.html'));await page.waitForFunction(()=>document.getElementById('result').dataset.value!==undefined);assert.equal(await page.locator('#error').textContent(),'');
const data=JSON.parse(await page.locator('#dataset').textContent());const r=data.latest[0];const observed=Number(await page.locator('#result').getAttribute('data-value'));
if(land){const k=r.remaining_price,v=k*1.05;close(observed,(.5*Math.max(v*1.25-k,0)+.5*Math.max(v*.75-k,0))/1.1-.02*k-Math.max(v-k,0));}
else close(observed,r.op_income);
// Invalid values and blank inputs must clear stale results, then recover.
const field=land?'p':'cost_growth';await page.locator('#'+field).fill('9');await page.getByRole('button',{name:'Calculate scenario',exact:true}).click();assert((await page.locator('#error').textContent()).includes('enter a number'));assert.equal(await page.locator('#result').textContent(),'—');
await page.locator('#'+field).fill('');await page.getByRole('button',{name:'Calculate scenario',exact:true}).click();assert((await page.locator('#error').textContent()).length>0);
await page.locator('#'+field).fill(land?'0.25':'0.1');await page.getByRole('button',{name:'Calculate scenario',exact:true}).click();assert.equal(await page.locator('#error').textContent(),'');const z=Number(await page.locator('#result').getAttribute('data-value'));
if(land){const k=r.remaining_price,v=k*1.05;close(z,(.25*Math.max(v*1.25-k,0)+.75*Math.max(v*.75-k,0))/1.1-.02*k-Math.max(v-k,0));}else close(z,r.op_income-r.reimb_expense*.1);
// Empty search and restoration, with no HTML injection into records.
await page.getByLabel('Search issuer, date or scope').fill('NO_SOURCE_RECORD_9347');assert((await page.locator('#history-body').textContent()).includes('No matching source'));await page.locator('#search').fill('2025');assert(Number((await page.locator('#count').textContent()).split(' ')[0])>0);
// Native keyboard selection, keyboard submit and focus return on reset.
await page.locator('#issuer').focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');const selected=await page.locator('#issuer').inputValue();assert(selected!==data.latest[0].ticker);assert((await page.locator('#source').textContent()).includes(selected));
await page.locator('#'+field).focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#error').textContent(),'');
// Source error state and recovery are executed, not just described.
await page.evaluate(()=>{const s=document.getElementById('issuer');s.add(new Option('Missing fixture','UNKNOWN'));s.value='UNKNOWN';s.dispatchEvent(new Event('change'));});assert((await page.locator('#error').textContent()).includes('No source record'));assert.equal(await page.locator('#result').textContent(),'—');
await page.getByRole('button',{name:'Reset',exact:true}).click();assert.equal(await page.locator('#issuer').inputValue(),data.latest[0].ticker);assert.equal(await page.locator('#error').textContent(),'');close(Number(await page.locator('#result').getAttribute('data-value')),observed);
// Tables remain locally scrollable while document width stays inside viewport.
const scroll=page.locator('.table-scroll').first();const sizes=await scroll.evaluate(e=>({client:e.clientWidth,full:e.scrollWidth}));if(view.name==='mobile')assert(sizes.full>sizes.client);await scroll.evaluate(e=>e.scrollLeft=e.scrollWidth);assert(await scroll.evaluate(e=>e.scrollLeft)>0||sizes.full<=sizes.client);
await page.getByRole('button',{name:'Reset',exact:true}).click();assert.equal(await scroll.evaluate(e=>e.scrollLeft),0);assert(await page.locator('#issuer').evaluate(e=>e===document.activeElement));
const width=await page.evaluate(()=>({viewport:innerWidth,body:document.body.scrollWidth,doc:document.documentElement.scrollWidth}));assert(width.doc<=width.viewport+1&&width.body<=width.viewport+1,JSON.stringify(width));assert.deepEqual(errors,[]);
await page.locator('#search').fill('');await page.screenshot({path:path.join(evidence,`${project}-${name}-${view.name}-app.png`),fullPage:true});results.push({project,engine:name,viewport:view.name,surface:'app',status:'PASS',screenshot:`${project}-${name}-${view.name}-app.png`});
await page.goto('file://'+path.join(root,project,'outputs/report.html'));await page.locator('img.chart').waitFor();assert(await page.locator('img.chart').evaluate(e=>e.complete&&e.naturalWidth>0));assert((await page.locator('h2').first().textContent()).includes('Decision'));const rw=await page.evaluate(()=>({w:innerWidth,d:document.documentElement.scrollWidth}));assert(rw.d<=rw.w+1,JSON.stringify(rw));await page.screenshot({path:path.join(evidence,`${project}-${name}-${view.name}-report.png`),fullPage:true});results.push({project,engine:name,viewport:view.name,surface:'report',status:'PASS',screenshot:`${project}-${name}-${view.name}-report.png`});console.log(name,project,view.name,'PASS');
}catch(e){await page.screenshot({path:path.join(evidence,`FAIL-${project}-${name}-${view.name}.png`),fullPage:true});throw e;}finally{await context.close();}}
await browser.close();}
fs.writeFileSync(path.join(evidence,'results.json'),JSON.stringify({status:'PASS',results},null,2)+'\n');}
run().catch(e=>{console.error(e);process.exit(1)});
