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
        "product/scripts/prepare_vesselflow_real_data_intake.py",
        "product/contracts/vesselflow_real_data_intake.contract.json",
        "product/contracts/data_anonymization_gate.contract.json",
        "product/schemas/vesselflow_real_data_intake.schema.json",
        "product/verticals/vesselflow/real_data_intake/vesselflow_real_data_intake_template.json",
        "product/verticals/vesselflow/real_data_intake/README.md",
    ]
    errors = []
    warnings = []

    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([
            sys.executable,
            str(repo / "product/scripts/prepare_vesselflow_real_data_intake.py"),
            "--repo",
            str(repo),
            "--check",
        ])
        if code != 0:
            errors.append("prepare_vesselflow_real_data_intake --check failed: " + out)

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
