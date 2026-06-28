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
            "case_runner_results": exists(self.outputs_root / "prod181_200_case_runner_results.json"),
            "random_cases": exists(self.outputs_root / "prod201_220_random_cases.json"),
            "scored_cases": exists(self.outputs_root / "prod201_220_scored_cases.json"),
            "anomaly_report": exists(self.outputs_root / "prod201_220_anomaly_report.json"),
            "family_behavior": exists(self.outputs_root / "prod201_220_family_behavior.json"),
            "ambiguity_behavior": exists(self.outputs_root / "prod201_220_ambiguity_behavior.json"),
            "risk_behavior": exists(self.outputs_root / "prod201_220_risk_behavior.json"),
            "stochastic_study_plan": exists(self.outputs_root / "prod201_220_stochastic_study_plan.json"),
            "calibration_policy": exists(self.outputs_root / "prod201_220_calibration_policy.json"),
            "stochastic_readiness": exists(self.outputs_root / "prod201_220_stochastic_readiness.json"),
            "stochastic_audit": exists(self.outputs_root / "prod201_220_audit_report.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Run multiple seeds and larger batches; then create real-document anonymized batch runner.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def __getattr__(self, name):
        mapping = {
            "random_cases": ("prod201_220_random_cases.json", "random_cases"),
            "scored_cases": ("prod201_220_scored_cases.json", "scored_cases"),
            "anomaly_report": ("prod201_220_anomaly_report.json", "anomaly_report"),
            "family_behavior": ("prod201_220_family_behavior.json", "family_behavior"),
            "ambiguity_behavior": ("prod201_220_ambiguity_behavior.json", "ambiguity_behavior"),
            "risk_behavior": ("prod201_220_risk_behavior.json", "risk_behavior"),
            "stochastic_study_plan": ("prod201_220_stochastic_study_plan.json", "stochastic_study_plan"),
            "calibration_policy": ("prod201_220_calibration_policy.json", "calibration_policy"),
            "stochastic_readiness": ("prod201_220_stochastic_readiness.json", "stochastic_readiness"),
            "stochastic_audit": ("prod201_220_audit_report.json", "stochastic_audit"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod201_220_anomaly_report.md",
            "prod201_220_stochastic_study_plan.md",
            "prod201_220_calibration_policy.md",
            "prod201_220_stochastic_readiness.md",
            "prod201_220_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
