"""Original lightweight report and chart helpers, using only local assets."""
from pathlib import Path
import hashlib,json,html
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
COLORS=['#7db8ff','#67d7b7','#e8bc77','#db8fa1']
plt.rcParams.update({'figure.facecolor':'#0d1520','axes.facecolor':'#0d1520','savefig.facecolor':'#0d1520','text.color':'#eef3fa','axes.labelcolor':'#bdcadd','xtick.color':'#bdcadd','ytick.color':'#bdcadd','axes.edgecolor':'#425369','grid.color':'#334357','font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'pratattack-2026','axes.spines.top':False,'axes.spines.right':False})
def load(sid):
 m=json.loads((ROOT/'data/source_manifest.json').read_text());s=next(s for s in m['sources'] if s['series']==sid)
 b=(ROOT/'data/raw'/f'{sid}.csv').read_bytes();assert hashlib.sha256(b).hexdigest()==s['sha256']
 df=pd.read_csv(ROOT/'data/raw'/f'{sid}.csv',parse_dates=['observation_date']).rename(columns={'observation_date':'date',sid:'value'})
 assert not df.date.duplicated().any() and df.date.is_monotonic_increasing
 df['value']=pd.to_numeric(df.value,errors='raise');assert df.value.notna().all() and (df.value>0).all()
 return df.set_index('date').value

def chart(name,title,subtitle,draw):
 fig,ax=plt.subplots(figsize=(11,5.8));draw(ax);ax.grid(axis='y',alpha=.5);ax.set_axisbelow(True)
 fig.suptitle(title,x=.09,ha='left',fontsize=18,fontweight='bold');fig.text(.09,.88,subtitle,color='#bdcadd',fontsize=10)
 fig.text(.09,.025,'Prathamesh Singh | '+('EIA via FRED' if 'diesel' in str(ROOT) else 'BLS via FRED')+' | Current-vintage snapshot retrieved 28 Oct 2026',fontsize=8,color='#bdcadd')
 fig.subplots_adjust(top=.81,bottom=.16,left=.09,right=.96)
 fig.savefig(OUT/(name+'.svg'),metadata={'Date':None});plt.close(fig)

CSS='''*{box-sizing:border-box}html{color-scheme:dark}body{margin:0;background:#0b111b;color:#eaf0f8;font:16px/1.65 system-ui,sans-serif}a{color:#94c6ff;text-underline-offset:.2em}a:focus-visible,input:focus-visible,button:focus-visible{outline:3px solid #e8bc77;outline-offset:4px}.wrap{max-width:1100px;margin:auto;padding:28px 24px 70px}header{border-bottom:1px solid #344258;padding-bottom:28px;margin-bottom:32px}nav{display:flex;flex-wrap:wrap;gap:20px}.eyebrow{color:#8fbefa;font-size:12px;text-transform:uppercase;letter-spacing:.13em}h1{font-size:clamp(32px,5vw,58px);line-height:1.1;letter-spacing:-.035em;max-width:950px}h2{font-size:28px;line-height:1.2;margin-top:50px}h3{font-size:20px}.lead{font-size:21px;max-width:840px;color:#cbd7e8}.note{border-left:3px solid #e8bc77;padding:12px 20px;background:#14202e}.metrics{display:grid;grid-template-columns:repeat(3,1fr);border-block:1px solid #344258;padding:22px 0;gap:24px}.metric b{font-size:30px;display:block;color:#94c6ff}.metric span{font-size:14px;color:#cbd7e8}figure{margin:35px 0}img{display:block;width:100%;height:auto}figcaption{font-size:14px;color:#bcc9dc;margin-top:12px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #344258}th{color:#94c6ff}.scroll{overflow:auto}label{display:block;margin:20px 0 5px}input{background:#101d2c;border:1px solid #667d9a;color:#fff;padding:10px;font:inherit;width:100%;max-width:280px}output{display:block;font-size:24px;color:#67d7b7;margin-top:22px}.fields{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}small{color:#bcc9dc}.skip{position:absolute;top:-80px}.skip:focus{top:0;background:#0b111b;padding:15px}footer{margin-top:48px;border-top:1px solid #344258;padding-top:20px;color:#bcc9dc}@media(max-width:640px){.metrics,.fields{grid-template-columns:1fr}.wrap{padding-inline:18px}h2{font-size:24px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}'''
def write_page(filename,title,lead,body,script=''):
 nav='<nav aria-label="Project"><a href="report.html">Research report</a><a href="workbench.html">Budget workbench</a><a href="../README.md">Documentation</a></nav>'
 s=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | Prathamesh Singh</title><link rel="stylesheet" href="report.css"></head><body><a class="skip" href="#main">Skip to content</a><div class="wrap"><header><p class="eyebrow">Independent research / Prathamesh Singh</p>{nav}</header><main id="main"><h1>{html.escape(title)}</h1><p class="lead">{html.escape(lead)}</p>{body}</main><footer>Reproducible portfolio research. Current-vintage data retrieved 28 October 2026. Observed results and hypothetical budgets are labeled separately.</footer></div>{script}</body></html>'''
 assert '\u2014' not in s
 (OUT/filename).write_text(s)
 (OUT/'report.css').write_text(CSS)
def metrics(items):return '<div class="metrics">'+''.join(f'<div class="metric"><b>{html.escape(v)}</b><span>{html.escape(k)}</span></div>' for k,v in items)+'</div>'
def figure(name,caption):return f'<figure><img src="{name}.svg" alt="{html.escape(caption,quote=True)}"><figcaption>{html.escape(caption)}</figcaption></figure>'
def table(df):return '<div class="scroll">'+df.to_html(index=False,border=0,float_format=lambda v:f'{v:,.3f}')+'</div>'
