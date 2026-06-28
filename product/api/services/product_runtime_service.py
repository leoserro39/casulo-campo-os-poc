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
            "custom_gpt_openapi_spec": exists(self.outputs_root / "prod151_160_openapi_spec.json"),
            "connector_readiness": exists(self.outputs_root / "prod151_160_connector_readiness.json"),
            "public_openapi_spec": exists(self.outputs_root / "prod161_170_public_openapi_spec.json"),
            "deployment_plan": exists(self.outputs_root / "prod161_170_deployment_plan.json"),
            "fastapi_adapter": exists(self.outputs_root / "prod161_170_fastapi_adapter.json"),
            "action_import_guide": exists(self.outputs_root / "prod161_170_action_import_guide.json"),
            "security_gate": exists(self.outputs_root / "prod161_170_security_gate.json"),
            "parser_task_mode": exists(self.outputs_root / "prod161_170_parser_task_mode.json"),
            "public_runtime_readiness": exists(self.outputs_root / "prod161_170_public_runtime_readiness.json"),
            "public_runtime_audit": exists(self.outputs_root / "prod161_170_audit_report.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Build State Store / Evidence Store / Graph Store baseline.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def __getattr__(self, name):
        mapping = {
            "custom_gpt_openapi_spec": ("prod151_160_openapi_spec.json", "openapi_spec"),
            "custom_gpt_instructions": ("prod151_160_custom_gpt_instructions.json", "custom_gpt_instructions"),
            "connector_readiness": ("prod151_160_connector_readiness.json", "connector_readiness"),
            "public_openapi_spec": ("prod161_170_public_openapi_spec.json", "public_openapi_spec"),
            "deployment_plan": ("prod161_170_deployment_plan.json", "deployment_plan"),
            "fastapi_adapter": ("prod161_170_fastapi_adapter.json", "fastapi_adapter"),
            "action_import_guide": ("prod161_170_action_import_guide.json", "action_import_guide"),
            "security_gate": ("prod161_170_security_gate.json", "security_gate"),
            "parser_task_mode": ("prod161_170_parser_task_mode.json", "parser_task_mode"),
            "public_runtime_readiness": ("prod161_170_public_runtime_readiness.json", "public_runtime_readiness"),
            "public_runtime_audit": ("prod161_170_audit_report.json", "public_runtime_audit"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod161_170_public_openapi_spec.md",
            "prod161_170_deployment_plan.md",
            "prod161_170_fastapi_adapter.md",
            "prod161_170_action_import_guide.md",
            "prod161_170_security_gate.md",
            "prod161_170_parser_task_mode.md",
            "prod161_170_public_runtime_readiness.md",
            "prod161_170_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
