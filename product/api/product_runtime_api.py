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
        parts = clean.split("/") if clean else []

        try:
            if path in ["/", "/ui", "/ui/"]:
                return self.send_static(UI_ROOT / "index.html")

            if clean.startswith("ui/"):
                requested = (UI_ROOT / clean.replace("ui/", "", 1)).resolve()
                if UI_ROOT.resolve() not in requested.parents and requested != UI_ROOT.resolve():
                    return self.send_json({"status": "FORBIDDEN"}, status=403)
                return self.send_static(requested)

            if clean == "api/health":
                return self.send_json(self.service.health())

            if clean == "api/product/status":
                return self.send_json(self.service.product_status())

            if clean == "api/verticals":
                return self.send_json(self.service.verticals())

            if len(parts) == 3 and parts[0] == "api" and parts[1] == "verticals":
                return self.send_json(self.service.vertical(parts[2]))

            if len(parts) == 4 and parts[0] == "api" and parts[1] == "verticals" and parts[3] == "state-request":
                return self.send_json(self.service.state_request(parts[2]))

            if clean == "api/vesselflow/import-manifest":
                return self.send_json(self.service.vesselflow_import_manifest())

            if clean == "api/vesselflow/state-definition":
                return self.send_json(self.service.vesselflow_state_definition())

            if clean == "api/reports":
                return self.send_json(self.service.reports())

            return self.send_json({
                "status": "NOT_FOUND",
                "path": path,
                "available_endpoints": [
                    "/",
                    "/ui",
                    "/api/health",
                    "/api/product/status",
                    "/api/verticals",
                    "/api/verticals/{vertical_id}",
                    "/api/verticals/{vertical_id}/state-request",
                    "/api/vesselflow/import-manifest",
                    "/api/vesselflow/state-definition",
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
    print(f"Operational Cube product runtime API/UI running at http://{args.host}:{args.port}")
    print("Open: /ui")
    print("Try: /api/health, /api/verticals, /api/vesselflow/state-definition")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping product runtime API/UI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
