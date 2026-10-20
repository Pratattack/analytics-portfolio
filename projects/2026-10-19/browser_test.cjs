// Real browser acceptance over isolated localhost HTTP. No account, external assets or secrets.
const {chromium, firefox, webkit} = require('playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');

const base = __dirname;
const evidence = path.join(base, 'browser_evidence');
const projects = [
  ['airline-delay-intervention-screen', 'Airline delay intervention screen'],
  ['bank-deposit-cost-attribution', 'Bank deposit cost attribution']
];
const mime = {'.html':'text/html', '.png':'image/png', '.svg':'image/svg+xml', '.md':'text/plain', '.csv':'text/plain', '.json':'application/json', '.gz':'application/gzip'};

async function main() {
  await fs.mkdir(evidence, {recursive:true});
  const server = http.createServer(async (req, res) => {
    try {
      if (new URL(req.url, 'http://localhost').pathname === '/favicon.ico') {res.writeHead(204).end(); return;}
      const requested = path.resolve(base, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
      if (!requested.startsWith(base + path.sep)) {res.writeHead(403).end(); return;}
      const bytes = await fs.readFile(requested);
      const type=mime[path.extname(requested)] || 'application/octet-stream';
      const text=type.startsWith('text/') || ['application/json','image/svg+xml'].includes(type);
      res.writeHead(200, {'Content-Type':type+(text?'; charset=utf-8':'')});
      res.end(req.method === 'HEAD' ? undefined : bytes);
    } catch {res.writeHead(404).end();}
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const results = [];
  try {
    for (const [engine, launcher] of Object.entries({chromium,firefox,webkit})) {
      const browser = await launcher.launch();
      try {
        for (const [size, viewport] of [['desktop',{width:1440,height:1000}],['mobile',{width:390,height:844}]]) {
          for (const [slug,reportTitle] of projects) {
           for (const view of ['report','app']) {
            const title=view==='report'?reportTitle:slug.startsWith('airline')?'Airline investigation workbench':'Bank funding economics workbench';
            const context = await browser.newContext({viewport});
            const page = await context.newPage();
            const errors = [];
            page.on('pageerror', error => errors.push(String(error)));
            page.on('console', message => {if (message.type() === 'error') errors.push(message.text());});
            const response = await page.goto(`${origin}/${slug}/outputs/${view}.html`, {waitUntil:'networkidle'});
            assert.equal(response.status(),200);
            assert.equal(await page.getByRole('heading',{level:1}).innerText(),title);
            assert(await page.getByRole('heading',{level:1}).isVisible());
            const layout = await page.evaluate(() => ({
              rootWidth:document.documentElement.scrollWidth, viewport:innerWidth,
              images:[...document.images].map(image => ({loaded:image.complete && image.naturalWidth>0,alt:image.alt,width:image.getBoundingClientRect().width})),
              tables:[...document.querySelectorAll('table')].map(table => ({container:table.parentElement.classList.contains('scroll'),overflow:getComputedStyle(table.parentElement).overflowX})),
              links:[...document.querySelectorAll('a')].map(link => ({href:link.href,label:link.textContent.trim()}))
            }));
            assert(layout.rootWidth <= layout.viewport + 1, 'Page overflows viewport');
            if(view==='report')assert(layout.images.length>0);
            assert(layout.images.every(image => image.loaded && image.alt && image.width>0 && image.width<=viewport.width));
            assert(layout.tables.every(table => table.container && ['auto','scroll'].includes(table.overflow)));
            for (const link of layout.links) {
              assert(link.label, 'Empty link name');
              assert(link.href.startsWith(origin), 'Unexpected external dependency');
              const linked = await context.request.get(link.href);
              assert.equal(linked.status(),200,link.href);
              assert((await linked.body()).length>0, 'Empty linked output');
            }
            if(view==='app') {
              if(slug.startsWith('airline')) {
                await page.getByText('43.38%',{exact:true}).waitFor();
                await page.getByLabel('Investigation slots (1–20)',{exact:true}).fill('21');
                assert((await page.getByRole('alert').innerText()).includes('integer from 1 to 20'));
                await page.getByLabel('Investigation slots (1–20)',{exact:true}).fill('10');
                await page.getByLabel('Carrier or airport search',{exact:true}).fill('ZZZ-NO-MATCH');
                assert((await page.getByRole('status').innerText()).includes('No sites match'));
                await page.getByRole('button',{name:'Reset assumptions',exact:true}).click();
                await page.getByText('43.38%',{exact:true}).waitFor();
                await page.getByLabel('Ranking policy',{exact:true}).selectOption('raw');
                await page.getByText('33.34%',{exact:true}).waitFor();
                await page.getByRole('button',{name:'Reset assumptions',exact:true}).click();
                await page.getByText('43.38%',{exact:true}).waitFor();
              } else {
                await page.getByText('$243,750',{exact:true}).waitFor();
                await page.getByText('9.33%',{exact:true}).waitFor();
                await page.getByLabel('Proposed cut (basis points)',{exact:true}).fill('300');
                assert((await page.getByRole('alert').innerText()).includes('cannot exceed'));
                await page.getByLabel('Proposed cut (basis points)',{exact:true}).fill('25');
                await page.getByLabel('Attrition on targeted balances (%)',{exact:true}).fill('15');
                await page.getByText('-$318,750',{exact:true}).waitFor();
                await page.getByLabel('Review-queue asset bucket',{exact:true}).selectOption('under_1bn');
                assert((await page.getByRole('status').innerText()).includes('selected review-queue banks'));
                await page.getByRole('button',{name:'Reset assumptions',exact:true}).click();
                await page.getByText('$243,750',{exact:true}).waitFor();
              }
              assert.equal(await page.locator('#error').textContent(),'');
            }
            const shot = `${slug}-${engine}-${size}-${view}.png`;
            await page.screenshot({path:path.join(evidence,shot),fullPage:true});
            await page.getByRole('link',{name:'Executive memo',exact:true}).focus();
            await page.keyboard.press('Enter');
            await page.waitForURL(`**/${slug}/outputs/executive_memo.md`);
            assert((await page.locator('body').innerText()).includes('# '));
            assert.deepEqual(errors,[]);
            results.push({project:slug,view,engine,viewport:size,status:'PASS',links:layout.links.length,screenshot:shot});
            await context.close();
           }
          }
        }
      } finally {await browser.close();}
    }
    await fs.writeFile(path.join(evidence,'results.json'),JSON.stringify({status:'PASS',checks:['HTTP report/image/output loading','desktop and mobile layout','horizontal table scrolling containers','accessible headings and link names','keyboard focus and memo navigation','calculator reconciliation','invalid input and recovery','empty search/filter states','policy switching and reset','no page or console errors'],results},null,2));
    console.log(JSON.stringify(results,null,2));
  } finally {await new Promise(resolve => server.close(resolve));}
}
main().catch(error => {console.error(error); process.exitCode=1;});
