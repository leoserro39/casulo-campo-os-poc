#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/case_level_human_decision_capture.contract.json",
    "product/contracts/board_closure.contract.json",
    "product/contracts/human_decision_summary.contract.json",
    "product/contracts/closure_readiness.contract.json",
    "product/schemas/case_level_human_decision.schema.json",
    "product/schemas/board_closure.schema.json",
    "product/schemas/human_decision_summary.schema.json",
    "product/schemas/closure_readiness.schema.json",
    "product/scripts/run_case_level_human_decision_capture.py",
    "product/scripts/build_case_level_human_decision_capture.py",
    "outputs/prod821_860_pilot_board_refresh_readiness.json",
    "outputs/prod821_860_pilot_board_refresh.json",
]

OUTPUTS = [
    "outputs/prod861_900_case_level_human_decision_template.json",
    "outputs/prod861_900_case_level_human_decisions.json",
    "outputs/prod861_900_board_closure.json",
    "outputs/prod861_900_closed_decision_ledger.json",
    "outputs/prod861_900_human_decision_summary.json",
    "outputs/prod861_900_case_level_recommendations.json",
    "outputs/prod861_900_closure_readiness.json",
    "outputs/prod861_900_closure_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod821_860_pilot_board_refresh_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CASE_LEVEL_HUMAN_DECISION_SESSION":
        errors.append("upstream PROD-821 readiness is not ready for case-level decision capture")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_case_level_human_decision_capture.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    closure = json.loads((repo / "outputs/prod861_900_board_closure.json").read_text(encoding="utf-8"))
    if closure.get("case_count") != 20:
        errors.append("closure must cover exactly 20 cases")
    if closure.get("closed_count") != 20:
        errors.append("closure must close exactly 20 cases in controlled seed mode")
    if closure.get("auto_apply") is not False:
        errors.append("closure auto_apply must be false")
    if closure.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    if closure.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    readiness = json.loads((repo / "outputs/prod861_900_closure_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_CONTROLLED_50_CASE_EXPANSION_DESIGN_NOT_EXECUTION":
        errors.append("readiness decision must be READY_FOR_CONTROLLED_50_CASE_EXPANSION_DESIGN_NOT_EXECUTION")
    decisions = json.loads((repo / "outputs/prod861_900_case_level_human_decisions.json").read_text(encoding="utf-8"))
    if decisions.get("validation", {}).get("auto_apply_violations"):
        errors.append("human decision validation has auto_apply violations")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 9, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
