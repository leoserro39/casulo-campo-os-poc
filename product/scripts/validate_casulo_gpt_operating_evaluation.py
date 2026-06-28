#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/casulo_method.contract.json",
    "product/contracts/company_chat_intake.contract.json",
    "product/contracts/gpt_operating_layer.contract.json",
    "product/contracts/evidence_harvest.contract.json",
    "product/contracts/operational_map.contract.json",
    "product/contracts/evaluation_layer.contract.json",
    "product/contracts/hallucination_index.contract.json",
    "product/contracts/delta_index.contract.json",
    "product/contracts/response_gate.contract.json",
    "product/contracts/calibration.contract.json",
    "product/contracts/technical_readiness_gate.contract.json",
    "product/schemas/casulo_evaluation_report.schema.json",
    "product/schemas/gpt_operating_session.schema.json",
    "product/scripts/build_casulo_gpt_operating_evaluation.py",
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
        code, out = run([sys.executable, str(repo / "product/scripts/build_casulo_gpt_operating_evaluation.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build failed: " + out)
    outputs = [
        "outputs/prod081_120_casulo_method.json",
        "outputs/prod081_120_company_chat_intake.json",
        "outputs/prod081_120_gpt_operating_layer.json",
        "outputs/prod081_120_evaluation_cases.json",
        "outputs/prod081_120_hallucination_index.json",
        "outputs/prod081_120_delta_index.json",
        "outputs/prod081_120_evaluation_report.json",
        "outputs/prod081_120_technical_readiness_gate.json",
        "outputs/prod081_120_calibration_ledger.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")
    report_path = repo / "outputs/prod081_120_evaluation_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") != "PASS":
            errors.append("evaluation report status is not PASS")
        if len(report.get("cases", [])) < 5:
            errors.append("less than 5 evaluation cases")
        gate = report.get("readiness_gate", {})
        if gate.get("gate") != "READY_FOR_COMPANY_INCUBATOR_AND_POC_SERVICES":
            errors.append("readiness gate not generated")
    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 3, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
