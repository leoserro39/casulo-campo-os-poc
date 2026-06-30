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
    "outputs/prod1221_1260_readiness.json",
    "outputs/prod941_980_graph_export_nodes.jsonl",
    "outputs/prod941_980_graph_export_relationships.jsonl",
    "product/scripts/generate_graph_import_sandbox_cypher.py",
    "product/scripts/run_graph_import_sandbox_dry_run.py",
    "product/scripts/build_graph_import_sandbox_dry_run.py",
    "product/config/neo4j_sandbox_docker_compose.example.yml",
    "product/config/neo4j_sandbox_import.env.example",
]
errors = [f"missing {x}" for x in required if not (repo / x).exists()]

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_graph_import_sandbox_dry_run.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

outputs = [
    "outputs/prod1261_1300_graph_import_sandbox_dry_run.json",
    "outputs/prod1261_1300_neo4j_manual_runbook.json",
    "outputs/prod1261_1300_graph_validation_queries.json",
    "outputs/prod1261_1300_readiness.json",
    "outputs/prod1261_1300_audit_report.json",
    "outputs/prod1261_1300_neo4j_sandbox_import_preview.cypher",
]
for x in outputs:
    if not (repo / x).exists():
        errors.append(f"missing output {x}")

if not errors:
    readiness = json.loads((repo / "outputs/prod1261_1300_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_MANUAL_NEO4J_SANDBOX_IMPORT_AND_GRAPH_RETRIEVAL_GAIN_EVALUATION":
        errors.append("unexpected readiness")
    dry = json.loads((repo / "outputs/prod1261_1300_graph_import_sandbox_dry_run.json").read_text(encoding="utf-8"))
    if dry.get("neo4j_connection_attempted") is not False:
        errors.append("neo4j_connection_attempted must be false")
    if dry.get("cypher_executed") is not False:
        errors.append("cypher_executed must be false")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(required) + len(outputs) + 4, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
