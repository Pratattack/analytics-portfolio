from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,functools
class Handler(SimpleHTTPRequestHandler):
 extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.md':'text/plain; charset=utf-8','.csv':'text/csv; charset=utf-8','.html':'text/html; charset=utf-8','.json':'application/json; charset=utf-8'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);args=p.parse_args()
 ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(Handler,directory=str(Path(__file__).resolve().parent))).serve_forever()
