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
        "product/scripts/build_vesselflow_real_data_delta_review.py",
        "product/contracts/real_data_delta_review.contract.json",
        "product/contracts/ui_delta_review_panel.contract.json",
        "product/schemas/real_data_delta_review.schema.json",
        "outputs/prod016_020_vesselflow_state_definition.json",
        "outputs/prod026_030_vesselflow_real_data_intake_preview.json",
    ]
    errors = []
    warnings = []
    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_vesselflow_real_data_delta_review.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_vesselflow_real_data_delta_review failed: " + out)

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
