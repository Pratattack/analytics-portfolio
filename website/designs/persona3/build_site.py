"""Publish the approved Persona 3 inspired shell at canonical portfolio routes."""
from pathlib import Path
import json,subprocess,html,re,shutil
D=Path(__file__).parent;SITE=D.parents[1];DIST=SITE/'dist';esc=html.escape

def main():
 records=json.loads((SITE/'content/published-projects.json').read_text());assert records
 code="""const fs=require('fs'),m=require(process.argv[1]),p=JSON.parse(fs.readFileSync(process.argv[2]));const v=m.createPortfolioViews(p),out={work:v.renderWork(),library:v.renderLibrary(),about:v.renderAbout(),resume:v.renderResume(),contact:v.renderContact(),missing:v.renderMissing()};for(const x of p)out['project/'+x.slug]=v.renderProject(x.slug);console.log(JSON.stringify(out));"""
 result=subprocess.run(['node','-e',code,str(D/'site-app.js'),str(SITE/'content/published-projects.json')],check=True,capture_output=True,text=True);views=json.loads(result.stdout)
 home=(D/'home.html').read_text().replace('<strong>26</strong>',f'<strong>{len(records)}</strong>')
 mappings={'home':'/','work':'/work/','library':'/projects/','about':'/about/','resume':'/resume/','contact':'/contact/'}
 def links(s):
  s=re.sub(r'href="#project/([^\"]+)"',lambda m:'href="/projects/'+m[1]+'/"',s)
  return re.sub(r'href="#(home|work|library|about|resume|contact)"',lambda m:'href="'+mappings[m[1]]+'"',s)
 assets=DIST/'assets/persona3';assets.mkdir(parents=True,exist_ok=True)
 preview=DIST/'design-preview/persona3';assert preview.exists(),'Build the preview asset bundle first'
 shutil.copytree(D/'assets',assets/'assets',dirs_exist_ok=True);shutil.copy2(D/'site-app.js',assets/'app.js')
 css=(preview/'style.css').read_text()+ '\n.no-js-note{background:#031b50;color:#e4f7ff;padding:20px;text-align:center;font-size:12px}\n'
 (assets/'style.css').write_text(css)
 data=json.dumps(records,ensure_ascii=False).replace('</',r'<\/');home_json=json.dumps(links(home)).replace('</',r'<\/')
 def document(path,title,description,body,page):
  canonical='https://prathameshsingh.com'+path
  return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0731ac"><meta name="description" content="{esc(description,quote=True)}"><title>{esc(title)} | Prathamesh Singh</title><link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title,quote=True)} | Prathamesh Singh"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:type" content="website"><link rel="icon" href="/assets/mark.svg" type="image/svg+xml"><link rel="preload" href="/assets/persona3/assets/barlow-condensed-bold.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="/assets/persona3/style.css"></head><body data-view="{page}" data-motion="on"><a class="skip" href="#main">Skip to content</a><div class="scene" aria-hidden="true"></div><div class="rays" aria-hidden="true"></div><div class="orbital" aria-hidden="true"></div><header class="app-header"><a class="brand" href="/" aria-label="Prathamesh Singh menu"><span class="brand-symbol" aria-hidden="true">PS</span><span class="brand-name">PRATHAMESH<br>SINGH</span></a><a class="preview-link" href="/projects/">EXPLORE ALL {len(records)} PROJECTS ↗</a></header><a class="return-menu" href="/"><span>← BACK TO MENU</span></a><main id="main" tabindex="-1">{links(body)}</main><div class="persistent-controls"><button id="motion" class="toggle" type="button" aria-pressed="true">Motion: on</button><button id="sound" class="toggle" type="button" aria-pressed="false">Sound: off</button></div><div id="transition-stripe" class="transition-stripe" aria-hidden="true"></div><script type="application/json" id="home-template">{home_json}</script><script type="application/json" id="portfolio-data">{data}</script><script src="/assets/persona3/app.js"></script><noscript><p class="no-js-note">All pages and downloads remain available. Enable JavaScript for search, motion and optional sound.</p></noscript></body></html>'''
 def write(path,title,desc,body,page):
  target=DIST/path.lstrip('/');target=target/'index.html' if path.endswith('/') else target;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(document(path,title,desc,body,page))
 write('/','Economics & Business Analysis','Prathamesh Singh is an economics graduate from the University of Houston. Explore his work on business costs, financial risks and operational decisions.',home,'home')
 for page in ['work','library','about','resume','contact']:
  title={'work':'Selected work','library':'Project library','about':'About','resume':'Résumé','contact':'Contact'}[page];write(mappings[page],title,title+' for Prathamesh Singh. Explore independent research in economics, finance and operations.',views[page],page)
 for p in records:write(p['url'],p['shortTitle'],p['summary'],views['project/'+p['slug']],'project')
 write('/404.html','Page not found','This page is not in the portfolio.',views['missing'],'missing')
 urls=list(mappings.values())+[p['url'] for p in records];(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://prathameshsingh.com'+u+'</loc></url>' for u in urls)+'</urlset>')
 print(json.dumps({'production_theme':'Persona 3 inspired','canonical_project_pages':len(records),'static_sections':6,'original_project_urls':True}))
if __name__=='__main__':main()
