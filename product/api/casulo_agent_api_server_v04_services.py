#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

services = load_module("operational_services", "product/services/operational_services.py")

def route_post(path, payload):
    msg = str(payload.get("message", ""))
    case_id = str(payload.get("case_id", "COMMON-COMPANY-001"))
    if path == "/services/diagnostic":
        return 200, services.diagnostic_service(msg, case_id)
    if path == "/services/monitoring":
        return 200, services.monitoring_service(msg, case_id)
    if path == "/services/solutions":
        return 200, services.solutions_service(msg, case_id)
    if path == "/services/calibration":
        return 200, services.calibration_service(msg, case_id)
    return 404, {"status": "not_found", "path": path}

def route_get(path):
    if path == "/health":
        return 200, {"status": "ok", "service": "casulo_agent_api_server_v04_services", "phase": "PROD-8381..8420"}
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIServices/0.1"
    def _json(self, code, payload):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        code, payload = route_get(urlparse(self.path).path)
        self._json(code, payload)
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except Exception as exc:
            self._json(400, {"status": "bad_json", "error": str(exc)})
            return
        code, response = route_post(path, payload)
        self._json(code, response)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8381)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"serving": True, "host": args.host, "port": args.port, "health": f"http://127.0.0.1:{args.port}/health"}, indent=2))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
