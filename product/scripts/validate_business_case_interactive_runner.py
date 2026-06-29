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
    "product/contracts/runner_telemetry.contract.json",
    "product/contracts/runner_readiness.contract.json",
    "product/schemas/interactive_case_input.schema.json",
    "product/schemas/interactive_case_run.schema.json",
    "product/schemas/runner_telemetry.schema.json",
    "product/schemas/runner_readiness.schema.json",
    "product/scripts/run_business_case_interactive_runner.py",
    "product/scripts/build_business_case_interactive_runner.py",
    "outputs/prod621b_650b_readiness.json",
]

OUTPUTS = [
    "outputs/prod651_680_business_runner_status.json",
    "outputs/prod651_680_business_runner_input_schema.json",
    "outputs/prod651_680_business_runner_sample_cases.json",
    "outputs/prod651_680_business_runner_runs.json",
    "outputs/prod651_680_business_runner_decisions.json",
    "outputs/prod651_680_business_runner_output_modes.json",
    "outputs/prod651_680_business_runner_telemetry.json",
    "outputs/prod651_680_business_runner_readiness.json",
    "outputs/prod651_680_business_runner_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod621b_650b_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_BUSINESS_CASE_INTERACTIVE_RUNNER_WITH_PREFLIGHT":
        errors.append("upstream PROD-621B readiness is not ready for interactive runner")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_business_case_interactive_runner.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    audit = json.loads((repo / "outputs/prod651_680_business_runner_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")
    runs = json.loads((repo / "outputs/prod651_680_business_runner_runs.json").read_text(encoding="utf-8"))
    if runs.get("case_count", 0) < 5:
        errors.append("runner must produce at least 5 sample runs")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 4, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
