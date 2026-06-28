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
        "product/scripts/build_internal_review_freeze_rc.py",
        "product/contracts/internal_review_freeze.contract.json",
        "product/contracts/release_candidate.contract.json",
        "product/schemas/release_candidate.schema.json",
        "outputs/prod041_045_vesselflow_human_review_package.json",
        "outputs/prod041_045_vesselflow_decision_gate.json",
    ]

    errors = []
    warnings = []

    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_internal_review_freeze_rc.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_internal_review_freeze_rc failed: " + out)

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
