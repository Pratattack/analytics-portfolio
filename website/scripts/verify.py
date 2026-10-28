"""Check generated navigation, assets, JS syntax, search logic and ZIP integrity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re, subprocess, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.images, self.headings = [], [], [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.refs.append(attrs[name])
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'h1':
            self.headings.append(tag)

def main():
    pages = list(DIST.rglob('*.html'))
    assertions = 0
    script_count = 0
    with tempfile.TemporaryDirectory() as temp:
        for file in pages:
            text = file.read_text()
            p = Page()
            p.feed(text)
            assert len(p.ids) == len(set(p.ids)), file
            assert all('alt' in image for image in p.images), file
            if 'demos' not in file.relative_to(DIST).parts:
                assert len(p.headings) == 1, file
                assert 'name="viewport"' in text and 'class="skip"' in text, file
            for ref in p.refs:
                u = urlsplit(ref)
                if u.scheme or u.netloc:
                    continue
                if not u.path:
                    if u.fragment:
                        assert u.fragment in p.ids, (file, ref)
                    continue
                target = DIST / unquote(u.path).lstrip('/') if u.path.startswith('/') else file.parent / unquote(u.path)
                if target.is_dir():
                    target /= 'index.html'
                assert target.exists(), (file, ref)
                assertions += 1
            for attrs, code in re.findall(r'<script([^>]*)>(.*?)</script>', text, re.S):
                if not code.strip() or 'application/json' in attrs or 'application/ld+json' in attrs:
                    continue
                path = Path(temp) / f'inline-{script_count}.js'
                path.write_text(code)
                subprocess.run(['node', '--check', str(path)], check=True, capture_output=True)
                script_count += 1
        for script in DIST.rglob('*.js'):
            subprocess.run(['node', '--check', str(script)], check=True, capture_output=True)
            script_count += 1
    packages = list((DIST/'downloads').glob('*.zip'))
    for package in packages:
        with zipfile.ZipFile(package) as archive:
            assert archive.testzip() is None, package
            assert archive.namelist(), package
    css_references = 0
    for stylesheet in DIST.rglob('*.css'):
        for url in re.findall(r'url\([\"\']?([^\)\"\']+)', stylesheet.read_text()):
            if urlsplit(url).scheme or url.startswith('data:'):
                continue
            target = DIST/url.lstrip('/') if url.startswith('/') else stylesheet.parent/url
            assert target.exists(), (stylesheet, url)
            css_references += 1
    served_text = [p for p in DIST.rglob('*') if p.suffix in {'.html','.js','.svg','.md','.txt','.css'}]
    assert all('—' not in p.read_text() for p in served_text), 'Em dash remains in served copy'
    records = json.loads((ROOT/'content/projects.json').read_text())
    test = '''const assert=require('node:assert/strict');
const fs=require('node:fs');
const {matchingProjects:m}=require('./dist/assets/library.js');
const p=JSON.parse(fs.readFileSync('./content/projects.json','utf8'));
assert.equal(m(p).length,p.length);
assert.deepEqual(m(p,'  HOUSTON mortgages ').map(x=>x.slug),['houston-mortgage-price-comparability']);
assert.equal(m(p,'','Forecasting').length,2);
assert.equal(m(p,'','Research','Simulation').length,0);
assert.equal(m(p,'','all','Simulation').length,3);
assert.equal(m(p,'nonexistent-query-xyz').length,0);
assert.equal(m(p,'','unknown-category').length,0);
assert.equal(m(p,'python').length,p.length);
assert.equal(m(p,'','Finance','Public + assumptions').length,5);
assert.equal(m(p,'diesel').length,1);
assert.equal(m(p,'real wages').length,1);
assert.equal(m(p,'','Operations','Public + assumptions').some(x=>x.slug==='diesel-budget-risk'),true);
assert.deepEqual(m(p,'','Finance','Report + assumptions').map(x=>x.slug),['fuel-retail-investment-lab']);
assert.equal(m(p,'underwriting').some(x=>x.slug==='fuel-retail-investment-lab'),true);
console.log('14 search/filter boundary checks passed');'''
    subprocess.run(['node','-e',test],cwd=ROOT,check=True)
    result = dict(html_pages=len(pages),local_link_asset_checks=assertions,
                  javascript_syntax_checks=script_count,zip_integrity_checks=len(packages),
                  search_filter_checks=14,case_studies=len(records),
                  css_asset_checks=css_references,em_dashes_in_served_copy=0,
                  browser_qa='Blocked by automatic approval review: explicit user instruction prohibited browser operation. Mobile rendering, keyboard interaction and demo recalculation remain unverified in this release.')
    (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
