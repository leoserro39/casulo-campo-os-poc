#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/graph_builder_v0.contract.json",
    "product/contracts/state_store_index.contract.json",
    "product/contracts/domain_assisted_extraction.contract.json",
    "product/contracts/recommendation_governance.contract.json",
    "product/contracts/poc_factory.contract.json",
    "product/schemas/graph_builder_session.schema.json",
    "product/schemas/poc_factory_report.schema.json",
    "product/scripts/build_graph_builder_poc_factory.py",
    "outputs/prod081_120_technical_readiness_gate.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

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
        code, out = run([sys.executable, str(repo / "product/scripts/build_graph_builder_poc_factory.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_graph_builder_poc_factory failed: " + out)
    outputs = [
        "outputs/prod121_130_graph_builder_v0.json",
        "outputs/prod121_130_state_store_index.json",
        "outputs/prod121_130_recommendation_governance.json",
        "outputs/prod121_130_poc_factory_pack.json",
        "outputs/prod121_130_poc_readiness_report.json",
        "outputs/prod121_130_graph_builder_audit.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")
    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 1, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
