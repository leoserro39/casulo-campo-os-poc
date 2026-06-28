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
        "product/scripts/build_vesselflow_human_review_package.py",
        "product/contracts/human_review_package.contract.json",
        "product/contracts/decision_gate.contract.json",
        "product/schemas/human_review_package.schema.json",
        "outputs/prod036_040_vesselflow_data_backed_rerun.json",
        "outputs/prod036_040_vesselflow_evidence_comparator.json",
    ]

    errors = []
    warnings = []
    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_vesselflow_human_review_package.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_vesselflow_human_review_package failed: " + out)

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
