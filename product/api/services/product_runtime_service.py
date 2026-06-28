from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


PRODUCT_DIRECTION = "Cubo Operacional / Operational Cube"
RUNTIME_MODE = "local_demo"
VERTICALS = ["small_service", "legal_office", "vesselflow"]
BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def exists(path: Path) -> bool:
    return path.exists()


class ProductRuntimeService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.product_root = repo_root / "product"
        self.outputs_root = repo_root / "outputs"

    def health(self) -> Dict[str, Any]:
        return {
            "status": "PASS",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "verticals": VERTICALS,
            "blocked_actions": BLOCKED_ACTIONS,
        }

    def product_status(self) -> Dict[str, Any]:
        checks = {
            "verticals_dir": exists(self.product_root / "verticals"),
            "vertical_runtime_adapter": exists(self.product_root / "scripts" / "build_vertical_state_request.py"),
            "vesselflow_state_request": exists(self.outputs_root / "prod_vert004_006_vesselflow_state_request.json"),
            "vesselflow_import_manifest": exists(self.outputs_root / "prod_vert004_006_vesselflow_import_manifest.json"),
            "product_ui": exists(self.product_root / "ui" / "index.html"),
            "vesselflow_state_definition": exists(self.outputs_root / "prod016_020_vesselflow_state_definition.json"),
            "vesselflow_state_report_export": exists(self.outputs_root / "prod021_025_vesselflow_state_report_export.json"),
            "vesselflow_real_data_intake": exists(self.product_root / "scripts" / "prepare_vesselflow_real_data_intake.py"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Prepare a real/anonymized VesselFlow intake JSON and run controlled state definition with --write --rerun-state.",
        }

    def verticals(self) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        for vertical_id in VERTICALS:
            try:
                items.append(self.vertical(vertical_id)["vertical"])
            except Exception as exc:
                items.append({"vertical_id": vertical_id, "status": "ERROR", "error": str(exc)})
        return {"status": "PASS", "verticals": items}

    def vertical(self, vertical_id: str) -> Dict[str, Any]:
        if vertical_id not in VERTICALS:
            return {"status": "NOT_FOUND", "error": f"Unknown vertical: {vertical_id}"}

        vdir = self.product_root / "verticals" / vertical_id
        manifest = read_json(vdir / "vertical_manifest.json")
        domain_map = read_json(vdir / "domain_map.json")
        gate_map = read_json(vdir / "gate_map.json")
        cube_seed = read_json(vdir / "operational_cube_seed.json")
        vertical = {
            "vertical_id": vertical_id,
            "vertical_name": manifest.get("vertical_name"),
            "complexity": manifest.get("complexity"),
            "domains_count": len(manifest.get("domains", [])),
            "entities_count": len(manifest.get("entities", [])),
            "gates_count": len(manifest.get("gates", [])),
            "blocked_by_default": manifest.get("blocked_by_default", []),
            "domain_keys": list(domain_map.get("domains", {}).keys()),
            "gate_policy": gate_map.get("default_gate_policy"),
            "cube_faces": list(cube_seed.get("faces", {}).keys()),
        }
        return {"status": "PASS", "vertical": vertical}

    def state_request(self, vertical_id: str) -> Dict[str, Any]:
        if vertical_id not in VERTICALS:
            return {"status": "NOT_FOUND", "error": f"Unknown vertical: {vertical_id}"}
        json_path = self.outputs_root / f"prod_vert004_006_{vertical_id}_state_request.json"
        md_path = self.outputs_root / f"prod_vert004_006_{vertical_id}_state_request.md"
        if not json_path.exists():
            return {"status": "MISSING", "error": f"State request not generated: {json_path}"}
        return {
            "status": "PASS",
            "vertical_id": vertical_id,
            "state_request": read_json(json_path),
            "markdown_path": str(md_path),
            "markdown_preview": read_text(md_path)[:4000] if md_path.exists() else "",
        }

    def vesselflow_import_manifest(self) -> Dict[str, Any]:
        json_path = self.outputs_root / "prod_vert004_006_vesselflow_import_manifest.json"
        md_path = self.outputs_root / "prod_vert004_006_vesselflow_import_manifest.md"
        if not json_path.exists():
            return {"status": "MISSING", "error": "VesselFlow import manifest is missing."}
        return {
            "status": "PASS",
            "manifest": read_json(json_path),
            "markdown_path": str(md_path),
            "markdown_preview": read_text(md_path)[:4000] if md_path.exists() else "",
        }

    def vesselflow_state_definition(self) -> Dict[str, Any]:
        json_path = self.outputs_root / "prod016_020_vesselflow_state_definition.json"
        md_path = self.outputs_root / "prod016_020_vesselflow_state_definition.md"
        readiness_path = self.outputs_root / "prod016_020_vesselflow_import_readiness.json"
        if not json_path.exists():
            return {"status": "MISSING", "error": "VesselFlow state definition has not been generated yet."}
        return {
            "status": "PASS",
            "state_definition": read_json(json_path),
            "readiness": read_json(readiness_path) if readiness_path.exists() else {},
            "markdown_path": str(md_path),
            "markdown_preview": read_text(md_path)[:4000] if md_path.exists() else "",
        }

    def vesselflow_state_report_export(self) -> Dict[str, Any]:
        json_path = self.outputs_root / "prod021_025_vesselflow_state_report_export.json"
        md_path = self.outputs_root / "prod021_025_vesselflow_state_report_export.md"
        if not json_path.exists():
            return {"status": "MISSING", "error": "VesselFlow report export has not been generated yet."}
        return {
            "status": "PASS",
            "report_export": read_json(json_path),
            "markdown_path": str(md_path),
            "markdown_preview": read_text(md_path)[:4000] if md_path.exists() else "",
        }

    def vesselflow_real_data_intake_preview(self) -> Dict[str, Any]:
        json_path = self.outputs_root / "prod026_030_vesselflow_real_data_intake_preview.json"
        md_path = self.outputs_root / "prod026_030_vesselflow_real_data_intake_preview.md"
        if not json_path.exists():
            return {"status": "MISSING", "error": "VesselFlow real data intake preview has not been generated yet."}
        return {
            "status": "PASS",
            "preview": read_json(json_path),
            "markdown_path": str(md_path),
            "markdown_preview": read_text(md_path)[:4000] if md_path.exists() else "",
        }

    def reports(self) -> Dict[str, Any]:
        patterns = [
            "prod001_005_product_foundation_report.md",
            "prod_vert001_003_vertical_case_pack_report.md",
            "prod_vert004_006_vertical_runtime_adapter_report.md",
            "prod006_010_product_runtime_api_report.md",
            "prod011_015_product_ui_shell_report.md",
            "prod016_020_vesselflow_state_definition.md",
            "prod021_025_vesselflow_state_report_export.md",
            "prod026_030_vesselflow_real_data_intake_preview.md",
            "wb020_poc_completion_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({
                "name": name,
                "exists": path.exists(),
                "path": str(path),
                "preview": read_text(path)[:1200] if path.exists() else "",
            })
        return {"status": "PASS", "reports": reports}
