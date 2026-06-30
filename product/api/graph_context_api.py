#!/usr/bin/env python3
import argparse
import json
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation",
    "gpt_call",
    "codex_execution"
]

def run_adapter(query, limit):
    cmd = [
        "python",
        "product/scripts/run_graph_backed_retrieval_adapter.py",
        "--query",
        query,
        "--limit",
        str(limit)
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=45)
    if proc.returncode != 0:
        return {
            "status": "ERROR",
            "error": proc.stderr.strip() or proc.stdout.strip(),
            "blocked_actions": BLOCKED_ACTIONS
        }

    packet_path = ROOT / "outputs" / "prod1341_1380_graph_context_packet.json"
    if not packet_path.exists():
        return {
            "status": "ERROR",
            "error": "context packet output not found",
            "blocked_actions": BLOCKED_ACTIONS
        }

    return json.loads(packet_path.read_text(encoding="utf-8"))

class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, code=200):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            self.send_json({
                "status": "PASS",
                "endpoint": "/api/health",
                "mode": "local_http_read_only_graph_context_api",
                "service": "CASULO Graph Context API",
                "blocked_actions": BLOCKED_ACTIONS
            })
            return

        if parsed.path == "/api/graph/context":
            params = parse_qs(parsed.query)
            query = params.get("query", ["missing evidence human review"])[0]
            try:
                limit = int(params.get("limit", ["8"])[0])
            except Exception:
                limit = 8

            limit = max(1, min(limit, 25))
            packet = run_adapter(query, limit)

            self.send_json({
                "status": packet.get("status", "UNKNOWN"),
                "endpoint": "/api/graph/context",
                "mode": "local_http_read_only_graph_context_api",
                "query": query,
                "limit": limit,
                "response": packet,
                "blocked_actions": BLOCKED_ACTIONS
            })
            return

        self.send_json({
            "status": "NOT_FOUND",
            "endpoint": parsed.path,
            "mode": "local_http_read_only_graph_context_api",
            "blocked_actions": BLOCKED_ACTIONS
        }, code=404)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8098)
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), Handler)
    print(f"CASULO Graph Context API running at http://{args.host}:{args.port}")
    print("Try: /api/health")
    print("Try: /api/graph/context?query=missing%20evidence%20human%20review&limit=8")
    server.serve_forever()

if __name__ == "__main__":
    main()
