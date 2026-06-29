#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/controlled_20_case_business_pilot.contract.json",
    "product/contracts/business_pilot_case_pack.contract.json",
    "product/contracts/business_pilot_feedback_seed.contract.json",
    "product/contracts/business_pilot_readiness.contract.json",
    "product/schemas/business_pilot_case.schema.json",
    "product/schemas/business_pilot_run.schema.json",
    "product/schemas/business_pilot_analysis.schema.json",
    "product/schemas/business_pilot_readiness.schema.json",
    "product/scripts/run_controlled_20_case_business_pilot.py",
    "product/scripts/build_controlled_20_case_business_pilot.py",
    "outputs/prod681_720_feedback_readiness.json",
    "product/scripts/run_business_case_interactive_runner.py",
]

OUTPUTS = [
    "outputs/prod721_760_business_pilot_case_pack.json",
    "outputs/prod721_760_business_pilot_status.json",
    "outputs/prod721_760_business_pilot_runs.json",
    "outputs/prod721_760_business_pilot_decisions.json",
    "outputs/prod721_760_business_pilot_feedback_seed.json",
    "outputs/prod721_760_business_pilot_analysis.json",
    "outputs/prod721_760_business_pilot_calibration_recommendations.json",
    "outputs/prod721_760_business_pilot_readiness.json",
    "outputs/prod721_760_business_pilot_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod681_720_feedback_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CONTROLLED_20_CASE_FEEDBACK_PILOT":
        errors.append("upstream PROD-681 readiness is not ready for 20-case pilot")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_controlled_20_case_business_pilot.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    case_pack = json.loads((repo / "outputs/prod721_760_business_pilot_case_pack.json").read_text(encoding="utf-8"))
    if case_pack.get("case_count") != 20:
        errors.append("pilot case pack must contain exactly 20 cases")
    runs = json.loads((repo / "outputs/prod721_760_business_pilot_runs.json").read_text(encoding="utf-8"))
    if runs.get("case_count") != 20:
        errors.append("pilot must run exactly 20 cases")
    recs = json.loads((repo / "outputs/prod721_760_business_pilot_calibration_recommendations.json").read_text(encoding="utf-8"))
    if recs.get("auto_apply") is not False:
        errors.append("pilot calibration auto_apply must be false")
    audit = json.loads((repo / "outputs/prod721_760_business_pilot_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 7, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
