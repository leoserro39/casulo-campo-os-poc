#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED = [
    "product/contracts/common_workload_mass_test_lab.contract.json",
    "product/contracts/routine_solver_case.contract.json",
    "product/contracts/direct_vs_cubo_metrics.contract.json",
    "product/contracts/mass_test_batch_policy.contract.json",
    "product/contracts/common_workload_readiness.contract.json",
    "product/schemas/common_workload_case.schema.json",
    "product/schemas/common_workload_batch_result.schema.json",
    "product/schemas/direct_vs_cubo_metrics.schema.json",
    "product/schemas/common_workload_readiness.schema.json",
    "product/scripts/run_common_workload_mass_test_lab.py",
    "product/scripts/build_common_workload_mass_test_lab.py",
    "outputs/prod561_600_solver_api_surface.json",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--cases-per-workload", type=int, default=10)
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")
    if not errors:
        p = subprocess.run([
            sys.executable,
            str(repo / "product/scripts/build_common_workload_mass_test_lab.py"),
            "--repo",
            str(repo),
            "--cases-per-workload",
            str(args.cases_per_workload),
        ], capture_output=True, text=True)
        if p.returncode:
            errors.append("build failed: " + p.stdout + p.stderr)
    outputs = [
        "outputs/prod601_620_common_workload_fixture_pack.json",
        "outputs/prod601_620_common_workload_batch_result.json",
        "outputs/prod601_620_direct_vs_cubo_metrics.json",
        "outputs/prod601_620_workload_metrics.json",
        "outputs/prod601_620_readiness.json",
        "outputs/prod601_620_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")
    if not errors:
        batch = json.loads((repo / "outputs/prod601_620_common_workload_batch_result.json").read_text(encoding="utf-8"))
        if batch.get("case_count", 0) < 100:
            errors.append("case_count must be at least 100")
        if batch.get("network_call_performed") is not False:
            errors.append("network_call_performed must be false")
        if batch.get("real_user_data_used") is not False:
            errors.append("real_user_data_used must be false")
    print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 3, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
