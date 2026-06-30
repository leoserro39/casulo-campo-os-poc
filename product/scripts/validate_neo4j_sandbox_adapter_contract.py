#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)
required = [
    "outputs/prod1181_1220_readiness.json",
    "outputs/prod941_980_graph_export_nodes.jsonl",
    "outputs/prod941_980_graph_export_relationships.jsonl",
    "product/config/neo4j_sandbox.env.example",
    "product/contracts/neo4j_sandbox_adapter_contract.contract.json",
    "product/contracts/neo4j_allowed_cypher.contract.json",
    "product/contracts/neo4j_import_plan.contract.json",
    "product/contracts/neo4j_gain_test_contract.contract.json",
    "product/scripts/run_neo4j_sandbox_adapter_contract.py",
    "product/scripts/build_neo4j_sandbox_adapter_contract.py",
]
errors = [f"missing {x}" for x in required if not (repo / x).exists()]
if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_neo4j_sandbox_adapter_contract.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)
outputs = [
    "outputs/prod1221_1260_neo4j_sandbox_adapter_contract.json",
    "outputs/prod1221_1260_allowed_cypher_queries.json",
    "outputs/prod1221_1260_neo4j_import_plan.json",
    "outputs/prod1221_1260_neo4j_gain_test_contract.json",
    "outputs/prod1221_1260_readiness.json",
    "outputs/prod1221_1260_audit_report.json",
]
for x in outputs:
    if not (repo / x).exists():
        errors.append(f"missing output {x}")
if not errors:
    readiness = json.loads((repo / "outputs/prod1221_1260_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_GRAPH_IMPORT_SANDBOX_DRY_RUN":
        errors.append("unexpected readiness")
    adapter = json.loads((repo / "outputs/prod1221_1260_neo4j_sandbox_adapter_contract.json").read_text(encoding="utf-8"))
    if adapter.get("connection_allowed_now") is not False:
        errors.append("connection_allowed_now must be false")
    if adapter.get("production_connection_allowed") is not False:
        errors.append("production_connection_allowed must be false")
print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(required) + len(outputs) + 5, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
