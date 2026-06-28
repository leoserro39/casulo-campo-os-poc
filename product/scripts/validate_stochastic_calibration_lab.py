#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/stochastic_calibration_lab.contract.json",
    "product/contracts/random_case_generator.contract.json",
    "product/contracts/fluctuation_anomaly_detector.contract.json",
    "product/contracts/ambiguity_behavior_model.contract.json",
    "product/contracts/calibration_decision_policy.contract.json",
    "product/schemas/stochastic_case.schema.json",
    "product/schemas/calibration_anomaly_report.schema.json",
    "product/scripts/generate_random_calibration_cases.py",
    "product/scripts/run_stochastic_calibration_study.py",
    "product/scripts/build_stochastic_calibration_lab.py",
    "outputs/prod181_200_case_runner_results.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260628)
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_stochastic_calibration_lab.py"), "--repo", str(repo), "--count", str(args.count), "--seed", str(args.seed)])
        if code != 0:
            errors.append("build_stochastic_calibration_lab failed: " + out)

    outputs = [
        "outputs/prod201_220_random_cases.json",
        "outputs/prod201_220_random_cases.csv",
        "outputs/prod201_220_scored_cases.json",
        "outputs/prod201_220_scored_cases.csv",
        "outputs/prod201_220_anomaly_report.json",
        "outputs/prod201_220_anomaly_report.md",
        "outputs/prod201_220_family_behavior.json",
        "outputs/prod201_220_ambiguity_behavior.json",
        "outputs/prod201_220_risk_behavior.json",
        "outputs/prod201_220_stochastic_study_plan.json",
        "outputs/prod201_220_calibration_policy.json",
        "outputs/prod201_220_stochastic_readiness.json",
        "outputs/prod201_220_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    report_path = repo / "outputs/prod201_220_anomaly_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("summary", {}).get("cases_count", 0) < args.count:
            errors.append("case count lower than requested")
        if not report.get("ambiguity_behavior"):
            errors.append("missing ambiguity behavior")
        if report.get("summary", {}).get("avg_hallucination_reduction", 0) <= 0:
            errors.append("no hallucination reduction measured")

    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 3, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
