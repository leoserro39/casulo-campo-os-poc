#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/negation_aware_execution_intent_hotfix.contract.json",
    "product/contracts/execution_intent_classifier.contract.json",
    "product/contracts/false_block_regression.contract.json",
    "product/contracts/execution_intent_readiness.contract.json",
    "product/schemas/execution_intent_classification.schema.json",
    "product/schemas/false_block_regression.schema.json",
    "product/schemas/execution_intent_readiness.schema.json",
    "product/scripts/patch_business_runner_negation_intent.py",
    "product/scripts/run_negation_aware_execution_intent_hotfix.py",
    "product/scripts/build_negation_aware_execution_intent_hotfix.py",
    "outputs/prod761_800_human_review_readiness.json",
    "outputs/prod721_760_business_pilot_case_pack.json",
    "outputs/prod721_760_business_pilot_decisions.json",
]

OUTPUTS = [
    "outputs/prod801_820_execution_intent_status.json",
    "outputs/prod801_820_execution_intent_classifications.json",
    "outputs/prod801_820_false_block_regression.json",
    "outputs/prod801_820_business_pilot_fixed_runs.json",
    "outputs/prod801_820_business_pilot_fixed_decisions.json",
    "outputs/prod801_820_false_block_resolution.json",
    "outputs/prod801_820_execution_intent_recommendations.json",
    "outputs/prod801_820_execution_intent_readiness.json",
    "outputs/prod801_820_execution_intent_audit_report.json",
]

EXPECTED_FALSE_BLOCKS = ["PILOT-001", "PILOT-007", "PILOT-016"]
EXPECTED_DIRECT_BLOCKS = ["PILOT-014", "PILOT-015", "PILOT-020"]

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)
errors = []

for rel in REQUIRED:
    if not (repo / rel).exists():
        errors.append(f"missing {rel}")

if not errors:
    upstream = json.loads((repo / "outputs/prod761_800_human_review_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_HUMAN_REVIEW_SESSION_NOT_THRESHOLD_MUTATION":
        errors.append("upstream PROD-761 readiness is not ready for execution-intent hotfix")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_negation_aware_execution_intent_hotfix.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    resolution = json.loads((repo / "outputs/prod801_820_false_block_resolution.json").read_text(encoding="utf-8"))
    for case_id in EXPECTED_FALSE_BLOCKS:
        if case_id not in resolution.get("resolved_false_block_candidates", []):
            errors.append(f"expected false block candidate not resolved: {case_id}")
    for case_id in EXPECTED_DIRECT_BLOCKS:
        if case_id not in resolution.get("direct_execution_blocks_preserved", []):
            errors.append(f"direct execution block not preserved: {case_id}")

    audit = json.loads((repo / "outputs/prod801_820_execution_intent_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    readiness = json.loads((repo / "outputs/prod801_820_execution_intent_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_PILOT_BOARD_REFRESH_AFTER_INTENT_HOTFIX":
        errors.append("readiness decision must be READY_FOR_PILOT_BOARD_REFRESH_AFTER_INTENT_HOTFIX")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 9, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
