#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/technical_readiness_memo.contract.json",
    "product/contracts/chat_agent_operating_model.contract.json",
    "product/contracts/target_stack.contract.json",
    "product/contracts/codex_github_bridge.contract.json",
    "product/contracts/incubator_technical_pack.contract.json",
    "product/schemas/technical_readiness_memo.schema.json",
    "product/schemas/chat_agent_operating_model.schema.json",
    "product/scripts/build_technical_readiness_incubator_pack.py",
    "outputs/prod131_140_poc_calibration_readiness.json",
    "outputs/prod131_140_calibration_results.json",
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
        code, out = run([sys.executable, str(repo / "product/scripts/build_technical_readiness_incubator_pack.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_technical_readiness_incubator_pack failed: " + out)
    outputs = [
        "outputs/prod141_150_technical_readiness_memo.json",
        "outputs/prod141_150_chat_agent_operating_model.json",
        "outputs/prod141_150_target_stack.json",
        "outputs/prod141_150_codex_github_bridge.json",
        "outputs/prod141_150_poc_service_blueprint.json",
        "outputs/prod141_150_risk_control_matrix.json",
        "outputs/prod141_150_technical_roadmap_90d.json",
        "outputs/prod141_150_incubator_technical_pack.json",
        "outputs/prod141_150_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")
    memo_path = repo / "outputs/prod141_150_technical_readiness_memo.json"
    if memo_path.exists():
        memo = json.loads(memo_path.read_text(encoding="utf-8"))
        if memo.get("status") != "PASS":
            errors.append("technical readiness memo not PASS")
        if "READY_FOR_COMPANY_INCUBATOR_INVESTOR" not in memo.get("readiness_decision", ""):
            errors.append("readiness decision not generated")
    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 2, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
