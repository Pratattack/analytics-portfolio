from pathlib import Path
import csv, html, json, math, statistics, hashlib
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
def csv_write(path,rows):
    rows=list(rows)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mean_ci(values):
    m=statistics.mean(values);se=statistics.stdev(values)/math.sqrt(len(values)) if len(values)>1 else 0
    return [m,m-1.96*se,m+1.96*se]
def report(title,subtitle,sections,chart=''):
    OUT.mkdir(exist_ok=True)
    memo='# '+title+'\n\n'+subtitle+'\n\n'+''.join('## '+h+'\n\n'+b+'\n\n' for h,b in sections)
    (OUT/'executive_memo.md').write_text(memo)
    content=''.join('<section><h2>'+html.escape(h)+'</h2><p>'+html.escape(b)+'</p></section>' for h,b in sections)
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>body{margin:0;background:#edf2f6;color:#17334b;font:16px/1.65 system-ui}main{max-width:1080px;margin:auto;padding:34px 22px}header,section,figure{background:white;border:1px solid #d9e3eb;border-radius:12px;margin:20px 0;padding:26px}header{border-top:7px solid #087f8c}h1{font-size:38px;line-height:1.15}h2{color:#087f8c}p{white-space:pre-wrap}svg{width:100%;height:auto}small{color:#51697e}a{color:#006d77}@media(max-width:600px){main{padding:14px}h1{font-size:28px}header,section,figure{padding:18px}}</style><main><header><small>ANALYTICS PORTFOLIO · 18 OCT 2026</small><h1>'+html.escape(title)+'</h1><p>'+html.escape(subtitle)+'</p></header>'+('<figure>'+chart+'</figure>' if chart else '')+content+'</main></html>'
    (OUT/'report.html').write_text(page)
def bars(title,records):
    high=max(v for _,v in records) or 1;out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 '+str(90+len(records)*52)+'" role="img" aria-label="'+html.escape(title,quote=True)+'"><rect width="100%" height="100%" fill="white"/><text x="20" y="28" font-family="sans-serif" font-size="20">'+html.escape(title)+'</text>']
    for i,(name,v) in enumerate(records):
        y=58+52*i;width=v/high*540
        out.append(f'<text x="20" y="{y+19}" font-family="sans-serif" font-size="13">{html.escape(name)}</text><rect x="270" y="{y}" width="{width}" height="27" fill="#087f8c"/><text x="{820}" y="{y+20}" font-family="sans-serif" font-size="14">{v:.2f}</text>')
    return ''.join(out)+'</svg>'
