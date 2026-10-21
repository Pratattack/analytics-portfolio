"""Local, read-only analyst workbench. No account, uploads or external services."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import argparse,csv,json
from analysis import scenario,read_panel,valid
ROOT=Path(__file__).resolve().parent
def resources():
    with (ROOT/'outputs/utility_due_diligence.csv').open() as f:review=list(csv.DictReader(f))
    return review,json.loads((ROOT/'outputs/metrics.json').read_text())
def api(path,params):
    review,metrics=resources()
    if path=='/api/status':return metrics
    def get(k,default=''):return params.get(k,[default])[0]
    if path=='/api/utilities':
        state,ownership,query=get('state'),get('ownership'),get('q').casefold()
        filtered=[r for r in review if (not state or r['state']==state) and (not ownership or r['ownership']==ownership) and (not query or query in (r['utility_name']+' '+r['utility_id']).casefold())]
        return dict(rows=filtered,states=sorted({r['state'] for r in review}),ownerships=sorted({r['ownership'] for r in review}),view_year=metrics['decision_view_year'])
    if path in ['/api/history','/api/scenario']:
        row=next((r for r in review if r['utility_id']==get('utility_id') and r['state']==get('state')),None)
        if row is None:raise ValueError('Select an eligible utility-state row')
        if path=='/api/history':
            rows=[r for r in read_panel() if r['utility_id']==int(row['utility_id']) and r['state']==row['state']]
            return dict(rows=rows,decision_view_year=metrics['decision_view_year'],quarantined_years=metrics['quarantined_years'])
        reduction=float(get('reduction'));hour_value=float(get('hour_value'));opex=float(get('opex'));rate=float(get('rate'));years=int(get('years'));capex=float(get('capex'))
        if not 0<=capex<1e12:raise ValueError('Capex must be a finite nonnegative amount below $1 trillion')
        result=scenario(float(row['saidi_normal']),float(row['customers']),reduction,hour_value,opex,rate,years)
        return dict(**result,proposed_capex_usd=capex,conditional_surplus_usd=result['break_even_upfront_cost_usd']-capex,utility=row,warning='Hypothetical social-value screen; effectiveness and outage valuation are assumptions, not EIA estimates. No investment recommendation or utility cash-flow valuation.',assumptions=dict(reduction=reduction,hour_value=hour_value,opex=opex,rate=rate,years=years))
    raise ValueError('Unknown endpoint')
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url=urlparse(self.path)
        try:
            if url.path.startswith('/api/'):
                payload=json.dumps(api(url.path,parse_qs(url.query)),allow_nan=False).encode();status=200;kind='application/json'
            elif url.path=='/favicon.ico':
                self.send_response(204);self.end_headers();return
            elif url.path in ['/','/index.html']:
                payload=(ROOT/'index.html').read_bytes();status=200;kind='text/html; charset=utf-8'
            else:self.send_error(404);return
        except (ValueError,TypeError,KeyError,OverflowError) as exc:payload=json.dumps(dict(error=str(exc))).encode();status=400;kind='application/json'
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(payload)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(payload)
    def log_message(self,*args):pass
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
    print(f'Open http://127.0.0.1:{args.port} — local read-only workbench',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
