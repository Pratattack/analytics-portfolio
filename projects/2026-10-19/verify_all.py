"""Three documented stages, failing closed; no network required for verification."""
import argparse,gzip,hashlib,json,os,subprocess,sys,tempfile,zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree
from research_support import digest,write_json
from collect import collect, fingerprint
BASE=Path(__file__).resolve().parent
PROJECTS=['airline-delay-intervention-screen','bank-deposit-cost-attribution']
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.images=[];self.scripts=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='script':self.scripts+=1
        for name in ['href','src']:
            if name in d:self.links.append(d[name])
        if tag=='img':assert d.get('alt');self.images.append(d['src'])

def sources(project):
    collect(project.name)
    pinned=json.loads((project/'data/pinned_content.json').read_text())
    for name,sha in pinned.items():assert fingerprint(project/'data/raw'/name)==sha
    return len(pinned)

def output_review(folder):
    from PIL import Image
    parser=Links();parser.feed((folder/'report.html').read_text());assert parser.scripts==0 and parser.images
    for link in parser.links:
        assert not link.startswith(('http:','https:','//')),('unexpected external dependency',link)
        assert (folder/link).is_file(),('broken local link',link)
    for path in folder.glob('*.svg'):assert ElementTree.parse(path).getroot().tag.endswith('svg')
    for path in folder.glob('*.png'):
        with Image.open(path) as im:assert im.width>=1200 and im.height>=600;im.verify()
    app=Links();app.feed((folder/'app.html').read_text());assert app.scripts==2
    for link in app.links:
        assert not link.startswith(('http:','https:','//'))
        assert (folder/link).is_file(),('broken application asset/link',link)
    return {'local_links_checked':len(parser.links),'figures_checked':len(parser.images),'report_type':'static offline HTML; no interactive controls or browser-dependent code'}

def hashes(folder):return {p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project',choices=PROJECTS);args=parser.parse_args();results={}
    subprocess.run([sys.executable,'-m','unittest','-v','test_server.py','test_restore_snapshot.py'],cwd=BASE,check=True)
    env=dict(os.environ,PYTHONHASHSEED='0',MPLCONFIGDIR=str(Path(tempfile.gettempdir())/'portfolio-mpl'))
    for name in [args.project] if args.project else PROJECTS:
        project=BASE/name;checks=sources(project)
        subprocess.run([sys.executable,str(project/'pipeline.py')],env=env,check=True,capture_output=True,text=True)
        expected=json.loads((project/'data/expected_results.json').read_text())
        actual=json.loads((project/'outputs/metrics.json').read_text())
        for key,value in expected.items():
            if isinstance(value,(int,float)) and not isinstance(value,bool):assert abs(actual[key]-value)<=max(1e-7,abs(value)*1e-10),(key,actual[key],value)
            else:assert actual[key]==value,(key,actual[key],value)
        run=subprocess.run([sys.executable,'-m','unittest','-v'],cwd=project,env=env,text=True,capture_output=True)
        (project/'test_results.txt').write_text(run.stdout+run.stderr)
        assert run.returncode==0,run.stdout+run.stderr
        with tempfile.TemporaryDirectory() as temp:
            first=Path(temp)/'first';second=Path(temp)/'second'
            for destination in [first,second]:
                subprocess.run([sys.executable,str(project/'pipeline.py'),'--output',str(destination)],env=env,check=True,capture_output=True,text=True)
            firsthash=hashes(first);secondhash=hashes(second);assert firsthash==secondhash,'clean builds differ'
            committed=hashes(project/'outputs')
            # Cross-platform PNG/font byte differences are not analytical changes; all numerical/text outputs must match.
            for file,sha in firsthash.items():
                if not file.endswith(('.png','.svg')):assert committed[file]==sha,('stale published output',file)
            review=output_review(first)
        metrics=json.loads((project/'outputs/metrics.json').read_text())
        evidence={'publication_gate':'PASS','stage_1':{'status':'PASS','checks':['source archive and decompressed hashes','complete API counts / BTS monthly coverage','unique natural keys','numeric and accounting contracts','explicit quarantines, no missing-to-zero imputation'],'source_hash_checks':checks},'stage_2':{'status':'PASS','checks':['hand-worked numerical cases','independent source-lineage audits of every analytical row','independent SQL/aggregation reconciliation','independent closed-form or exhaustive oracle','scenario downside and boundary cases'],'test_log':'test_results.txt'},'stage_3':{'status':'PASS','checks':['two isolated output directories, fresh Python processes, no network','all regenerated artifacts byte-identical across clean builds','published numerical/text outputs match regenerated values','HTML local-link/alt-text checks; SVG XML and PNG decoding'],'review':review},'human_visual_review':'See VISUAL_REVIEW.md for actual chart inspection and browser limitation.','source_cutoff':'2026-10-19','metrics':metrics,'regenerated_hashes':firsthash}
        evidence['publication_gate']='ANALYTICAL_PASS_BROWSER_CI_REQUIRED'
        evidence['browser_acceptance']='Separate october19-browser-acceptance CI job; consult its actual result at this commit.'
        write_json(project/'verification.json',evidence);results[name]='PASS';print(name,'PASS',flush=True)
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
