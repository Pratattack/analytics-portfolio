"""Original static presentation helpers; no remote fonts or client dependencies."""
from pathlib import Path
import json,html,re,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
plt.rcParams.update({'figure.facecolor':'#0a111a','axes.facecolor':'#0a111a','savefig.facecolor':'#0a111a','text.color':'#eeeae3','axes.labelcolor':'#b2c0d1','xtick.color':'#b2c0d1','ytick.color':'#b2c0d1','axes.edgecolor':'#465d76','grid.color':'#314358','font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'market-research-2026','axes.spines.top':False,'axes.spines.right':False})
COLORS=['#a8cdf4','#9bd7c7','#e9bc83','#dda9b0']
def dump(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def table(frame):return '<div class="scroll" tabindex="0" role="region" aria-label="Evidence table">'+frame.to_html(index=False,border=0,float_format=lambda v:f'{v:,.3f}')+'</div>'
def plot(name,title,subtitle,draw):
 fig,ax=plt.subplots(figsize=(11,6));draw(ax);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.35);fig.suptitle(title,x=.09,ha='left',fontsize=18,fontweight='bold');fig.text(.09,.88,subtitle,color='#b2c0d1',fontsize=10);fig.text(.09,.025,'Independent research by Prathamesh Singh | Source dates and scenario assumptions are stated separately',fontsize=8,color='#b2c0d1');fig.subplots_adjust(top=.76,bottom=.18,left=.11,right=.96);handles,labels=ax.get_legend_handles_labels();
 if handles:ax.legend(handles,labels,loc='upper left',bbox_to_anchor=(0,1.14),ncol=2,frameon=False,fontsize=8)
 fig.savefig(OUT/(name+'.svg'),metadata={'Date':None});qa=ROOT.parents[3].parent/'market-2026-review/chart-review';qa.mkdir(exist_ok=True,parents=True);fig.savefig(qa/(name+'.png'),dpi=110);plt.close(fig)
def figure(name,caption):
 s=(OUT/(name+'.svg')).read_text();s=s[s.index('<svg'):]
 for old in set(re.findall(r'id="([^"]+)"',s)):
  new=name+'-'+old;s=s.replace('id="'+old+'"','id="'+new+'"').replace('href="#'+old+'"','href="#'+new+'"').replace('url(#'+old+')','url(#'+new+')')
 s=s.replace('<svg ','<svg role="img" aria-label="'+html.escape(caption,quote=True)+'" ',1)
 return '<figure class="chart">'+s+'<figcaption>'+html.escape(caption)+'</figcaption></figure>'
def page(file,title,lead,body,script='',data=None):
 css=(OUT/'app.css').read_text();head=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | Prathamesh Singh</title><style>{css}</style></head><body><a class="skip" href="#main">Skip to content</a><div class="wrap"><header class="topbar"><a href="https://prathameshsingh.com" class="brand">Prathamesh Singh ↗</a><span class="review-label">Review version / Not published</span></header><nav class="subnav" aria-label="Project"><a href="report.html">Research report</a><a href="workbench.html">Interactive tool</a><a href="../README.md">Documentation</a></nav><main id="main"><section class="hero" style="display:block"><p class="eyebrow">Economics / Finance / Decision research</p><h1>{html.escape(title)}</h1><p class="lead">{html.escape(lead)}</p></section>{body}</main><footer class="footer"><p>Independent portfolio research. Official source observations and hypothetical scenarios are labeled separately. This review has not been published.</p></footer></div>'
 tail=''
 if data is not None:tail+='<script id="project-data" type="application/json">'+json.dumps(data,allow_nan=False).replace('<','\\u003c')+'</script>'
 if script:tail+='<script>'+script+'</script>'
 result=head+tail+'<noscript><p>Enable JavaScript for recalculation. The research report contains fixed reference results.</p></noscript></body></html>';assert '\u2014' not in result
 if '--release' in sys.argv:result=result.replace('Review version / Not published','Independent research').replace('This review has not been published.','Source and scenario dates are stated above.')
 (OUT/file).write_text(result)
