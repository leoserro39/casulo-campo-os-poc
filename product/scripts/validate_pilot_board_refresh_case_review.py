#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/pilot_board_refresh.contract.json",
    "product/contracts/case_level_review_decision.contract.json",
    "product/contracts/pilot_refresh_ledger.contract.json",
    "product/contracts/pilot_refresh_readiness.contract.json",
    "product/schemas/pilot_board_refresh_item.schema.json",
    "product/schemas/pilot_refresh_ledger.schema.json",
    "product/schemas/case_level_review_summary.schema.json",
    "product/schemas/pilot_refresh_readiness.schema.json",
    "product/scripts/run_pilot_board_refresh_case_review.py",
    "product/scripts/build_pilot_board_refresh_case_review.py",
    "outputs/prod801_820_execution_intent_readiness.json",
    "outputs/prod801_820_business_pilot_fixed_decisions.json",
    "outputs/prod801_820_false_block_resolution.json",
    "outputs/prod761_800_human_review_board.json",
]

OUTPUTS = [
    "outputs/prod821_860_pilot_board_refresh_status.json",
    "outputs/prod821_860_pilot_board_refresh.json",
    "outputs/prod821_860_case_level_decision_ledger.json",
    "outputs/prod821_860_pilot_board_refresh_findings.json",
    "outputs/prod821_860_case_level_recommendations.json",
    "outputs/prod821_860_pilot_board_refresh_readiness.json",
    "outputs/prod821_860_pilot_board_refresh_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod801_820_execution_intent_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_PILOT_BOARD_REFRESH_AFTER_INTENT_HOTFIX":
        errors.append("upstream PROD-801 readiness is not ready for pilot board refresh")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_pilot_board_refresh_case_review.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    board = json.loads((repo / "outputs/prod821_860_pilot_board_refresh.json").read_text(encoding="utf-8"))
    if board.get("case_count") != 20:
        errors.append("refreshed board must contain exactly 20 cases")
    ledger = json.loads((repo / "outputs/prod821_860_case_level_decision_ledger.json").read_text(encoding="utf-8"))
    if ledger.get("ledger_count") != 20:
        errors.append("refreshed ledger must contain exactly 20 entries")
    recs = json.loads((repo / "outputs/prod821_860_case_level_recommendations.json").read_text(encoding="utf-8"))
    if recs.get("auto_apply") is not False:
        errors.append("case-level recommendations auto_apply must be false")
    audit = json.loads((repo / "outputs/prod821_860_pilot_board_refresh_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    readiness = json.loads((repo / "outputs/prod821_860_pilot_board_refresh_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_CASE_LEVEL_HUMAN_DECISION_SESSION":
        errors.append("readiness decision must be READY_FOR_CASE_LEVEL_HUMAN_DECISION_SESSION")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 8, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
