#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/human_review_pilot_board.contract.json",
    "product/contracts/pilot_decision_ledger.contract.json",
    "product/contracts/human_review_recommendation.contract.json",
    "product/contracts/pilot_board_readiness.contract.json",
    "product/schemas/human_review_board_item.schema.json",
    "product/schemas/pilot_decision_ledger.schema.json",
    "product/schemas/human_review_findings.schema.json",
    "product/schemas/human_review_readiness.schema.json",
    "product/scripts/run_human_review_pilot_board.py",
    "product/scripts/build_human_review_pilot_board.py",
    "outputs/prod721_760_business_pilot_readiness.json",
    "outputs/prod721_760_business_pilot_runs.json",
    "outputs/prod721_760_business_pilot_feedback_seed.json",
]

OUTPUTS = [
    "outputs/prod761_800_human_review_board_status.json",
    "outputs/prod761_800_human_review_board.json",
    "outputs/prod761_800_decision_ledger.json",
    "outputs/prod761_800_human_review_findings.json",
    "outputs/prod761_800_human_review_recommendations.json",
    "outputs/prod761_800_human_review_readiness.json",
    "outputs/prod761_800_human_review_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod721_760_business_pilot_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_HUMAN_REVIEWED_20_CASE_BUSINESS_PILOT":
        errors.append("upstream PROD-721 readiness is not ready for human review board")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_human_review_pilot_board.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    board = json.loads((repo / "outputs/prod761_800_human_review_board.json").read_text(encoding="utf-8"))
    if board.get("case_count") != 20:
        errors.append("human review board must contain exactly 20 cases")
    ledger = json.loads((repo / "outputs/prod761_800_decision_ledger.json").read_text(encoding="utf-8"))
    if ledger.get("ledger_count") != 20:
        errors.append("decision ledger must contain exactly 20 entries")
    recs = json.loads((repo / "outputs/prod761_800_human_review_recommendations.json").read_text(encoding="utf-8"))
    if recs.get("auto_apply") is not False:
        errors.append("human review recommendations auto_apply must be false")
    audit = json.loads((repo / "outputs/prod761_800_human_review_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 7, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
