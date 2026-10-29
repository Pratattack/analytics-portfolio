"""Static and reproducibility checks; no browser operation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,json,hashlib,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.controls=[];self.labels=[];self.h1=0
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if t=='a' and 'href' in d:self.refs.append(d['href'])
  if t=='img':assert 'alt' in d
  if t in ['input','select']:self.controls.append(d)
  if t=='label':self.labels.append(d.get('for'))
  if t=='h1':self.h1+=1

def main():
 for rel,h in json.loads((ROOT/'data_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 links=0;controls=0;scripts=0;pages=list((ROOT/'outputs').glob('*.html'))
 with tempfile.TemporaryDirectory() as tmp:
  for f in pages:
   text=f.read_text();p=Page();p.feed(text);assert p.h1==1 and len(p.ids)==len(set(p.ids)),f
   assert 'name="viewport"' in text and 'class="skip"' in text
   for d in p.controls:assert d['id'] in p.labels;controls+=1
   for ref in p.refs:
    u=urlsplit(ref)
    if u.scheme or u.netloc:continue
    if not u.path:assert not u.fragment or u.fragment in p.ids
    else:assert (f.parent/unquote(u.path)).exists(),(f,ref);links+=1
   for i,(attrs,code) in enumerate(re.findall(r'<script([^>]*)>(.*?)</script>',text,re.S)):
    if 'application/json' in attrs:json.loads(code);continue
    q=Path(tmp)/f'script-{i}.js';q.write_text(code);subprocess.run(['node','--check',str(q)],check=True,capture_output=True);scripts+=1
  for f in (ROOT/'outputs').glob('*.js'):subprocess.run(['node','--check',str(f)],check=True,capture_output=True);scripts+=1
 for f in (ROOT/'outputs').rglob('*'):
  if f.suffix in ['.html','.js','.css','.svg','.md']:assert '\u2014' not in f.read_text(),f
 tests=subprocess.run(['python3','-m','unittest','discover','-s','tests','-q'],cwd=ROOT,text=True,capture_output=True);assert tests.returncode==0,tests.stderr
 parity=subprocess.run(['node','tests/parity.cjs'],cwd=ROOT,text=True,capture_output=True);assert parity.returncode==0,parity.stderr
 r=dict(analytical_tests=7,source_hashes=len(json.loads((ROOT/'data_hashes.json').read_text())),html_pages=len(pages),local_references=links,labelled_controls=controls,javascript_syntax_checks=scripts,python_javascript_parity=json.loads(parity.stdout),em_dashes_in_visitor_copy=0,browser_qa='Not performed because the owner prohibited browser operation. Rendering, mobile interaction, focus traversal and actual download clicks remain unverified.',publication='Approved release')
 (ROOT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
