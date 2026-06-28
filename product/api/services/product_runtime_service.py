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
            "stochastic_anomaly_report": exists(self.outputs_root / "prod201_220_anomaly_report.json"),
            "multi_seed_runs": exists(self.outputs_root / "prod221_240_multi_seed_runs.json"),
            "stability_report": exists(self.outputs_root / "prod221_240_stability_report.json"),
            "drift_report": exists(self.outputs_root / "prod221_240_drift_report.json"),
            "anomaly_cluster_report": exists(self.outputs_root / "prod221_240_anomaly_cluster_report.json"),
            "threshold_recommendations": exists(self.outputs_root / "prod221_240_calibrated_threshold_recommendations.json"),
            "seed_summary": exists(self.outputs_root / "prod221_240_seed_summary.csv"),
            "all_seed_cases": exists(self.outputs_root / "prod221_240_scored_cases_all_seeds.json"),
            "multi_seed_readiness": exists(self.outputs_root / "prod221_240_readiness.json"),
            "multi_seed_audit": exists(self.outputs_root / "prod221_240_audit_report.json"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Run anonymized real-document batch after synthetic multi-seed stability review.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def __getattr__(self, name):
        mapping = {
            "multi_seed_runs": ("prod221_240_multi_seed_runs.json", "multi_seed_runs"),
            "stability_report": ("prod221_240_stability_report.json", "stability_report"),
            "drift_report": ("prod221_240_drift_report.json", "drift_report"),
            "anomaly_cluster_report": ("prod221_240_anomaly_cluster_report.json", "anomaly_cluster_report"),
            "threshold_recommendations": ("prod221_240_calibrated_threshold_recommendations.json", "threshold_recommendations"),
            "multi_seed_readiness": ("prod221_240_readiness.json", "multi_seed_readiness"),
            "multi_seed_audit": ("prod221_240_audit_report.json", "multi_seed_audit"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod221_240_stability_report.md",
            "prod221_240_readiness.md",
            "prod221_240_audit_report.md",
            "prod221_240_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
