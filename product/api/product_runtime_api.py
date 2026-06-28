#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

THIS_FILE = Path(__file__).resolve()
PRODUCT_ROOT = THIS_FILE.parents[1]
REPO_ROOT = PRODUCT_ROOT.parent
UI_ROOT = PRODUCT_ROOT / "ui"
sys.path.insert(0, str(PRODUCT_ROOT))

from api.services.product_runtime_service import ProductRuntimeService


def json_bytes(data):
    return json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")


class ProductRuntimeHandler(BaseHTTPRequestHandler):
    service: ProductRuntimeService = ProductRuntimeService(REPO_ROOT)

    def send_json(self, data, status=200):
        body = json_bytes(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_static(self, path: Path):
        if not path.exists() or not path.is_file():
            return self.send_json({"status": "NOT_FOUND", "path": str(path)}, status=404)
        body = path.read_bytes()
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in ["application/javascript", "text/css"]:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        path = urlparse(self.path).path
        clean = path.strip("/")
        try:
            if path in ["/", "/ui", "/ui/"]: return self.send_static(UI_ROOT / "index.html")
            if clean.startswith("ui/"):
                requested = (UI_ROOT / clean.replace("ui/", "", 1)).resolve()
                if UI_ROOT.resolve() not in requested.parents and requested != UI_ROOT.resolve():
                    return self.send_json({"status": "FORBIDDEN"}, status=403)
                return self.send_static(requested)
            route_map = {
                "api/health": self.service.health,
                "api/product/status": self.service.product_status,
                "api/casulo/agent/openapi-spec": self.service.custom_gpt_openapi_spec,
                "api/casulo/agent/custom-gpt-instructions": self.service.custom_gpt_instructions,
                "api/casulo/agent/readiness": self.service.connector_readiness,
                "api/casulo/public-runtime/openapi-spec": self.service.public_openapi_spec,
                "api/casulo/public-runtime/deployment-plan": self.service.deployment_plan,
                "api/casulo/public-runtime/fastapi-adapter": self.service.fastapi_adapter,
                "api/casulo/public-runtime/action-import-guide": self.service.action_import_guide,
                "api/casulo/public-runtime/security-gate": self.service.security_gate,
                "api/casulo/public-runtime/parser-task-mode": self.service.parser_task_mode,
                "api/casulo/public-runtime/readiness": self.service.public_runtime_readiness,
                "api/casulo/public-runtime/audit": self.service.public_runtime_audit,
                "api/reports": self.service.reports,
            }
            if clean in route_map:
                return self.send_json(route_map[clean]())
            return self.send_json({"status": "NOT_FOUND", "path": path}, status=404)
        except Exception as exc:
            return self.send_json({"status": "ERROR", "error": str(exc)}, status=500)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8097)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), ProductRuntimeHandler)
    print(f"Operational Cube product runtime API/UI running at http://{args.host}:{args.port}")
    print("Open: /ui")
    print("Try: /api/health, /api/casulo/public-runtime/readiness")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping product runtime API/UI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
