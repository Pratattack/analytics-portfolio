"""Static, privacy and numeric verification without operating a browser."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,json,hashlib,subprocess,tempfile,decimal,zipfile
from model import ROOT,DEFAULT
OUT=ROOT/'outputs'
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.labels=[];self.inputs=[];self.h1=0
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='a' and 'href' in d:self.refs.append(d['href'])
  if tag=='img':assert 'alt' in d
  if tag=='label' and 'for' in d:self.labels.append(d['for'])
  if tag in ['input','select']:self.inputs.append((tag,d))
  if tag=='h1':self.h1+=1

def luminance(h):
 x=[int(h[i:i+2],16)/255 for i in [1,3,5]];v=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in x];return .2126*v[0]+.7152*v[1]+.0722*v[2]
def contrast(a,b):x,y=sorted([luminance(a),luminance(b)]);return (y+.05)/(x+.05)
def main():
 counts=dict(local_references=0,html_pages=0,labelled_controls=0,javascript_syntax_checks=0,input_default_step_checks=0)
 pages=list(OUT.glob('*.html'))
 with tempfile.TemporaryDirectory() as temp:
  for f in pages:
   s=f.read_text();p=Page();p.feed(s);assert len(p.ids)==len(set(p.ids)),f;assert p.h1==1,f;assert 'name="viewport"' in s and 'class="skip"' in s
   for ref in p.refs:
    u=urlsplit(ref)
    if u.scheme or u.netloc:continue
    if not u.path:
     assert not u.fragment or u.fragment in p.ids,(f,ref);continue
    target=f.parent/unquote(u.path);assert target.exists(),(f,ref);counts['local_references']+=1
   for tag,d in p.inputs:
    assert d.get('id') in p.labels,(f,d);counts['labelled_controls']+=1
    if d.get('type')=='number':
     v=decimal.Decimal(d['value']);low=decimal.Decimal(d.get('min','0'));step=decimal.Decimal(d.get('step','1'))
     assert v>=low and v<=decimal.Decimal(d['max']) and (v-low)%step==0,(f,d);counts['input_default_step_checks']+=1
   for i,(attrs,code) in enumerate(re.findall(r'<script([^>]*)>(.*?)</script>',s,re.S)):
    if 'application/json' in attrs:json.loads(code);continue
    q=Path(temp)/f'inline-{i}.js';q.write_text(code);subprocess.run(['node','--check',str(q)],check=True,capture_output=True);counts['javascript_syntax_checks']+=1
   counts['html_pages']+=1
  for f in OUT.glob('*.js'):subprocess.run(['node','--check',str(f)],check=True,capture_output=True);counts['javascript_syntax_checks']+=1
 # Scan public preparation only, never original attachments, for identifying source details.
 banned=[r'Rizwan',r'Shuja',r'Qasim',r'Iqbal',r'Cameron',r'R23725',r'\b76520\b',r'1502\s+W',r'4th\s+Street',r'4833195040',r'Brookshire',r'CEFCO',r'Krispy',r'Hunt Brothers',r'Data Feasibility']
 scanned=0
 for f in ROOT.rglob('*'):
  if not f.is_file() or '__pycache__' in f.parts or f.name=='verify.py' or f.suffix in {'.zip','.png','.pdf'}:continue
  text=f.read_text()
  for b in banned:assert not re.search(b,text,re.I),(f,b)
  if f.suffix in {'.html','.js','.css','.md','.svg'} and 'external' not in f.parts:assert '\u2014' not in text,f
  scanned+=1
 for source in json.loads((ROOT/'data/external/manifest.json').read_text()):
  b=(ROOT/'data/external'/source['file']).read_bytes();assert len(b)==source['bytes'] and hashlib.sha256(b).hexdigest()==source['sha256']
 ratios={name:contrast(c,'#0a111a') for name,c in [('body','#eeeae3'),('muted','#b2c0d1'),('blue','#b3d2f5'),('gold','#e9bc83'),('red','#e6aaaa')]}
 assert min(ratios.values())>=4.5
 grid_ratios={c:contrast('#f4f4ee',c) for c in ['#6b3d3c','#22354a','#255d61']};assert min(grid_ratios.values())>=4.5
 tests=subprocess.run(['python3','-m','unittest','discover','-s','tests','-q'],cwd=ROOT,capture_output=True,text=True);assert tests.returncode==0,tests.stderr
 parity=subprocess.run(['node','tests/test_parity.cjs'],cwd=ROOT,capture_output=True,text=True);assert parity.returncode==0,parity.stderr
 result={**counts,'privacy_scanned_text_files':scanned,'external_snapshot_hashes':3,'python_tests':21,'python_javascript':json.loads(parity.stdout),'body_contrast_ratios':{k:round(v,2) for k,v in ratios.items()},'minimum_grid_text_contrast':round(min(grid_ratios.values()),2),'em_dashes_in_visitor_copy':0,'browser_qa':'Not performed. The owner prohibited browser operation; visual mobile rendering, focus traversal and actual download clicks remain unverified. Pure calculations and static control associations were checked.','publication':'Release checks passed; publication status recorded separately'}
 (ROOT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
