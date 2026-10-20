"""Serve a generated workbench on localhost with explicit UTF-8 text definitions."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        content_type = super().guess_type(path)
        if content_type.startswith('text/') or content_type in ['application/json', 'application/javascript', 'image/svg+xml']:
            content_type += '; charset=utf-8'
        return content_type

    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
        else:
            super().do_GET()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True, choices=['airline-delay-intervention-screen', 'bank-deposit-cost-attribution'])
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    directory = BASE / args.project / 'outputs'
    assert (directory / 'app.html').exists(), 'Build the project first with pipeline.py.'
    print(f'Workbench: http://127.0.0.1:{args.port}/app.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(directory))).serve_forever()
