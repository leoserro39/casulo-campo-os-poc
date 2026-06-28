from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


PRODUCT_DIRECTION = "Cubo Operacional / Operational Cube"
RUNTIME_MODE = "local_demo"
VERTICALS = ["small_service", "legal_office", "vesselflow", "tic_si"]
BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
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
            "internal_review_freeze": exists(self.outputs_root / "prod046_050_internal_review_freeze.json"),
            "release_candidate": exists(self.outputs_root / "prod046_050_release_candidate.json"),
            "product_positioning": exists(self.outputs_root / "prod051_060_product_positioning.json"),
            "development_layer": exists(self.outputs_root / "prod051_060_development_layer.json"),
            "tic_state_mesh": exists(self.outputs_root / "prod051_060_tic_state_mesh.json"),
            "software_review_gate": exists(self.outputs_root / "prod051_060_software_review_gate.json"),
            "commercial_packages": exists(self.outputs_root / "prod051_060_commercial_packages.json"),
            "tic_si_vertical": exists(self.product_root / "verticals" / "tic_si" / "vertical_manifest.json"),
            "tic_si_state_mesh": exists(self.outputs_root / "prod061_070_tic_si_state_mesh.json"),
            "tic_si_gate_matrix": exists(self.outputs_root / "prod061_070_tic_si_gate_matrix.json"),
            "tic_si_review_package": exists(self.outputs_root / "prod061_070_tic_si_review_package.json"),
            "software_review_intake": exists(self.outputs_root / "prod071_080_software_review_intake.json"),
            "software_review_gate_runtime": exists(self.outputs_root / "prod071_080_software_review_gate.json"),
            "development_tasks": exists(self.outputs_root / "prod071_080_development_tasks.json"),
            "codex_scope": exists(self.outputs_root / "prod071_080_codex_scope.json"),
            "casulo_method": exists(self.outputs_root / "prod081_120_casulo_method.json"),
            "company_chat_intake": exists(self.outputs_root / "prod081_120_company_chat_intake.json"),
            "gpt_operating_layer": exists(self.outputs_root / "prod081_120_gpt_operating_layer.json"),
            "evaluation_cases": exists(self.outputs_root / "prod081_120_evaluation_cases.json"),
            "hallucination_index": exists(self.outputs_root / "prod081_120_hallucination_index.json"),
            "delta_index": exists(self.outputs_root / "prod081_120_delta_index.json"),
            "evaluation_report": exists(self.outputs_root / "prod081_120_evaluation_report.json"),
            "technical_readiness_gate": exists(self.outputs_root / "prod081_120_technical_readiness_gate.json"),
            "calibration_ledger": exists(self.outputs_root / "prod081_120_calibration_ledger.json"),
            "audit_report": exists(self.outputs_root / "prod081_120_audit_report.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Calibrate with real/anonymous cases, then build Graph Builder v0 and POC Factory Pack.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def casulo_method(self) -> Dict: return self._payload("prod081_120_casulo_method.json", "casulo_method")
    def company_chat_intake(self) -> Dict: return self._payload("prod081_120_company_chat_intake.json", "company_chat_intake")
    def gpt_operating_layer(self) -> Dict: return self._payload("prod081_120_gpt_operating_layer.json", "gpt_operating_layer")
    def evaluation_cases(self) -> Dict: return self._payload("prod081_120_evaluation_cases.json", "evaluation_cases")
    def hallucination_index(self) -> Dict: return self._payload("prod081_120_hallucination_index.json", "hallucination_index")
    def delta_index(self) -> Dict: return self._payload("prod081_120_delta_index.json", "delta_index")
    def evaluation_report(self) -> Dict: return self._payload("prod081_120_evaluation_report.json", "evaluation_report")
    def technical_readiness_gate(self) -> Dict: return self._payload("prod081_120_technical_readiness_gate.json", "technical_readiness_gate")
    def calibration_ledger(self) -> Dict: return self._payload("prod081_120_calibration_ledger.json", "calibration_ledger")
    def audit_report(self) -> Dict: return self._payload("prod081_120_audit_report.json", "audit_report")

    # Existing endpoint compatibility
    def verticals(self) -> Dict: return {"status": "PASS", "verticals": VERTICALS}
    def vertical(self, vertical_id: str) -> Dict: return {"status": "PASS", "vertical": {"vertical_id": vertical_id}}
    def state_request(self, vertical_id: str) -> Dict: return self._payload(f"prod_vert004_006_{vertical_id}_state_request.json", "state_request")
    def __getattr__(self, name):
        mapping = {
            "vesselflow_import_manifest": ("prod_vert004_006_vesselflow_import_manifest.json", "manifest"),
            "vesselflow_state_definition": ("prod016_020_vesselflow_state_definition.json", "state_definition"),
            "vesselflow_state_report_export": ("prod021_025_vesselflow_state_report_export.json", "report_export"),
            "vesselflow_real_data_intake_preview": ("prod026_030_vesselflow_real_data_intake_preview.json", "preview"),
            "vesselflow_real_data_delta_review": ("prod031_035_vesselflow_real_data_delta_review.json", "delta_review"),
            "vesselflow_data_backed_rerun": ("prod036_040_vesselflow_data_backed_rerun.json", "data_backed_rerun"),
            "vesselflow_evidence_comparator": ("prod036_040_vesselflow_evidence_comparator.json", "evidence_comparator"),
            "vesselflow_human_review_package": ("prod041_045_vesselflow_human_review_package.json", "human_review_package"),
            "vesselflow_decision_gate": ("prod041_045_vesselflow_decision_gate.json", "decision_gate"),
            "internal_review_freeze": ("prod046_050_internal_review_freeze.json", "internal_review_freeze"),
            "release_candidate": ("prod046_050_release_candidate.json", "release_candidate"),
            "product_positioning": ("prod051_060_product_positioning.json", "product_positioning"),
            "development_layer": ("prod051_060_development_layer.json", "development_layer"),
            "tic_state_mesh": ("prod051_060_tic_state_mesh.json", "tic_state_mesh"),
            "software_review_gate": ("prod051_060_software_review_gate.json", "software_review_gate"),
            "commercial_packages": ("prod051_060_commercial_packages.json", "commercial_packages"),
            "tic_si_state_mesh": ("prod061_070_tic_si_state_mesh.json", "tic_si_state_mesh"),
            "tic_si_gate_matrix": ("prod061_070_tic_si_gate_matrix.json", "tic_si_gate_matrix"),
            "tic_si_review_package": ("prod061_070_tic_si_review_package.json", "tic_si_review_package"),
            "software_review_intake": ("prod071_080_software_review_intake.json", "software_review_intake"),
            "software_review_runtime_gate": ("prod071_080_software_review_gate.json", "software_review_gate"),
            "development_tasks": ("prod071_080_development_tasks.json", "development_tasks"),
            "codex_scope": ("prod071_080_codex_scope.json", "codex_scope"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod081_120_casulo_method.md",
            "prod081_120_company_chat_intake.md",
            "prod081_120_gpt_operating_layer.md",
            "prod081_120_hallucination_index.md",
            "prod081_120_delta_index.md",
            "prod081_120_evaluation_report.md",
            "prod081_120_technical_readiness_gate.md",
            "prod081_120_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
