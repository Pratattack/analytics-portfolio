"""Shared deterministic export and presentation utilities; analytical methods live in each project."""
import csv, json, html, hashlib, io, gzip
from pathlib import Path

def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
def write_csv(path,rows,fields=None):
    rows=list(rows);fields=fields or list(rows[0])
    buffer=io.StringIO(newline='');w=csv.DictWriter(buffer,fieldnames=fields);w.writeheader();w.writerows(rows)
    data=buffer.getvalue().encode('utf-8')
    path.write_bytes(gzip.compress(data,mtime=0) if path.suffix=='.gz' else data)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def table(rows,fields):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+html.escape(k)+'</th>' for k in fields)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(f'{r[k]:,.2f}' if isinstance(r[k],float) else str(r[k]))+'</td>' for k in fields)+'</tr>' for r in rows)+'</tbody></table></div>'
def report(path,title,kicker,lead,sections):
    body=''.join('<section><h2>'+html.escape(title)+'</h2>'+content+'</section>' for title,content in sections)
    path.write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+html.escape(title)+'''</title><style>
:root{font-family:Arial,sans-serif;color:#172d39;background:#edf2f4;line-height:1.6}body{max-width:1120px;margin:auto;padding:28px}header{background:#123648;color:white;padding:38px;border-radius:14px}h1{font-size:34px;line-height:1.2;max-width:950px}h2{font-size:23px;color:#123648}section{background:white;padding:28px;margin-top:22px;border-radius:12px}p{max-width:950px}img{width:100%;height:auto}table{border-collapse:collapse;font-size:14px;white-space:nowrap;width:100%}td,th{padding:10px;border-bottom:1px solid #d9e4e9;text-align:left}th{background:#eaf2f4}.scroll{overflow-x:auto}a{color:#067b83}.flag{border-left:5px solid #bd7624;padding:14px;background:#fff4df}small{color:#bdd7df}@media(max-width:600px){body{padding:12px}header,section{padding:20px}h1{font-size:27px}}@media print{body{background:white;padding:0}section{break-inside:avoid}header{color:#123648;background:white}}</style></head><body><header><small>'''+html.escape(kicker)+'''</small><h1>'''+html.escape(title)+'''</h1><p>'''+html.escape(lead)+'''</p></header>'''+body+'''<footer><p>Independent portfolio research by Prathamesh Singh · Information cutoff: October 19, 2026. Public source code and offline reports; no hosted service or employer engagement.</p></footer></body></html>''')
def plot_bars(path,labels,values,title,xlabel,colors=None):
    import matplotlib
    matplotlib.use('Agg');matplotlib.rcParams.update({'svg.hashsalt':'portfolio-20261019','font.family':'DejaVu Sans','font.size':11})
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(11,5.3),layout='constrained');fig.patch.set_facecolor('#ffffff')
    ax.barh(labels,values,color=colors or '#137f8c');ax.invert_yaxis();ax.set_title(title,loc='left',pad=16,fontweight='bold');ax.set_xlabel(xlabel);ax.axvline(0,color='#455a64',lw=.7);ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
    fig.savefig(path.with_suffix('.svg'),metadata={'Date':None,'Creator':'Analytics Portfolio'})
    fig.savefig(path.with_suffix('.png'),dpi=145,metadata={'Software':'Analytics Portfolio'});plt.close(fig)
