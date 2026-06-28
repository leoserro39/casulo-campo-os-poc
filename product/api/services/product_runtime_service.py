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
            "public_runtime_readiness": exists(self.outputs_root / "prod161_170_public_runtime_readiness.json"),
            "parser_task_mode": exists(self.outputs_root / "prod161_170_parser_task_mode.json"),
            "store_status": exists(self.outputs_root / "prod171_180_store_status.json"),
            "state_store_index": exists(self.outputs_root / "prod171_180_state_store_index.json"),
            "evidence_store_index": exists(self.outputs_root / "prod171_180_evidence_store_index.json"),
            "graph_store_index": exists(self.outputs_root / "prod171_180_graph_store_index.json"),
            "store_write_policy": exists(self.outputs_root / "prod171_180_store_write_policy.json"),
            "enterprise_workspace_integration": exists(self.outputs_root / "prod171_180_enterprise_workspace_integration.json"),
            "store_migration_path": exists(self.outputs_root / "prod171_180_store_migration_path.json"),
            "store_readiness": exists(self.outputs_root / "prod171_180_store_readiness.json"),
            "store_audit": exists(self.outputs_root / "prod171_180_audit_report.json"),
            "state_records": exists(self.store_root / "state_records.jsonl"),
            "evidence_records": exists(self.store_root / "evidence_records.jsonl"),
            "graph_records": exists(self.store_root / "graph_records.jsonl"),
            "audit_records": exists(self.store_root / "audit_records.jsonl"),
        }
        return {
            "status": "PASS" if all(checks.values()) else "INCOMPLETE",
            "product_direction": PRODUCT_DIRECTION,
            "runtime_mode": RUNTIME_MODE,
            "checks": checks,
            "store_counts": {
                "state_records": len(read_jsonl(self.store_root / "state_records.jsonl")),
                "evidence_records": len(read_jsonl(self.store_root / "evidence_records.jsonl")),
                "graph_records": len(read_jsonl(self.store_root / "graph_records.jsonl")),
                "audit_records": len(read_jsonl(self.store_root / "audit_records.jsonl")),
            },
            "blocked_actions": BLOCKED_ACTIONS,
            "next_recommended_step": "Build Enterprise Custom GPT Import Kit / Parser POC Runbook.",
        }

    def _payload(self, stem: str, key: str) -> Dict:
        return payload(self.outputs_root / stem, key)

    def state_records(self) -> Dict:
        return {"status": "PASS", "state_records": read_jsonl(self.store_root / "state_records.jsonl")}

    def evidence_records(self) -> Dict:
        return {"status": "PASS", "evidence_records": read_jsonl(self.store_root / "evidence_records.jsonl")}

    def graph_records(self) -> Dict:
        return {"status": "PASS", "graph_records": read_jsonl(self.store_root / "graph_records.jsonl")}

    def store_audit_records(self) -> Dict:
        return {"status": "PASS", "audit_records": read_jsonl(self.store_root / "audit_records.jsonl")}

    def __getattr__(self, name):
        mapping = {
            "store_status": ("prod171_180_store_status.json", "store_status"),
            "state_store_index": ("prod171_180_state_store_index.json", "state_store_index"),
            "evidence_store_index": ("prod171_180_evidence_store_index.json", "evidence_store_index"),
            "graph_store_index": ("prod171_180_graph_store_index.json", "graph_store_index"),
            "store_write_policy": ("prod171_180_store_write_policy.json", "store_write_policy"),
            "enterprise_workspace_integration": ("prod171_180_enterprise_workspace_integration.json", "enterprise_workspace_integration"),
            "store_migration_path": ("prod171_180_store_migration_path.json", "store_migration_path"),
            "store_readiness": ("prod171_180_store_readiness.json", "store_readiness"),
            "store_audit": ("prod171_180_audit_report.json", "store_audit"),
        }
        if name in mapping:
            stem, key = mapping[name]
            return lambda: self._payload(stem, key)
        raise AttributeError(name)

    def reports(self) -> Dict:
        patterns = [
            "prod171_180_store_status.md",
            "prod171_180_state_store_index.md",
            "prod171_180_evidence_store_index.md",
            "prod171_180_graph_store_index.md",
            "prod171_180_store_write_policy.md",
            "prod171_180_enterprise_workspace_integration.md",
            "prod171_180_store_readiness.md",
            "prod171_180_audit_report.md",
        ]
        reports = []
        for name in patterns:
            path = self.outputs_root / name
            reports.append({"name": name, "exists": path.exists(), "path": str(path), "preview": read_text(path)[:1200] if path.exists() else ""})
        return {"status": "PASS", "reports": reports}
