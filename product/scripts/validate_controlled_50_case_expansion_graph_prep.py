#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/controlled_50_case_expansion_design.contract.json",
    "product/contracts/graph_persistence_prep.contract.json",
    "product/contracts/graph_entity_mapping.contract.json",
    "product/contracts/expansion_readiness.contract.json",
    "product/schemas/controlled_50_case_candidate.schema.json",
    "product/schemas/graph_node_mapping.schema.json",
    "product/schemas/graph_relationship_mapping.schema.json",
    "product/schemas/expansion_readiness.schema.json",
    "product/scripts/run_controlled_50_case_expansion_graph_prep.py",
    "product/scripts/build_controlled_50_case_expansion_graph_prep.py",
    "outputs/prod861_900_closure_readiness.json",
]

OUTPUTS = [
    "outputs/prod901_940_controlled_50_case_expansion_status.json",
    "outputs/prod901_940_controlled_50_case_candidate_pack.json",
    "outputs/prod901_940_gate_expectation_plan.json",
    "outputs/prod901_940_expansion_risk_plan.json",
    "outputs/prod901_940_graph_node_mapping.json",
    "outputs/prod901_940_graph_relationship_mapping.json",
    "outputs/prod901_940_graph_persistence_prep.json",
    "outputs/prod901_940_expansion_recommendations.json",
    "outputs/prod901_940_expansion_readiness.json",
    "outputs/prod901_940_expansion_audit_report.json",
    "outputs/prod901_940_graph_cypher_stub.cypher",
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
    upstream = json.loads((repo / "outputs/prod861_900_closure_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CONTROLLED_50_CASE_EXPANSION_DESIGN_NOT_EXECUTION":
        errors.append("upstream PROD-861 readiness is not ready for 50-case design")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_controlled_50_case_expansion_graph_prep.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    pack = json.loads((repo / "outputs/prod901_940_controlled_50_case_candidate_pack.json").read_text(encoding="utf-8"))
    if pack.get("case_count") != 50:
        errors.append("candidate pack must contain exactly 50 cases")
    prep = json.loads((repo / "outputs/prod901_940_graph_persistence_prep.json").read_text(encoding="utf-8"))
    if prep.get("neo4j_connection_allowed") is not False:
        errors.append("neo4j_connection_allowed must be false")
    if prep.get("live_graph_database_write_allowed") is not False:
        errors.append("live_graph_database_write_allowed must be false")
    audit = json.loads((repo / "outputs/prod901_940_expansion_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("execution_allowed") is not False:
        errors.append("execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    readiness = json.loads((repo / "outputs/prod901_940_expansion_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_CONTROLLED_50_CASE_DRY_RUN_AND_GRAPH_EXPORT_STUB":
        errors.append("readiness decision must be READY_FOR_CONTROLLED_50_CASE_DRY_RUN_AND_GRAPH_EXPORT_STUB")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 10, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
