#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/real_anonymous_poc_calibration.contract.json",
    "product/contracts/anonymized_company_case.contract.json",
    "product/contracts/delta_control_score.contract.json",
    "product/contracts/calibration_ledger_v1.contract.json",
    "product/contracts/poc_service_readiness.contract.json",
    "product/schemas/anonymized_company_case.schema.json",
    "product/schemas/poc_calibration_result.schema.json",
    "product/scripts/build_real_anonymous_poc_calibration.py",
    "outputs/prod121_130_poc_readiness_report.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--cases", default="")
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")
    if not errors:
        cmd = [sys.executable, str(repo / "product/scripts/build_real_anonymous_poc_calibration.py"), "--repo", str(repo)]
        if args.cases:
            cmd += ["--cases", args.cases]
        code, out = run(cmd)
        if code != 0:
            errors.append("build_real_anonymous_poc_calibration failed: " + out)
    outputs = [
        "outputs/prod131_140_poc_intake_template.json",
        "outputs/prod131_140_calibration_cases.json",
        "outputs/prod131_140_calibration_results.json",
        "outputs/prod131_140_calibration_ledger_v1.json",
        "outputs/prod131_140_delta_control_report.json",
        "outputs/prod131_140_poc_calibration_readiness.json",
        "outputs/prod131_140_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    results_path = repo / "outputs/prod131_140_calibration_results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        if results.get("status") != "PASS":
            errors.append("calibration results not PASS")
        if results.get("summary", {}).get("cases_count", 0) < 4:
            warnings.append("less than 4 calibration cases")
        if results.get("summary", {}).get("avg_delta_control_gain", 0) <= 0:
            errors.append("delta control gain did not improve")
    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 3, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
