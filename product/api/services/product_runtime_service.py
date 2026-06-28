from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


PRODUCT_DIRECTION = "Cubo Operacional / Operational Cube"
RUNTIME_MODE = "local_demo"
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
        self.outputs_root = repo_root / "outputs"

    def health(self) -> Dict:
        return {"status": "PASS", "product_direction": PRODUCT_DIRECTION, "runtime_mode": RUNTIME_MODE, "blocked_actions": BLOCKED_ACTIONS}

    def product_status(self) -> Dict:
        checks = {
            "poc_calibration_readiness": exists(self.outputs_root / "prod131_140_poc_calibration_readiness.json"),
            "calibration_results": exists(self.outputs_root / "prod131_140_calibration_results.json"),
            "technical_readiness_memo": exists(self.outputs_root / "prod141_150_technical_readiness_memo.json"),
            "chat_agent_operating_model": exists(self.outputs_root / "prod141_150_chat_agent_operating_model.json"),
            "target_stack": exists(self.outputs_root / "prod141_150_target_stack.json"),
            "codex_github_bridge": exists(self.outputs_root / "prod141_150_codex_github_bridge.json"),
            "poc_service_blueprint": exists(self.outputs_root / "prod141_150_poc_service_blueprint.json"),
            "risk_control_matrix": exists(self.outputs_root / "prod141_150_risk_control_matrix.json"),
            "technical_roadmap_90d": exists(self.outputs_root / "prod141_150_technical_roadmap_90d.json"),
            "incubator_technical_pack": exists(self.outputs_root / "prod141_150_incubator_technical_pack.json"),
            "technical_readiness_audit": exists(self.outputs_root / "prod141_150_audit_report.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Build Custom GPT Actions / Agent Connector Prototype.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def __getattr__(self, name):
        mapping = {
            "poc_calibration_results": ("prod131_140_calibration_results.json", "calibration_results"),
            "technical_readiness_memo": ("prod141_150_technical_readiness_memo.json", "technical_readiness_memo"),
            "chat_agent_operating_model": ("prod141_150_chat_agent_operating_model.json", "chat_agent_operating_model"),
            "target_stack": ("prod141_150_target_stack.json", "target_stack"),
            "codex_github_bridge": ("prod141_150_codex_github_bridge.json", "codex_github_bridge"),
            "poc_service_blueprint": ("prod141_150_poc_service_blueprint.json", "poc_service_blueprint"),
            "risk_control_matrix": ("prod141_150_risk_control_matrix.json", "risk_control_matrix"),
            "technical_roadmap_90d": ("prod141_150_technical_roadmap_90d.json", "technical_roadmap_90d"),
            "incubator_technical_pack": ("prod141_150_incubator_technical_pack.json", "incubator_technical_pack"),
            "technical_readiness_audit": ("prod141_150_audit_report.json", "technical_readiness_audit"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod141_150_technical_readiness_memo.md",
            "prod141_150_chat_agent_operating_model.md",
            "prod141_150_target_stack.md",
            "prod141_150_codex_github_bridge.md",
            "prod141_150_poc_service_blueprint.md",
            "prod141_150_risk_control_matrix.md",
            "prod141_150_technical_roadmap_90d.md",
            "prod141_150_incubator_technical_pack.md",
            "prod141_150_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
