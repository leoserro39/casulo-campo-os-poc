#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)

    required = [
        "product/ui/index.html",
        "product/ui/app.js",
        "product/api/product_runtime_api.py",
        "product/api/services/product_runtime_service.py",
        "product/scripts/export_vesselflow_state_report.py",
        "product/contracts/state_definition_panel.contract.json",
        "product/contracts/report_export.contract.json",
        "product/schemas/state_definition_panel.schema.json",
        "outputs/prod016_020_vesselflow_state_definition.json",
    ]
    errors = []
    warnings = []

    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/export_vesselflow_state_report.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("export_vesselflow_state_report failed: " + out)

    result = {
        "status": "FAIL" if errors else "PASS",
        "checks": len(required) + 1,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
