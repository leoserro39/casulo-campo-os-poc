#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/enterprise_parser_case_runner.contract.json",
    "product/contracts/parser_case_schema.contract.json",
    "product/contracts/batch_calibration_plan.contract.json",
    "product/contracts/enterprise_import_parser_poc.contract.json",
    "product/contracts/case_result_metrics.contract.json",
    "product/schemas/parser_case.schema.json",
    "product/schemas/parser_case_result.schema.json",
    "product/scripts/run_parser_case_runner.py",
    "product/scripts/build_enterprise_parser_case_runner.py",
    "outputs/prod171_180_store_readiness.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []

    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_enterprise_parser_case_runner.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_enterprise_parser_case_runner failed: " + out)

    outputs = [
        "outputs/prod181_200_case_catalog.json",
        "outputs/prod181_200_first_three_case_plan.json",
        "outputs/prod181_200_batch_calibration_plan.json",
        "outputs/prod181_200_case_runner_results.json",
        "outputs/prod181_200_enterprise_import_kit.json",
        "outputs/prod181_200_case_runner_readiness.json",
        "outputs/prod181_200_audit_report.json",
        "outputs/prod181_200_case_runs.jsonl",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    results_path = repo / "outputs/prod181_200_case_runner_results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        if results.get("summary", {}).get("cases_count", 0) < 3:
            errors.append("less than three cases")
        if not results.get("summary", {}).get("production_blocked_all_cases", False):
            errors.append("production not blocked in all cases")

    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 2, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
