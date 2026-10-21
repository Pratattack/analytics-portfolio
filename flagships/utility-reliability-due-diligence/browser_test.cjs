// Tests the actual API client and self-contained offline delivery in real browsers.
const {chromium, firefox, webkit} = require('playwright');
const {spawn, execFileSync} = require('node:child_process');
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const base = __dirname;
const evidence = path.join(base, 'browser_evidence');
const python = process.env.PYTHON || 'python';
const review = JSON.parse(execFileSync(python, ['-c', "import csv,json; print(json.dumps(list(csv.DictReader(open('outputs/utility_due_diligence.csv')))))"], {cwd:base, encoding:'utf8'}));
const money = n => Number(n).toLocaleString('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0});
async function waitServer(origin, process) {
  for(let attempt=0;attempt<100;attempt++) {
    if(process.exitCode!==null)throw Error('API server exited');
    try {if((await fetch(origin+'/api/status')).ok)return;} catch {}
    await new Promise(r=>setTimeout(r,100));
  }
  throw Error('API server failed to start');
}
async function main() {
  await fs.mkdir(evidence,{recursive:true});
  const probe=http.createServer();await new Promise(r=>probe.listen(0,'127.0.0.1',r));
  const port=probe.address().port;await new Promise(r=>probe.close(r));
  const apiOrigin=`http://127.0.0.1:${port}`;
  const api=spawn(python,['app.py','--port',String(port)],{cwd:base,stdio:['ignore','pipe','pipe']});
  let stderr='';api.stderr.on('data',s=>stderr+=s);
  const staticServer=http.createServer(async(req,res)=>{
    if(req.url==='/favicon.ico'){res.writeHead(204).end();return;}
    if(req.url!=='/workbench.html'){res.writeHead(404).end();return;}
    res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
    res.end(await fs.readFile(path.join(base,'outputs/workbench.html')));
  });
  const results=[];
  try {
    await waitServer(apiOrigin,api);
    await new Promise(r=>staticServer.listen(0,'127.0.0.1',r));
    const offlineOrigin=`http://127.0.0.1:${staticServer.address().port}`;
    for(const [engine,launcher] of Object.entries({chromium,firefox,webkit})) {
      const browser=await launcher.launch();
      try {
        for(const [size,viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]) {
          for(const mode of ['api','offline']) {
            const context=await browser.newContext({viewport,locale:'en-US'});
            const page=await context.newPage();const errors=[];const unexpected=[];
            page.on('pageerror',e=>errors.push(String(e)));
            page.on('request',r=>{if(mode==='offline'&&r.url()!==offlineOrigin+'/workbench.html'&&!r.url().endsWith('/favicon.ico'))unexpected.push(r.url());});
            assert.equal((await page.goto(mode==='api'?apiOrigin:offlineOrigin+'/workbench.html')).status(),200);
            await page.waitForFunction(()=>document.querySelector('#history table')&&document.querySelector('#rows tr'));
            assert((await page.locator('#sourceNotice').innerText()).includes('2025 quarantined'));
            assert((await page.locator('#modelGate').innerText()).includes('No — evidence/data gates not satisfied'));
            assert.equal(await page.locator('#rows tr').count(),review.length);
            await page.getByLabel('State',{exact:true}).selectOption('TX');
            await page.getByLabel('Ownership',{exact:true}).selectOption('Cooperative');
            const expected=review.filter(r=>r.state==='TX'&&r.ownership==='Cooperative');
            await page.waitForFunction(n=>document.querySelectorAll('#rows tr').length===n,expected.length);
            assert(expected.length>1);
            await page.locator('#rows tr').nth(1).focus();await page.keyboard.press('Enter');
            await page.waitForFunction(id=>selected?.utility_id===id&&document.querySelector('#history table'),expected[1].utility_id);
            assert((await page.locator('#selectedInfo').innerText()).includes('EIA utility '+expected[1].utility_id));
            assert((await page.locator('#history').innerText()).includes('Quarantined release'));
            // Independent closed-form annuity oracle, compared with displayed calculator output.
            const row=expected[1],annual=Number(row.saidi_normal)*Number(row.customers)*.1/60*15-25000;
            for(const rate of [0,7]) {
              await page.getByLabel('Discount rate (%)',{exact:true}).fill(String(rate));
              await page.getByRole('button',{name:'Calculate conditional threshold'}).click();
              const factor=rate===0?10:(1-(1+rate/100)**-10)/(rate/100);
              await page.waitForFunction(text=>document.querySelector('#scenarioResult').textContent.includes(text),money(annual*factor)).catch(async error=>{await page.screenshot({path:path.join(evidence,`failure-${mode}-${engine}-${size}.png`),fullPage:true});console.error({expected:money(annual*factor),actual:await page.locator('#scenarioResult').innerText(),inputs:await page.locator('input:invalid').evaluateAll(es=>es.map(e=>({id:e.id,value:e.value,validation:e.validationMessage})))});throw error;});
              assert((await page.locator('#scenarioResult').innerText()).includes(money(annual*factor-1000000)));
            }
            await page.getByLabel('Assumed reduction (%)',{exact:true}).fill('0');
            await page.getByRole('button',{name:'Calculate conditional threshold'}).click();
            const negative=-25000*(1-1.07**-10)/.07;
            await page.waitForFunction(text=>document.querySelector('#scenarioResult').textContent.includes(text),money(negative));
            await page.getByLabel('Assumed reduction (%)',{exact:true}).fill('-1');
            await page.getByRole('button',{name:'Calculate conditional threshold'}).click();
            assert(await page.locator('#reduction').evaluate(el=>el.validity.rangeUnderflow));
            await page.getByLabel('Assumed reduction (%)',{exact:true}).fill('10');
            await page.getByLabel('Proposed up-front cost ($)',{exact:true}).fill('1000000000000');
            await page.getByRole('button',{name:'Calculate conditional threshold'}).click();
            await page.waitForFunction(()=>/Invalid|below \$1 trillion/.test(document.querySelector('#scenarioResult').textContent));
            await page.getByLabel('Proposed up-front cost ($)',{exact:true}).fill('1000000');
            await page.getByRole('button',{name:'Calculate conditional threshold'}).click();
            await page.waitForFunction(()=>document.querySelector('#scenarioResult').textContent.includes('Conditional break-even'));
            const rejected=await page.evaluate(async()=>{
              const normal={utility_id:selected.utility_id,state:selected.state,reduction:'.1',hour_value:'15',opex:'25000',rate:'.07',years:'10',capex:'1000000'};
              const cases=[{capex:'1000000000000'},{capex:'NaN'},{years:'1.5'},{hour_value:''},{utility_id:'-1'}];
              const checks=[];for(const bad of cases){try{await request('/api/scenario?'+new URLSearchParams({...normal,...bad}));checks.push(false);}catch{checks.push(true);}}return checks;
            });assert.deepEqual(rejected,[true,true,true,true,true]);
            await page.getByLabel('Name or EIA utility ID',{exact:true}).fill('ZZZ-NO-MATCH-EXPECTED');
            await page.waitForFunction(()=>document.querySelector('#selectedTitle').textContent==='No utilities match these filters');
            assert.equal(await page.locator('#history table').count(),0);
            assert.equal(await page.evaluate(()=>selected),null);
            await page.getByLabel('Name or EIA utility ID',{exact:true}).fill('');
            await page.waitForFunction(()=>document.querySelector('#history table')&&selected);
            if(mode==='api') {
              await page.route('**/api/utilities?*',route=>route.fulfill({status:503,contentType:'application/json',body:'{"error":"Test-only temporary outage"}'}),{times:1});
              await page.getByLabel('State',{exact:true}).selectOption('CA');
              await page.getByRole('alert').filter({hasText:'Test-only temporary outage'}).waitFor();
              assert.equal(await page.evaluate(()=>selected),null,'Failed filter must clear stale selection');
              await page.getByLabel('State',{exact:true}).selectOption('TX');
              await page.waitForFunction(()=>document.querySelector('#appError').hidden);
              // Delay old responses to prove rapid filter changes cannot restore stale rows.
              await page.route('**/api/utilities?*',async route=>{const u=new URL(route.request().url());const response=await route.fetch();if(u.searchParams.get('state')==='CA')await new Promise(r=>setTimeout(r,500));await route.fulfill({response});});
              await page.getByLabel('State',{exact:true}).selectOption('CA');
              await page.getByLabel('State',{exact:true}).selectOption('TX');
              await page.waitForTimeout(800);
              assert(await page.evaluate(()=>records.every(r=>r.state==='TX')));
              await page.unroute('**/api/utilities?*');
            }
            const layout=await page.evaluate(()=>({root:document.documentElement.scrollWidth,width:innerWidth,tables:[...document.querySelectorAll('table')].every(t=>['auto','scroll'].includes(getComputedStyle(t.parentElement).overflowX))}));
            if(layout.root>layout.width+1){await page.screenshot({path:path.join(evidence,`overflow-${mode}-${engine}-${size}.png`),fullPage:true});console.error(await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,id:e.id,class:e.className,right:e.getBoundingClientRect().right})).slice(0,20)));}
            assert(layout.root<=layout.width+1,'Root page overflows viewport');assert(layout.tables,'Table lacks scrolling container');
            assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[],'Offline workbench requested external data');
            const screenshot=`${mode}-${engine}-${size}.png`;await page.screenshot({path:path.join(evidence,screenshot),fullPage:true});
            results.push({mode,engine,viewport:size,status:'PASS',screenshot});await context.close();
          }
        }
      } finally {await browser.close();}
    }
    assert.equal(results.length,12);
    await fs.writeFile(path.join(evidence,'results.json'),JSON.stringify({status:'PASS',checks:['source quarantine and failed model gate','state/ownership filters','keyboard utility selection','history/source lineage','closed-form scenario reconciliation at zero/positive discount','negative net outcome','native invalid-input recovery','API/offline rejection parity','empty search recovery','API error recovery and response ordering','offline external-request absence','desktop/mobile overflow'],results},null,2));
    console.log(JSON.stringify({status:'PASS',cases:results.length}));
  } finally {api.kill();if(staticServer.listening)await new Promise(r=>staticServer.close(r));if(stderr)console.error(stderr);}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
