#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/public_https_runtime.contract.json",
    "product/contracts/fastapi_deploy_adapter.contract.json",
    "product/contracts/custom_gpt_public_actions.contract.json",
    "product/contracts/deploy_security_gate.contract.json",
    "product/contracts/runtime_environment.contract.json",
    "product/schemas/public_runtime_deploy.schema.json",
    "product/schemas/public_actions_openapi.schema.json",
    "product/scripts/build_public_https_runtime_adapter.py",
    "product/deploy/fastapi_runtime_adapter.py",
    "product/deploy/requirements.txt",
    "outputs/prod151_160_openapi_spec.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--public-base-url", default="http://127.0.0.1:8098")
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_public_https_runtime_adapter.py"), "--repo", str(repo), "--public-base-url", args.public_base_url])
        if code != 0:
            errors.append("build_public_https_runtime_adapter failed: " + out)

    outputs = [
        "outputs/prod161_170_public_openapi_spec.json",
        "outputs/prod161_170_deployment_plan.json",
        "outputs/prod161_170_fastapi_adapter.json",
        "outputs/prod161_170_action_import_guide.json",
        "outputs/prod161_170_security_gate.json",
        "outputs/prod161_170_parser_task_mode.json",
        "outputs/prod161_170_public_runtime_readiness.json",
        "outputs/prod161_170_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    spec_path = repo / "outputs/prod161_170_public_openapi_spec.json"
    if spec_path.exists():
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        if spec.get("openapi") != "3.1.0":
            errors.append("public OpenAPI spec missing version")
        server_url = spec.get("servers", [{}])[0].get("url", "")
        if not server_url.startswith("https://"):
            warnings.append("public base URL is not HTTPS; valid for local planning only")

    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 2, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
