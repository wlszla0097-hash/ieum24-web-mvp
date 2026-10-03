"""Local preview for static pages and the same Python handlers used by Vercel."""
from __future__ import annotations
import io, os
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)

def load_local_env():
    path=ROOT/'.env.local'
    if not path.exists():return
    for line in path.read_text(encoding='utf-8').splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line:continue
        key,value=line.split('=',1);key=key.strip();value=value.strip().strip('"\'')
        if key and key not in os.environ:os.environ[key]=value

class Bridge:
    """Minimal request/response surface needed by the BaseHTTPRequestHandler methods."""
    def __init__(self,headers,body):self.headers=headers;self.rfile=io.BytesIO(body);self.wfile=io.BytesIO();self.status=200
    def send_response(self,status,*args):self.status=status
    def send_header(self,*args):pass
    def end_headers(self):pass

class Preview(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml'}
    def do_GET(self):
        path=urlsplit(self.path).path
        if path.startswith('/api/'):
            self.call_api(path[5:],'GET');return
        if path=='/':self.path='/index.html'
        super().do_GET()
    def do_POST(self):self.call_api(urlsplit(self.path).path[5:],'POST')
    def call_api(self,name,method):
        if name not in {'programs','status','recommend'}:self.send_error(404);return
        from importlib import import_module
        module=import_module('api.'+name)
        size=min(int(self.headers.get('Content-Length','0')),4001)
        bridge=Bridge(self.headers,self.rfile.read(size) if method=='POST' else b'')
        try:module.handler.__dict__[f'do_{method}'](bridge)
        except Exception as exc:
            print('local_handler_error',name,type(exc).__name__)
            bridge.status=500;bridge.wfile=io.BytesIO(b'{"error":"Local API error"}')
        self.send_response(bridge.status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(bridge.wfile.getvalue())
    def log_message(self,fmt,*args):print('preview',self.address_string(),fmt%args)

def serve(port=8000):
    load_local_env()
    with ThreadingHTTPServer(('127.0.0.1',port),Preview) as server:
        print(f'이음24 local preview: http://127.0.0.1:{port}')
        try:server.serve_forever()
        except KeyboardInterrupt:pass

if __name__=='__main__':serve(int(os.environ.get('PORT','8000')))
