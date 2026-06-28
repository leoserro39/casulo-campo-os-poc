#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

THIS_FILE = Path(__file__).resolve()
PRODUCT_ROOT = THIS_FILE.parents[1]
REPO_ROOT = PRODUCT_ROOT.parent
sys.path.insert(0, str(PRODUCT_ROOT))

from api.services.product_runtime_service import ProductRuntimeService


def json_bytes(data, status=200):
    body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    return status, body


class ProductRuntimeHandler(BaseHTTPRequestHandler):
    service: ProductRuntimeService = ProductRuntimeService(REPO_ROOT)

    def send_json(self, data, status=200):
        code, body = json_bytes(data, status=status)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Keep demo logs small.
        return

    def do_GET(self):
        path = urlparse(self.path).path.strip("/")
        parts = path.split("/") if path else []

        try:
            if path == "api/health":
                return self.send_json(self.service.health())

            if path == "api/product/status":
                return self.send_json(self.service.product_status())

            if path == "api/verticals":
                return self.send_json(self.service.verticals())

            if len(parts) == 3 and parts[0] == "api" and parts[1] == "verticals":
                return self.send_json(self.service.vertical(parts[2]))

            if len(parts) == 4 and parts[0] == "api" and parts[1] == "verticals" and parts[3] == "state-request":
                return self.send_json(self.service.state_request(parts[2]))

            if path == "api/vesselflow/import-manifest":
                return self.send_json(self.service.vesselflow_import_manifest())

            if path == "api/reports":
                return self.send_json(self.service.reports())

            return self.send_json({
                "status": "NOT_FOUND",
                "path": "/" + path,
                "available_endpoints": [
                    "/api/health",
                    "/api/product/status",
                    "/api/verticals",
                    "/api/verticals/{vertical_id}",
                    "/api/verticals/{vertical_id}/state-request",
                    "/api/vesselflow/import-manifest",
                    "/api/reports",
                ],
            }, status=404)
        except Exception as exc:
            return self.send_json({"status": "ERROR", "error": str(exc)}, status=500)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8097)
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), ProductRuntimeHandler)
    print(f"Operational Cube product runtime API running at http://{args.host}:{args.port}")
    print("Try: /api/health, /api/verticals, /api/vesselflow/import-manifest")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping product runtime API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
