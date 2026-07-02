#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import importlib.util

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

git_adapter = load_module("git_repo_adapter", "product/adapters/read_only/git_repo_adapter.py")
artifact_indexer = load_module("output_artifact_indexer", "product/adapters/read_only/output_artifact_indexer.py")
neo4j_adapter = load_module("neo4j_readonly_adapter_scaffold", "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py")
trace_adapter = load_module("evidence_trace_adapter", "product/adapters/read_only/evidence_trace_adapter.py")

def route_get(path, query):
    if path == "/health":
        return 200, {
            "status": "ok",
            "service": "casulo_agent_api_server_v02_adapters",
            "phase": "PROD-8301..8340",
            "mode": "read_only_adapters",
            "writes_allowed": False,
        }
    if path == "/adapters/git/status":
        return 200, git_adapter.git_repo_status()
    if path == "/adapters/git/timeline":
        limit = int(query.get("limit", ["80"])[0])
        return 200, git_adapter.git_repo_timeline(limit=limit)
    if path == "/adapters/repo/artifact-index":
        return 200, artifact_indexer.artifact_index()
    if path == "/adapters/repo/find":
        q = query.get("q", [""])[0]
        return 200, artifact_indexer.find_artifacts(q)
    if path == "/adapters/graph/summary":
        return 200, neo4j_adapter.graph_summary()
    if path == "/adapters/evidence/trace":
        case_id = query.get("case_id", ["REAL-CASE-001"])[0]
        return 200, trace_adapter.evidence_trace(case_id=case_id)
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIAdapters/0.1"
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8301)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"serving": True, "host": args.host, "port": args.port, "health": f"http://127.0.0.1:{args.port}/health"}, indent=2))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
