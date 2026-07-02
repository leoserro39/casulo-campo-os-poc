#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name, ROOT/path); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod
runtime=load("material_admission_runtime","product/materials/material_admission_runtime.py")
def rjson(path, default=None):
    p=ROOT/path
    if not p.exists(): return default
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return default
def route_get(path, query):
    if path=="/health": return 200, {"status":"ok","service":"casulo_agent_api_server_v07_materials","phase":"PROD-8501..8540","writes_allowed":False}
    if path=="/materials/taxonomy": return 200, rjson("product/materials/material_taxonomy_matrix_v0_1.json",{})
    if path=="/materials/dimensions": return 200, rjson("product/materials/material_dimensional_matrix_v0_1.json",{})
    return 404, {"status":"not_found","path":path}
def route_post(path,payload):
    raw=str(payload.get("raw",payload.get("message",""))); source=str(payload.get("source_type","chat_message")); domain=str(payload.get("domain_candidate","GENERAL_BUSINESS"))
    if path=="/materials/admit": return 200, runtime.admit_material(raw, source, domain)
    if path=="/materials/profile":
        items=payload.get("items") if isinstance(payload.get("items"), list) else [{"raw":raw,"source_type":source,"domain_candidate":domain}]
        return 200, runtime.profile_materials(items)
    if path=="/materials/gate": return 200, runtime.admit_material(raw, source, domain)["admission"]
    return 404, {"status":"not_found","path":path}
class Handler(BaseHTTPRequestHandler):
    def _json(self,code,payload):
        body=json.dumps(payload,indent=2,ensure_ascii=False).encode("utf-8"); self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p=urlparse(self.path); code,payload=route_get(p.path,parse_qs(p.query)); self._json(code,payload)
    def do_POST(self):
        length=int(self.headers.get("Content-Length","0") or "0"); raw=self.rfile.read(length).decode("utf-8") if length else "{}"
        try: payload=json.loads(raw) if raw.strip() else {}
        except Exception as e: self._json(400,{"status":"bad_json","error":str(e)}); return
        code,response=route_post(urlparse(self.path).path,payload); self._json(code,response)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--host",default="0.0.0.0"); ap.add_argument("--port",type=int,default=8501); args=ap.parse_args()
    httpd=ThreadingHTTPServer((args.host,args.port),Handler); print(json.dumps({"serving":True,"host":args.host,"port":args.port},indent=2)); httpd.serve_forever()
if __name__=="__main__": main()
