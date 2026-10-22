'use strict';
const { chromium, firefox, webkit }=require('playwright');
const fs=require('fs'),path=require('path'),http=require('http'),assert=require('assert/strict');
const root=__dirname,out=path.join(root,'browser_evidence');fs.mkdirSync(out,{recursive:true});
const projects=['semiconductor-inventory-funding','freight-rail-capital-review'];
const mime={'.html':'text/html; charset=utf-8','.svg':'image/svg+xml','.csv':'text/csv; charset=utf-8','.md':'text/plain; charset=utf-8','.json':'application/json; charset=utf-8'};
const server=http.createServer((req,res)=>{let file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}fs.readFile(file,(err,b)=>{if(err){res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'});res.end('Not found');}else{res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});res.end(b);}});});
function close(a,b){assert.ok(Math.abs(a-b)<Math.max(1,Math.abs(b)*1e-10),`${a} != ${b}`);}
async function layout(page){
 const diag=await page.evaluate(()=>({page:document.documentElement.scrollWidth,viewport:innerWidth,offenders:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&!e.closest('.scroll')).map(e=>({tag:e.tagName,cls:e.className,id:e.id,w:e.getBoundingClientRect().width})).slice(0,15)}));
 assert.ok(diag.page<=diag.viewport+1,JSON.stringify(diag));
 const cards=await page.locator('.value').evaluateAll(es=>es.map(e=>({text:e.textContent,w:e.clientWidth,sw:e.scrollWidth})));
 assert.ok(cards.every(x=>x.sw<=x.w+1),JSON.stringify(cards));
}
async function main(){
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${server.address().port}`;let results=[];
 try{
 for(const [engine,type] of Object.entries({chromium,firefox,webkit})){
  const browser=await type.launch({headless:true});
  try{for(const [device,viewport] of Object.entries({desktop:{width:1440,height:1000},mobile:{width:390,height:844}})){
   for(const project of projects){for(const delivery of ['report','app']){
    const page=await browser.newPage({viewport});const errors=[];page.on('pageerror',e=>errors.push(e.message));const bad=[];page.on('response',r=>{if(r.status()>=400)bad.push(r.url());});
    const url=`${base}/${project}/outputs/${delivery}.html`;await page.goto(url,{waitUntil:'networkidle'});await page.getByRole('heading',{level:1}).waitFor();await layout(page);
    if(delivery==='report'){
     assert.equal(await page.locator('img').evaluateAll(es=>es.every(e=>e.complete&&e.naturalWidth>0)),true);
     for(const href of await page.locator('a').evaluateAll(es=>es.map(e=>e.getAttribute('href')))){const r=await page.request.get(new URL(href,url).href);assert.equal(r.status(),200,href);}
    }else{
     const semi=project.startsWith('semi');const data=JSON.parse(await page.locator('#project-data').textContent());const first=data.latest[0];
     const vals=async()=>page.locator('.scenario-value').evaluateAll(es=>es.map(e=>Number(e.dataset.value)));
     let v=await vals();assert.equal(v.length,3);
     if(semi){close(v[0],Number(first.inventory));close(v[1],0);close(v[2],Number(first.inventory)*.025);}
     else {close(v[0],Math.max(0,Number(first.cfo)-Number(first.capex)-Number(first.dividends)));close(v[1],Number(first.cfo)-Number(first.capex)-Number(first.dividends)-Number(first.buybacks));}
     await page.getByLabel('Search issuers',{exact:true}).fill('NO_SUCH_ISSUER');assert.equal(await page.locator('#decisions tbody tr').count(),0);assert.match(await page.locator('#count').textContent(),/No issuers match/);
     await page.getByRole('button',{name:'Reset',exact:true}).click();assert.equal(await page.locator('#decisions tbody tr').count(),data.latest.length);
     await page.locator('#assumptionA').fill(semi?'41':'-61');await page.getByRole('button',{name:'Calculate',exact:true}).click();assert.match(await page.getByRole('alert').textContent(),/within the stated/);assert.equal((await vals()).length,0);
     await page.locator('#assumptionA').fill('');await page.getByRole('button',{name:'Calculate',exact:true}).click();assert.match(await page.getByRole('alert').textContent(),/within the stated/);
     await page.locator('#assumptionA').fill(semi?'20':'-20');await page.locator('#assumptionB').fill(semi?'10':'120');await page.locator('#assumptionB').press('Enter');v=await vals();assert.equal(v.length,3);
     if(semi){close(v[0],Number(first.inventory)*1.1);close(v[2],Number(first.inventory)*1.1*.05);await page.getByLabel('Forecast basis',{exact:true}).selectOption('candidate');assert.match(await page.locator('#scenario').textContent(),/Rejected-model diagnostic/);close((await vals())[0],Math.max(Number(first.forecast),Number(first.upper90))*1.1);await page.getByLabel('Issuer',{exact:true}).selectOption('COHU');assert.match(await page.getByRole('alert').textContent(),/scenario blocked/);assert.equal((await vals()).length,0);}
     else{close(v[1],Number(first.cfo)*.8-Number(first.capex)*1.2-Number(first.dividends)-Number(first.buybacks));}
     await page.getByRole('button',{name:'Reset',exact:true}).click();assert.equal(await page.getByRole('alert').textContent(),'');
     // Actual keyboard change and activation, not only script dispatch.
     const issuer=page.getByLabel('Issuer',{exact:true});await issuer.focus();await issuer.press('End');await issuer.press('Enter');await page.waitForTimeout(50);assert.equal(await issuer.inputValue(),data.latest.at(-1).ticker);assert.match(await page.locator('#scenario').textContent(),new RegExp(data.latest.at(-1).ticker));
     const region=page.getByRole('region',{name:'Issuer decision table'});await region.focus();await region.press('ArrowRight');
     if(device==='mobile'){
      const scroll=await region.evaluate(e=>{const before=e.scrollLeft;e.scrollLeft=e.scrollWidth;return {right:e.scrollLeft,max:e.scrollWidth-e.clientWidth,before};});assert.ok(scroll.max>0);assert.ok(scroll.right>=scroll.max-1);
     }
     await page.getByRole('button',{name:'Reset',exact:true}).click();assert.equal(await region.evaluate(e=>e.scrollLeft),0);await layout(page);
     // Tablet metric-card audit as a separate responsive checkpoint within this case.
     if(device==='desktop'){await page.setViewportSize({width:768,height:1024});await layout(page);await page.setViewportSize(viewport);}
    }
    const screenshot=`${project}-${engine}-${device}-${delivery}.png`;await page.screenshot({path:path.join(out,screenshot),fullPage:true});
    const memo=page.getByRole('link',{name:'Executive memo',exact:true});await memo.click();await page.waitForLoadState('load');assert.match(await page.locator('body').textContent(),/Decision|decision/);
    assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);results.push({project,engine,device,delivery,status:'PASS',screenshot});console.log(`PASS ${engine} ${device} ${project} ${delivery}`);await page.close();
   }}
  }}finally{await browser.close();}
 }
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({status:'PASS',results},null,2)+'\n');
 }finally{await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);fs.writeFileSync(path.join(out,'failure.txt'),e.stack+'\n');process.exitCode=1;server.close();});
