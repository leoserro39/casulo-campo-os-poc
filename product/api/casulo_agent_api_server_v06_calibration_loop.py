#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

runner = load_module("controlled_business_case_runner", "product/calibration_loop/controlled_business_case_runner.py")

def route_get(path, query):
    if path == "/health":
        return 200, {
            "status": "ok",
            "service": "casulo_agent_api_server_v06_calibration_loop",
            "phase": "PROD-8461..8500",
            "writes_allowed": False,
        }
    if path == "/calibration-loop/cases":
        return 200, {"status": "ok", "cases": runner.load_cases(), "writes_allowed": False}
    return 404, {"status": "not_found", "path": path}

def route_post(path, payload):
    if path == "/calibration-loop/run":
        max_cases = payload.get("max_cases")
        if max_cases is not None:
            try:
                max_cases = int(max_cases)
            except Exception:
                max_cases = None
        return 200, runner.run_controlled_loop(max_cases=max_cases)
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPICalibrationLoop/0.1"
    def _json(self, code, payload):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        parsed = urlparse(self.path)
        code, payload = route_get(parsed.path, parse_qs(parsed.query))
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
    ap.add_argument("--port", type=int, default=8461)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"serving": True, "host": args.host, "port": args.port, "health": f"http://127.0.0.1:{args.port}/health"}, indent=2))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
