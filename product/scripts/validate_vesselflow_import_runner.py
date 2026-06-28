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
        "product/scripts/run_vesselflow_state_definition.py",
        "product/contracts/vesselflow_data_import_runner.contract.json",
        "product/contracts/vesselflow_state_definition_runner.contract.json",
        "product/schemas/vesselflow_import_input.schema.json",
        "product/verticals/vesselflow/import_inputs/vesselflow_import_input.json",
        "product/verticals/vesselflow/import_templates/vesselflow_import_input_template.json",
    ]

    errors = []
    warnings = []
    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/run_vesselflow_state_definition.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("run_vesselflow_state_definition failed: " + out)

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
