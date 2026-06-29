#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/business_case_interactive_runner.contract.json",
    "product/contracts/interactive_case_input.contract.json",
    "product/contracts/runner_output_mode_policy.contract.json",
    "product/contracts/runner_readiness.contract.json",
    "product/contracts/runner_telemetry.contract.json",
    "product/contracts/business_runner_risk_scale_hotfix.contract.json",
    "product/schemas/interactive_case_input.schema.json",
    "product/schemas/interactive_case_run.schema.json",
    "product/schemas/runner_readiness.schema.json",
    "product/schemas/runner_telemetry.schema.json",
    "product/schemas/business_runner_risk_integrity.schema.json",
    "product/scripts/run_business_case_interactive_runner.py",
    "product/scripts/build_business_case_interactive_runner.py",
    "outputs/prod651_680_business_runner_readiness.json",
]

OUTPUTS = [
    "outputs/prod651a_680a_business_runner_status.json",
    "outputs/prod651a_680a_business_runner_runs.json",
    "outputs/prod651a_680a_business_runner_decisions.json",
    "outputs/prod651a_680a_business_runner_telemetry.json",
    "outputs/prod651a_680a_business_runner_risk_integrity.json",
    "outputs/prod651a_680a_business_runner_readiness.json",
    "outputs/prod651a_680a_business_runner_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod651_680_business_runner_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CONTROLLED_ANONYMIZED_BUSINESS_CASE_PILOT":
        errors.append("upstream PROD-651 readiness is not ready for risk hotfix")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_business_case_interactive_runner.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    integrity = json.loads((repo / "outputs/prod651a_680a_business_runner_risk_integrity.json").read_text(encoding="utf-8"))
    checks = integrity.get("integrity_checks", {})
    for key, value in checks.items():
        if value is not True:
            errors.append(f"risk integrity check failed: {key}")
    stats = integrity.get("risk_statistics", {})
    if stats.get("max_adjusted_risk", 0) <= 1:
        errors.append("adjusted_risk still appears collapsed to unit scale")
    if stats.get("risk_range", 0) <= 5:
        errors.append("adjusted_risk range too small for calibration")
    audit = json.loads((repo / "outputs/prod651a_680a_business_runner_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 7, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
