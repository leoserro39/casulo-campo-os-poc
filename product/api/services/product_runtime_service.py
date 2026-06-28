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
            "casulo_method": exists(self.outputs_root / "prod081_120_casulo_method.json"),
            "company_chat_intake": exists(self.outputs_root / "prod081_120_company_chat_intake.json"),
            "gpt_operating_layer": exists(self.outputs_root / "prod081_120_gpt_operating_layer.json"),
            "evaluation_report": exists(self.outputs_root / "prod081_120_evaluation_report.json"),
            "technical_readiness_gate": exists(self.outputs_root / "prod081_120_technical_readiness_gate.json"),
            "graph_builder_v0": exists(self.outputs_root / "prod121_130_graph_builder_v0.json"),
            "state_store_index": exists(self.outputs_root / "prod121_130_state_store_index.json"),
            "recommendation_governance": exists(self.outputs_root / "prod121_130_recommendation_governance.json"),
            "poc_factory_pack": exists(self.outputs_root / "prod121_130_poc_factory_pack.json"),
            "poc_readiness_report": exists(self.outputs_root / "prod121_130_poc_readiness_report.json"),
            "graph_builder_audit": exists(self.outputs_root / "prod121_130_audit_report.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Run real/anonymous POC calibration, then harden Graph Builder v0 and persistence.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def graph_builder_v0(self) -> Dict: return self._payload("prod121_130_graph_builder_v0.json", "graph_builder_v0")
    def state_store_index(self) -> Dict: return self._payload("prod121_130_state_store_index.json", "state_store_index")
    def recommendation_governance(self) -> Dict: return self._payload("prod121_130_recommendation_governance.json", "recommendation_governance")
    def poc_factory_pack(self) -> Dict: return self._payload("prod121_130_poc_factory_pack.json", "poc_factory_pack")
    def poc_readiness_report(self) -> Dict: return self._payload("prod121_130_poc_readiness_report.json", "poc_readiness_report")
    def graph_builder_audit(self) -> Dict: return self._payload("prod121_130_audit_report.json", "graph_builder_audit")

    def __getattr__(self, name):
        mapping = {
            "casulo_method": ("prod081_120_casulo_method.json", "casulo_method"),
            "company_chat_intake": ("prod081_120_company_chat_intake.json", "company_chat_intake"),
            "gpt_operating_layer": ("prod081_120_gpt_operating_layer.json", "gpt_operating_layer"),
            "evaluation_cases": ("prod081_120_evaluation_cases.json", "evaluation_cases"),
            "hallucination_index": ("prod081_120_hallucination_index.json", "hallucination_index"),
            "delta_index": ("prod081_120_delta_index.json", "delta_index"),
            "evaluation_report": ("prod081_120_evaluation_report.json", "evaluation_report"),
            "technical_readiness_gate": ("prod081_120_technical_readiness_gate.json", "technical_readiness_gate"),
            "calibration_ledger": ("prod081_120_calibration_ledger.json", "calibration_ledger"),
            "audit_report": ("prod081_120_audit_report.json", "audit_report"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod121_130_graph_builder_v0.md",
            "prod121_130_state_store_index.md",
            "prod121_130_recommendation_governance.md",
            "prod121_130_poc_factory_pack.md",
            "prod121_130_poc_readiness_report.md",
            "prod121_130_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
