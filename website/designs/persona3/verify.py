from pathlib import Path
import re,json,hashlib,subprocess
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
D=Path(__file__).parent;SITE=D.parents[1];OUT=SITE/'dist/design-preview/persona3'
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.h1=0;self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='img':self.images.append(a)
  for k in ['src','href','data']:
   if a.get(k):self.refs.append(a[k])
def main():
 raw=(OUT/'index.html').read_text();p=HTML();p.feed(raw);assert p.h1==1;assert len(p.ids)==len(set(p.ids));assert 'noindex,nofollow' in raw
 records=json.loads((SITE/'content/published-projects.json').read_text());assert len(records)==28 and len({p['slug'] for p in records})==len(records)
 embedded=json.loads(re.search(r'<script type="application/json" id="portfolio-data">(.*?)</script>',raw,re.S)[1]);assert embedded==records
 refs=0
 for ref in p.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  if not u.path:
   if u.fragment:assert u.fragment in p.ids or u.fragment in ['home','work','library','about','resume','contact'],ref
   continue
  f=SITE/'dist'/unquote(u.path).lstrip('/') if u.path.startswith('/') else OUT/unquote(u.path);f=f/'index.html' if f.is_dir() else f;assert f.exists(),str(f);refs+=1
 for r in records:
  for name in ['demo','report','download']:
   if not r.get(name):continue
   u=urlsplit(r[name]);
   if u.scheme:continue
   target=SITE/'dist'/u.path.lstrip('/');assert target.exists(),str(target);refs+=1
 for f in OUT.rglob('*'):
  if f.suffix in {'.html','.js','.css','.txt','.svg'}:assert '\u2014' not in f.read_text(),f
 for url in re.findall(r'url\([\"\']?([^\)\"\']+)',(OUT/'style.css').read_text()):
  f=SITE/'dist'/url.lstrip('/') if url.startswith('/') else OUT/url;assert f.exists(),f
 subprocess.run(['node','--check',str(OUT/'app.js')],check=True)
 code='''const assert=require('assert'),fs=require('fs');const{matchingProjects:m,parseRoute:r,escapeHtml:e}=require('./designs/persona3/app.js');const p=JSON.parse(fs.readFileSync('content/published-projects.json'));assert.equal(m(p).length,28);assert.equal(m(p,'python').length,28);assert.equal(m(p,'HOUSTON mortgages').length,1);assert.equal(m(p,'','Finance','Public + assumptions').length,8);assert.equal(m(p,'','Forecasting').length,2);assert.equal(m(p,'nonexistent-xyz').length,0);assert.equal(m(p,'','unknown').length,0);assert.equal(m(p,'','Research','Simulation').length,0);assert.equal(m(p,'private credit').some(x=>x.slug==='private-credit-measurement'),true);assert.equal(m(p,'sourcing').some(x=>x.slug==='import-duty-sourcing'),true);assert.equal(m(p,'recruiting capacity').some(x=>x.slug==='workforce-replacement-planning'),true);assert.equal(m(p,'cash deadlines').some(x=>x.slug==='treasury-cash-ladder'),true);for(const page of ['home','work','library','about','resume','contact'])assert.equal(r('#'+page).page,page);for(const project of p){const z=r('#project/'+project.slug);assert.equal(z.page,'project');assert.equal(z.slug,project.slug);}assert.equal(r('#unknown').page,'missing');assert.equal(r('#main').page,'home');const z=r('#library?q=credit&category=Finance&data=Public+%2B+assumptions');assert.equal(z.params.get('data'),'Public + assumptions');assert.equal(z.params.get('q'),'credit');assert.equal(e('<img src=x onerror="x">'), '&lt;img src=x onerror=&quot;x&quot;&gt;');console.log('47 filter, route and escaping checks passed.');'''
 subprocess.run(['node','-e',code],cwd=SITE,check=True)
 result=dict(projects=28,embedded_case_studies_match_source=True,static_local_references=refs,filter_route_escaping_checks=47,original_project_urls=True,browser_verification='Not performed; owner excludes browser operation. Rendering, focus traversal, PDF embedding and audio playback remain unverified.')
 (D/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
