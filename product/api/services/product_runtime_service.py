from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


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


def read_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
        self.store_root = repo_root / "product" / "store"

    def health(self) -> Dict:
        return {"status": "PASS", "product_direction": PRODUCT_DIRECTION, "runtime_mode": RUNTIME_MODE, "blocked_actions": BLOCKED_ACTIONS}

    def product_status(self) -> Dict:
        checks = {
            "store_readiness": exists(self.outputs_root / "prod171_180_store_readiness.json"),
            "case_catalog": exists(self.outputs_root / "prod181_200_case_catalog.json"),
            "first_three_case_plan": exists(self.outputs_root / "prod181_200_first_three_case_plan.json"),
            "batch_calibration_plan": exists(self.outputs_root / "prod181_200_batch_calibration_plan.json"),
            "case_runner_results": exists(self.outputs_root / "prod181_200_case_runner_results.json"),
            "enterprise_import_kit": exists(self.outputs_root / "prod181_200_enterprise_import_kit.json"),
            "case_runner_readiness": exists(self.outputs_root / "prod181_200_case_runner_readiness.json"),
            "case_runner_audit": exists(self.outputs_root / "prod181_200_audit_report.json"),
            "case_runs_jsonl": exists(self.outputs_root / "prod181_200_case_runs.jsonl"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Run first three parser cases one by one; then expand batch calibration by type.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def case_runs(self) -> Dict:
        return {"status": "PASS", "case_runs": read_jsonl(self.outputs_root / "prod181_200_case_runs.jsonl")}

    def __getattr__(self, name):
        mapping = {
            "case_catalog": ("prod181_200_case_catalog.json", "case_catalog"),
            "first_three_case_plan": ("prod181_200_first_three_case_plan.json", "first_three_case_plan"),
            "batch_calibration_plan": ("prod181_200_batch_calibration_plan.json", "batch_calibration_plan"),
            "case_runner_results": ("prod181_200_case_runner_results.json", "case_runner_results"),
            "enterprise_import_kit": ("prod181_200_enterprise_import_kit.json", "enterprise_import_kit"),
            "case_runner_readiness": ("prod181_200_case_runner_readiness.json", "case_runner_readiness"),
            "case_runner_audit": ("prod181_200_audit_report.json", "case_runner_audit"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod181_200_case_catalog.md",
            "prod181_200_first_three_case_plan.md",
            "prod181_200_batch_calibration_plan.md",
            "prod181_200_case_runner_results.md",
            "prod181_200_enterprise_import_kit.md",
            "prod181_200_case_runner_readiness.md",
            "prod181_200_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
