#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,mimetypes,sys
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from urllib.parse import urlparse

THIS_FILE=Path(__file__).resolve()
PRODUCT_ROOT=THIS_FILE.parents[1]
REPO_ROOT=PRODUCT_ROOT.parent
UI_ROOT=PRODUCT_ROOT/"ui"
sys.path.insert(0,str(PRODUCT_ROOT))
from api.services.product_runtime_service import ProductRuntimeService

def json_bytes(data): return json.dumps(data,indent=2,ensure_ascii=False).encode("utf-8")

class ProductRuntimeHandler(BaseHTTPRequestHandler):
    service=ProductRuntimeService(REPO_ROOT)
    def send_json(self,data,status=200):
        body=json_bytes(data); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def send_static(self,path:Path):
        if not path.exists() or not path.is_file(): return self.send_json({"status":"NOT_FOUND","path":str(path)},404)
        body=path.read_bytes(); ct=mimetypes.guess_type(str(path))[0] or "application/octet-stream"; self.send_response(200); self.send_header("Content-Type",ct); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self,fmt,*args): return
    def do_GET(self):
        path=urlparse(self.path).path; clean=path.strip("/")
        try:
            if path in ["/","/ui","/ui/"]: return self.send_static(UI_ROOT/"index.html")
            routes={
                "api/health":self.service.health,
                "api/product/status":self.service.product_status,
                "api/casulo/closure-replay/synthetic-url-manifest":self.service.synthetic_url_manifest,
                "api/casulo/closure-replay/ledger":self.service.closure_replay_ledger,
                "api/casulo/closure-replay/result":self.service.closure_replay_result,
                "api/casulo/closure-replay/readiness":self.service.closure_replay_readiness,
                "api/casulo/closure-replay/audit":self.service.closure_replay_audit,
                "api/reports":self.service.reports,
            }
            if clean in routes: return self.send_json(routes[clean]())
            return self.send_json({"status":"NOT_FOUND","path":path},404)
        except Exception as exc:
            return self.send_json({"status":"ERROR","error":str(exc)},500)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--host",default="127.0.0.1"); ap.add_argument("--port",type=int,default=8097); args=ap.parse_args()
    server=HTTPServer((args.host,args.port),ProductRuntimeHandler)
    print(f"Operational Cube product runtime API/UI running at http://{args.host}:{args.port}")
    print("Open: /ui")
    print("Try: /api/health, /api/casulo/closure-replay/result")
    try: server.serve_forever()
    except KeyboardInterrupt: print("Stopping product runtime API/UI.")
if __name__=="__main__": main()
