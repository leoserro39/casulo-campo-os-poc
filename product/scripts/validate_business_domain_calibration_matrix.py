#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED = [
    "product/contracts/business_domain_calibration_matrix.contract.json",
    "product/contracts/business_domain_intake.contract.json",
    "product/contracts/business_domain_sensitivity.contract.json",
    "product/contracts/business_domain_case_runner.contract.json",
    "product/contracts/business_domain_readiness.contract.json",
    "product/schemas/business_domain_matrix.schema.json",
    "product/schemas/business_domain_case.schema.json",
    "product/schemas/business_domain_batch_result.schema.json",
    "product/schemas/business_domain_readiness.schema.json",
    "product/scripts/run_business_domain_calibration_matrix.py",
    "product/scripts/build_business_domain_calibration_matrix.py",
    "outputs/prod602_620_solver_agent_readiness.json",
]

OUTPUTS = [
    "outputs/prod621_650_business_domain_matrix.json",
    "outputs/prod621_650_business_domain_cases.json",
    "outputs/prod621_650_business_domain_batch_result.json",
    "outputs/prod621_650_business_domain_metrics.json",
    "outputs/prod621_650_business_scenario_metrics.json",
    "outputs/prod621_650_business_intake_schema.json",
    "outputs/prod621_650_business_calibration_thresholds.json",
    "outputs/prod621_650_business_readiness.json",
    "outputs/prod621_650_business_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod602_620_solver_agent_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CONTROLLED_USER_CASE_INPUT_WITH_LIVE_DELTA":
        errors.append("upstream PROD-602 readiness is not ready for controlled business cases")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_business_domain_calibration_matrix.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    batch = json.loads((repo / "outputs/prod621_650_business_domain_batch_result.json").read_text(encoding="utf-8"))
    if batch.get("case_count", 0) < 100:
        errors.append("case_count must be at least 100")
    if batch.get("safe_behavior_rate_pct", 0) < 80:
        errors.append("safe_behavior_rate_pct must be at least 80")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 3, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)
