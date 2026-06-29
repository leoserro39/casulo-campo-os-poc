#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED = [
    "product/contracts/operator_console_surface.contract.json",
    "product/contracts/solver_api_surface.contract.json",
    "product/contracts/common_workload_lab_protocol.contract.json",
    "product/contracts/business_domain_lab_protocol.contract.json",
    "product/contracts/solver_input_safety_gate.contract.json",
    "product/schemas/operator_console_summary.schema.json",
    "product/schemas/solver_api_surface.schema.json",
    "product/schemas/common_workload_lab_protocol.schema.json",
    "product/schemas/solver_input_safety_gate.schema.json",
    "product/scripts/run_operator_console_solver_api_surface.py",
    "product/scripts/build_operator_console_solver_api_surface.py",
    "outputs/prod521_560_common_workload_mass_test_register.json",
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")
    if not errors:
        p = subprocess.run([sys.executable, str(repo / "product/scripts/build_operator_console_solver_api_surface.py"), "--repo", str(repo)], capture_output=True, text=True)
        if p.returncode:
            errors.append("build failed: " + p.stdout + p.stderr)
    outputs = [
        "outputs/prod561_600_operator_console_summary.json",
        "outputs/prod561_600_solver_api_surface.json",
        "outputs/prod561_600_common_workload_lab_protocol.json",
        "outputs/prod561_600_business_domain_lab_protocol.json",
        "outputs/prod561_600_solver_input_safety_gate.json",
        "outputs/prod561_600_readiness.json",
        "outputs/prod561_600_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")
    if not errors:
        solver = json.loads((repo / "outputs/prod561_600_solver_api_surface.json").read_text(encoding="utf-8"))
        if len(solver.get("planned_endpoints", [])) < 6:
            errors.append("planned solver endpoints are incomplete")
    print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 1, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
