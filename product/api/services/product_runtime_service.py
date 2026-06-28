from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


PRODUCT_DIRECTION = "Cubo Operacional / Operational Cube"
RUNTIME_MODE = "local_demo"
VERTICALS = ["small_service", "legal_office", "vesselflow"]
BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
]


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def exists(path: Path) -> bool:
    return path.exists()


def payload(path: Path, key: str):
    if not path.exists():
        return {"status": "MISSING", "error": f"{key} has not been generated yet."}
    md = path.with_suffix(".md")
    return {"status": "PASS", key: read_json(path), "markdown_path": str(md), "markdown_preview": read_text(md)[:4000] if md.exists() else ""}


class ProductRuntimeService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.product_root = repo_root / "product"
        self.outputs_root = repo_root / "outputs"

    def health(self) -> Dict:
        return {"status": "PASS", "product_direction": PRODUCT_DIRECTION, "runtime_mode": RUNTIME_MODE, "verticals": VERTICALS, "blocked_actions": BLOCKED_ACTIONS}

    def product_status(self) -> Dict:
        checks = {
            "verticals_dir": exists(self.product_root / "verticals"),
            "product_ui": exists(self.product_root / "ui" / "index.html"),
            "vesselflow_state_definition": exists(self.outputs_root / "prod016_020_vesselflow_state_definition.json"),
            "vesselflow_state_report_export": exists(self.outputs_root / "prod021_025_vesselflow_state_report_export.json"),
            "vesselflow_real_data_intake": exists(self.product_root / "scripts" / "prepare_vesselflow_real_data_intake.py"),
            "vesselflow_real_data_delta_review": exists(self.outputs_root / "prod031_035_vesselflow_real_data_delta_review.json"),
            "vesselflow_data_backed_rerun": exists(self.outputs_root / "prod036_040_vesselflow_data_backed_rerun.json"),
            "vesselflow_evidence_comparator": exists(self.outputs_root / "prod036_040_vesselflow_evidence_comparator.json"),
            "vesselflow_human_review_package": exists(self.outputs_root / "prod041_045_vesselflow_human_review_package.json"),
            "vesselflow_decision_gate": exists(self.outputs_root / "prod041_045_vesselflow_decision_gate.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Review decision gate and only proceed after reviewed real/anonymized data is available.",
        }

    def verticals(self) -> Dict:
        items = []
        for vertical_id in VERTICALS:
            try:
                items.append(self.vertical(vertical_id)["vertical"])
            except Exception as exc:
                items.append({"vertical_id": vertical_id, "status": "ERROR", "error": str(exc)})
        return {"status": "PASS", "verticals": items}

    def vertical(self, vertical_id: str) -> Dict:
        if vertical_id not in VERTICALS:
            return {"status": "NOT_FOUND", "error": f"Unknown vertical: {vertical_id}"}
        vdir = self.product_root / "verticals" / vertical_id
        manifest = read_json(vdir / "vertical_manifest.json")
        domain_map = read_json(vdir / "domain_map.json")
        gate_map = read_json(vdir / "gate_map.json")
        cube_seed = read_json(vdir / "operational_cube_seed.json")
        return {"status": "PASS", "vertical": {
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
        }}

    def state_request(self, vertical_id: str) -> Dict:
        return payload(self.outputs_root / f"prod_vert004_006_{vertical_id}_state_request.json", "state_request")

    def vesselflow_import_manifest(self) -> Dict:
        return payload(self.outputs_root / "prod_vert004_006_vesselflow_import_manifest.json", "manifest")

    def vesselflow_state_definition(self) -> Dict:
        return payload(self.outputs_root / "prod016_020_vesselflow_state_definition.json", "state_definition")

    def vesselflow_state_report_export(self) -> Dict:
        return payload(self.outputs_root / "prod021_025_vesselflow_state_report_export.json", "report_export")

    def vesselflow_real_data_intake_preview(self) -> Dict:
        return payload(self.outputs_root / "prod026_030_vesselflow_real_data_intake_preview.json", "preview")

    def vesselflow_real_data_delta_review(self) -> Dict:
        return payload(self.outputs_root / "prod031_035_vesselflow_real_data_delta_review.json", "delta_review")

    def vesselflow_data_backed_rerun(self) -> Dict:
        return payload(self.outputs_root / "prod036_040_vesselflow_data_backed_rerun.json", "data_backed_rerun")

    def vesselflow_evidence_comparator(self) -> Dict:
        return payload(self.outputs_root / "prod036_040_vesselflow_evidence_comparator.json", "evidence_comparator")

    def vesselflow_human_review_package(self) -> Dict:
        return payload(self.outputs_root / "prod041_045_vesselflow_human_review_package.json", "human_review_package")

    def vesselflow_decision_gate(self) -> Dict:
        return payload(self.outputs_root / "prod041_045_vesselflow_decision_gate.json", "decision_gate")

    def reports(self) -> Dict:
        patterns = [
            "prod001_005_product_foundation_report.md",
            "prod_vert001_003_vertical_case_pack_report.md",
            "prod_vert004_006_vertical_runtime_adapter_report.md",
            "prod006_010_product_runtime_api_report.md",
            "prod011_015_product_ui_shell_report.md",
            "prod016_020_vesselflow_state_definition.md",
            "prod021_025_vesselflow_state_report_export.md",
            "prod026_030_vesselflow_real_data_intake_preview.md",
            "prod031_035_vesselflow_real_data_delta_review.md",
            "prod036_040_vesselflow_data_backed_rerun.md",
            "prod036_040_vesselflow_evidence_comparator.md",
            "prod041_045_vesselflow_human_review_package.md",
            "prod041_045_vesselflow_decision_gate.md",
            "wb020_poc_completion_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
