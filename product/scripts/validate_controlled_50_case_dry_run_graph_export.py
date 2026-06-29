#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/controlled_50_case_dry_run.contract.json",
    "product/contracts/graph_export_stub.contract.json",
    "product/contracts/dry_run_diagnostic_selection.contract.json",
    "product/contracts/dry_run_readiness.contract.json",
    "product/schemas/dry_run_case_result.schema.json",
    "product/schemas/graph_export_node.schema.json",
    "product/schemas/graph_export_relationship.schema.json",
    "product/schemas/dry_run_readiness.schema.json",
    "product/scripts/run_controlled_50_case_dry_run_graph_export.py",
    "product/scripts/build_controlled_50_case_dry_run_graph_export.py",
    "outputs/prod901_940_expansion_readiness.json",
    "outputs/prod901_940_controlled_50_case_candidate_pack.json",
    "product/scripts/run_business_case_interactive_runner.py",
]

OUTPUTS = [
    "outputs/prod941_980_50_case_dry_run_status.json",
    "outputs/prod941_980_50_case_runnable_cases.json",
    "outputs/prod941_980_50_case_dry_run_runs.json",
    "outputs/prod941_980_50_case_dry_run_decisions.json",
    "outputs/prod941_980_graph_export_summary.json",
    "outputs/prod941_980_business_diagnostic_selection.json",
    "outputs/prod941_980_dry_run_recommendations.json",
    "outputs/prod941_980_dry_run_readiness.json",
    "outputs/prod941_980_dry_run_audit_report.json",
    "outputs/prod941_980_graph_export_nodes.jsonl",
    "outputs/prod941_980_graph_export_relationships.jsonl",
]

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)
errors = []

for rel in REQUIRED:
    if not (repo / rel).exists():
        errors.append(f"missing {rel}")

if not errors:
    upstream = json.loads((repo / "outputs/prod901_940_expansion_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CONTROLLED_50_CASE_DRY_RUN_AND_GRAPH_EXPORT_STUB":
        errors.append("upstream PROD-901 readiness is not ready for 50-case dry-run")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_controlled_50_case_dry_run_graph_export.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    runs = json.loads((repo / "outputs/prod941_980_50_case_dry_run_runs.json").read_text(encoding="utf-8"))
    if runs.get("case_count") != 50:
        errors.append("dry-run must contain exactly 50 runs")
    summary = json.loads((repo / "outputs/prod941_980_graph_export_summary.json").read_text(encoding="utf-8"))
    if summary.get("neo4j_connection_allowed") is not False:
        errors.append("neo4j_connection_allowed must be false")
    if summary.get("live_graph_database_write_allowed") is not False:
        errors.append("live_graph_database_write_allowed must be false")
    audit = json.loads((repo / "outputs/prod941_980_dry_run_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("graph_write_allowed") is not False:
        errors.append("graph_write_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    readiness = json.loads((repo / "outputs/prod941_980_dry_run_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY":
        errors.append("readiness decision must be READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 10, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
