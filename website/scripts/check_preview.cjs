const assert = require('node:assert/strict');
const { once } = require('node:events');
const { spawn } = require('node:child_process');
const { chromium } = require('playwright');

async function main() {
  const directory = process.argv[2] || 'website/dist';
  const requestedURL = process.env.PORTFOLIO_PREVIEW_URL;
  const server = requestedURL ? null : spawn('python3', ['-u', '-m', 'http.server', '0',
    '--bind', '127.0.0.1', '--directory', directory]);
  let browser;
  try {
    let baseURL = requestedURL;
    if (server) {
      const [output] = await once(server.stdout, 'data');
      const port = output.toString().match(/port (\d+)/)?.[1];
      assert(port, output.toString());
      baseURL = 'http://127.0.0.1:' + port;
    }
    browser = await chromium.launch(
      process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
    const project = '/projects/portfolio-preview-deployments/';
    for (const [name, viewport] of [
      ['desktop', { width: 1440, height: 900 }],
      ['mobile', { width: 390, height: 844 }],
    ]) {
      const page = await browser.newPage({ viewport });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      async function visit(path) {
        const response = await page.goto(new URL(path, baseURL).href);
        assert.equal(response.status(), 200, path);
        assert(await page.locator('h1').isVisible(), path);
      }
      await visit('/');
      await visit('/work/');
      assert(await page.locator('main a[href="' + project + '"]').first().isVisible());
      await visit('/projects/');
      await page.locator('#search').fill('mortgages');
      await page.getByRole('link', { name: /mortgage/i }).first().waitFor();
      assert.equal(await page.locator('main a[href="' + project + '"]:visible').count(), 0);
      await visit(project);
      assert.match(await page.locator('h1').innerText(), /pass review before/);
      await visit('/projects/crocs-brand-cash-allocation/');
      const [download] = await Promise.all([
        page.waitForEvent('download'),
        page.getByRole('link', { name: /download excel model/i }).click(),
      ]);
      assert.equal(download.suggestedFilename(), 'CROX_Financial_Model.xlsx');
      assert.equal(await download.failure(), null);
      assert.deepEqual(errors, []);
      console.log(name + ' Chromium: homepage, Selected Work, search, case study and Excel download passed');
      await page.close();
    }
  } finally {
    await browser?.close();
    server?.kill();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
