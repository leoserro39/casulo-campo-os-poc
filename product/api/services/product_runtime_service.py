from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from api.runtime_endpoint_registry import BLOCKED_ACTIONS, ENDPOINT_GROUPS

PRODUCT_DIRECTION = "Cubo Operacional / Operational Cube"
RUNTIME_MODE = "local_demo"

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

class ProductRuntimeService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.outputs_root = repo_root / "outputs"

    def health(self) -> Dict[str, Any]:
        return {
            "status": "PASS",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "blocked_actions": BLOCKED_ACTIONS,
        }

    def endpoint_registry(self) -> Dict[str, Any]:
        route_count = sum(len(g.get("routes", [])) for g in ENDPOINT_GROUPS)
        return {
            "status": "PASS",
            "endpoint_groups": ENDPOINT_GROUPS,
            "group_count": len(ENDPOINT_GROUPS),
            "route_count": route_count,
            "blocked_actions": BLOCKED_ACTIONS,
        }

    def product_status(self) -> Dict[str, Any]:
        checks = {}
        for group in ENDPOINT_GROUPS:
            for route in group.get("routes", []):
                rel = route.get("file")
                if rel:
                    checks[route["path"]] = (self.repo_root / rel).exists()
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "endpoint_group_count": len(ENDPOINT_GROUPS),
            "endpoint_route_count": sum(len(g.get("routes", [])) for g in ENDPOINT_GROUPS),
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Add external evidence adapter after runtime surface preservation is committed.",
        }

    def route_payload(self, route_path: str) -> Dict[str, Any]:
        for group in ENDPOINT_GROUPS:
            for route in group.get("routes", []):
                if route.get("path") == route_path:
                    rel = route.get("file")
                    key = route.get("key", "payload")
                    kind = route.get("kind", "json")
                    if not rel:
                        return {"status": "MISSING_ROUTE_FILE", "route": route_path}
                    path = self.repo_root / rel
                    if not path.exists():
                        return {"status": "MISSING", "route": route_path, "path": rel}
                    if kind == "markdown":
                        return {
                            "status": "PASS",
                            "route": route_path,
                            "group": group["group"],
                            key: read_text(path),
                            "path": rel,
                            "blocked_actions": BLOCKED_ACTIONS,
                        }
                    md = path.with_suffix(".md")
                    return {
                        "status": "PASS",
                        "route": route_path,
                        "group": group["group"],
                        key: read_json(path),
                        "path": rel,
                        "markdown_path": str(md),
                        "markdown_preview": read_text(md)[:4000] if md.exists() else "",
                        "blocked_actions": BLOCKED_ACTIONS,
                    }
        return {"status": "NOT_FOUND", "route": route_path}

    def reports(self) -> Dict[str, Any]:
        reports = []
        for pattern in [
            "prod481_500_operational_readiness_dossier.md",
            "prod501_520_runtime_surface_map.md",
            "prod501_520_repo_hygiene_report.md",
            "prod501_520_readiness.md",
            "prod501_520_audit_report.md",
        ]:
            p = self.outputs_root / pattern
            reports.append({
                "name": pattern,
                "exists": p.exists(),
                "path": str(p),
                "preview": read_text(p)[:1200] if p.exists() else "",
            })
        return {"status": "PASS", "reports": reports}
