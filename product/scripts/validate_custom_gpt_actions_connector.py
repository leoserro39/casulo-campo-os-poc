#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/custom_gpt_actions_connector.contract.json",
    "product/contracts/manual_chat_protocol.contract.json",
    "product/contracts/custom_gpt_instructions.contract.json",
    "product/contracts/openapi_action_schema.contract.json",
    "product/contracts/agent_connector_security.contract.json",
    "product/contracts/action_tool_router.contract.json",
    "product/schemas/custom_gpt_action_manifest.schema.json",
    "product/schemas/agent_connector_session.schema.json",
    "product/scripts/build_custom_gpt_actions_connector.py",
    "outputs/prod141_150_technical_readiness_memo.json",
    "outputs/prod141_150_chat_agent_operating_model.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base-url", default="http://127.0.0.1:8097")
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []

    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_custom_gpt_actions_connector.py"), "--repo", str(repo), "--base-url", args.base_url])
        if code != 0:
            errors.append("build_custom_gpt_actions_connector failed: " + out)

    outputs = [
        "outputs/prod151_160_openapi_spec.json",
        "outputs/prod151_160_custom_gpt_instructions.json",
        "outputs/prod151_160_action_manifest.json",
        "outputs/prod151_160_tool_router.json",
        "outputs/prod151_160_connector_session.json",
        "outputs/prod151_160_security_policy.json",
        "outputs/prod151_160_connector_readiness.json",
        "outputs/prod151_160_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    spec_path = repo / "outputs/prod151_160_openapi_spec.json"
    if spec_path.exists():
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        if spec.get("openapi") != "3.1.0":
            errors.append("OpenAPI version missing or invalid")
        if len(spec.get("paths", {})) < 8:
            errors.append("OpenAPI paths too few")

    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 2, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
