#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/state_store_baseline.contract.json",
    "product/contracts/evidence_store_baseline.contract.json",
    "product/contracts/graph_store_baseline.contract.json",
    "product/contracts/store_write_policy.contract.json",
    "product/contracts/enterprise_workspace_integration.contract.json",
    "product/contracts/store_migration_path.contract.json",
    "product/schemas/state_record.schema.json",
    "product/schemas/evidence_record.schema.json",
    "product/schemas/graph_record.schema.json",
    "product/scripts/build_state_evidence_graph_store.py",
    "outputs/prod161_170_public_runtime_readiness.json",
    "outputs/prod161_170_parser_task_mode.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_state_evidence_graph_store.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_state_evidence_graph_store failed: " + out)

    outputs = [
        "outputs/prod171_180_store_status.json",
        "outputs/prod171_180_state_store_index.json",
        "outputs/prod171_180_evidence_store_index.json",
        "outputs/prod171_180_graph_store_index.json",
        "outputs/prod171_180_store_write_policy.json",
        "outputs/prod171_180_enterprise_workspace_integration.json",
        "outputs/prod171_180_store_migration_path.json",
        "outputs/prod171_180_store_readiness.json",
        "outputs/prod171_180_audit_report.json",
        "product/store/state_records.jsonl",
        "product/store/evidence_records.jsonl",
        "product/store/graph_records.jsonl",
        "product/store/audit_records.jsonl",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    if count_jsonl(repo / "product/store/state_records.jsonl") < 3:
        errors.append("state store has too few records")
    if count_jsonl(repo / "product/store/evidence_records.jsonl") < 4:
        errors.append("evidence store has too few records")
    if count_jsonl(repo / "product/store/graph_records.jsonl") < 2:
        errors.append("graph store has too few records")

    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 3, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
