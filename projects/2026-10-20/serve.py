"""Serve one finance workbench's public outputs on localhost with explicit UTF-8."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from sec_sources import BASE, PROJECTS


class Handler(SimpleHTTPRequestHandler):
    def guess_type(self,path):
        kind=super().guess_type(path)
        return kind+'; charset=utf-8' if kind.startswith('text/') or kind in ['application/json','application/javascript','image/svg+xml'] else kind
    def do_GET(self):
        if self.path=='/favicon.ico':self.send_response(204);self.end_headers();return
        if self.path=='/':self.path='/app.html'
        super().do_GET()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--project',choices=PROJECTS,required=True);parser.add_argument('--port',type=int,default=8767);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(BASE/args.project/'outputs')))
    print(f'Open http://127.0.0.1:{args.port}/app.html',flush=True);server.serve_forever()
