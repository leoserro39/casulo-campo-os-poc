#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/interactive_runner_feedback_loop.contract.json",
    "product/contracts/runner_feedback_event.contract.json",
    "product/contracts/runner_feedback_calibration.contract.json",
    "product/contracts/runner_feedback_readiness.contract.json",
    "product/schemas/runner_feedback_event.schema.json",
    "product/schemas/runner_feedback_analysis.schema.json",
    "product/schemas/runner_feedback_calibration.schema.json",
    "product/schemas/runner_feedback_readiness.schema.json",
    "product/scripts/run_interactive_runner_feedback_calibration.py",
    "product/scripts/build_interactive_runner_feedback_calibration.py",
    "outputs/prod651a_680a_business_runner_readiness.json",
    "outputs/prod651a_680a_business_runner_runs.json",
]

OUTPUTS = [
    "outputs/prod681_720_feedback_loop_status.json",
    "outputs/prod681_720_feedback_events.json",
    "outputs/prod681_720_feedback_analysis.json",
    "outputs/prod681_720_feedback_taxonomy.json",
    "outputs/prod681_720_calibration_recommendations.json",
    "outputs/prod681_720_feedback_telemetry.json",
    "outputs/prod681_720_feedback_readiness.json",
    "outputs/prod681_720_feedback_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod651a_680a_business_runner_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_INTERACTIVE_FEEDBACK_CALIBRATION_LOOP":
        errors.append("upstream PROD-651A readiness is not ready for feedback loop")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_interactive_runner_feedback_calibration.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    recs = json.loads((repo / "outputs/prod681_720_calibration_recommendations.json").read_text(encoding="utf-8"))
    if recs.get("auto_apply") is not False:
        errors.append("calibration auto_apply must be false")
    if recs.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic threshold mutation must be false")
    audit = json.loads((repo / "outputs/prod681_720_feedback_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    events = json.loads((repo / "outputs/prod681_720_feedback_events.json").read_text(encoding="utf-8"))
    if events.get("feedback_count", 0) < 6:
        errors.append("feedback_count must be at least 6 for seed loop")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 6, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
