#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/business_diagnostic_report_pack.contract.json",
    "product/contracts/graph_adapter_boundary.contract.json",
    "product/contracts/diagnostic_case_report.contract.json",
    "product/contracts/diagnostic_readiness.contract.json",
    "product/schemas/business_diagnostic_report.schema.json",
    "product/schemas/graph_adapter_boundary.schema.json",
    "product/schemas/diagnostic_case_report.schema.json",
    "product/schemas/diagnostic_readiness.schema.json",
    "product/scripts/run_business_diagnostic_report_pack.py",
    "product/scripts/build_business_diagnostic_report_pack.py",
    "outputs/prod941_980_dry_run_readiness.json",
    "outputs/prod941_980_50_case_dry_run_status.json",
    "outputs/prod941_980_business_diagnostic_selection.json",
    "outputs/prod941_980_graph_export_summary.json",
]

OUTPUTS = [
    "outputs/prod981_1020_business_diagnostic_report_pack.json",
    "outputs/prod981_1020_diagnostic_case_reports.json",
    "outputs/prod981_1020_graph_adapter_boundary.json",
    "outputs/prod981_1020_business_diagnostic_recommendations.json",
    "outputs/prod981_1020_business_diagnostic_readiness.json",
    "outputs/prod981_1020_business_diagnostic_audit_report.json",
    "outputs/prod981_1020_business_diagnostic_report_pack.md",
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
    upstream = json.loads((repo / "outputs/prod941_980_dry_run_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY":
        errors.append("upstream PROD-941 readiness is not ready for business diagnostic report pack")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_business_diagnostic_report_pack.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    report = json.loads((repo / "outputs/prod981_1020_business_diagnostic_report_pack.json").read_text(encoding="utf-8"))
    if report.get("case_count") != 50:
        errors.append("business diagnostic pack must reference exactly 50 cases")
    boundary = json.loads((repo / "outputs/prod981_1020_graph_adapter_boundary.json").read_text(encoding="utf-8"))
    if boundary.get("neo4j_connection_allowed") is not False:
        errors.append("neo4j_connection_allowed must be false")
    if boundary.get("live_graph_database_write_allowed") is not False:
        errors.append("live_graph_database_write_allowed must be false")
    audit = json.loads((repo / "outputs/prod981_1020_business_diagnostic_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    readiness = json.loads((repo / "outputs/prod981_1020_business_diagnostic_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_CONTROLLED_DEMO_EVIDENCE_PACK_AND_NON_LIVE_GRAPH_IMPORT_REVIEW":
        errors.append("readiness decision must be READY_FOR_CONTROLLED_DEMO_EVIDENCE_PACK_AND_NON_LIVE_GRAPH_IMPORT_REVIEW")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 9, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
