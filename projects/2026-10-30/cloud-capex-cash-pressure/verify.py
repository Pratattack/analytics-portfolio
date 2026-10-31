from pathlib import Path
import hashlib,json,subprocess,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.labels=[];self.controls=[];self.h1=0;self.viewport=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='label':self.labels.append(a.get('for'))
  if tag in ['input','select']:self.controls.append(a.get('id'))
  if tag=='h1':self.h1+=1
  if tag=='meta' and a.get('name')=='viewport':self.viewport=True
  for k in ['href','src']:
   if k in a:self.refs.append(a[k])
def main():
 for name,sha in json.loads((ROOT/'data_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
 refs=0;js=0
 for f in (ROOT/'outputs').glob('*.html'):
  s=f.read_text();assert '\u2014' not in s;page=Page();page.feed(s);assert len(page.ids)==len(set(page.ids)),f;assert page.h1==1 and page.viewport;assert all(x in page.labels for x in page.controls);assert 'href="#main"' in s
  for ref in page.refs:
   u=urlsplit(ref)
   if u.scheme or u.netloc or not u.path:continue
   target=f.parent/unquote(u.path);assert target.exists(),str(target);refs+=1
  for script in re.findall(r'<script(?![^>]*application/json)[^>]*>(.*?)</script>',s,re.S):
   temp=ROOT/'outputs/.syntax-check.js';temp.write_text(script);subprocess.run(['node','--check',str(temp)],check=True,capture_output=True);temp.unlink();js+=1
 test=subprocess.run(['python','-m','unittest','discover','-s','tests','-v'],cwd=ROOT,text=True,capture_output=True);assert test.returncode==0,test.stderr
 parity=subprocess.run(['node','tests/parity.cjs'],cwd=ROOT,text=True,capture_output=True);assert parity.returncode==0,parity.stderr
 result=dict(analytical_tests=int(re.search(r'Ran (\d+) tests',test.stderr)[1]),source_hash_checks=len(json.loads((ROOT/'data_hashes.json').read_text())),local_references=refs,inline_javascript_checks=js,python_javascript_parity=json.loads(parity.stdout),browser_qa='Not performed: owner instruction excludes browser operation. Mobile rendering and focus traversal remain unverified.');(ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
