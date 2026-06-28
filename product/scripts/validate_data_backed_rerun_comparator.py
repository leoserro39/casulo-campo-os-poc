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
        "product/scripts/run_vesselflow_data_backed_rerun.py",
        "product/scripts/build_vesselflow_evidence_comparator.py",
        "product/contracts/data_backed_rerun.contract.json",
        "product/contracts/evidence_comparator.contract.json",
        "product/schemas/data_backed_rerun.schema.json",
        "outputs/prod031_035_vesselflow_real_data_delta_review.json",
    ]

    errors = []
    warnings = []
    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/run_vesselflow_data_backed_rerun.py"), "--repo", str(repo), "--check"])
        if code != 0:
            errors.append("run_vesselflow_data_backed_rerun --check failed: " + out)
        else:
            code2, out2 = run([sys.executable, str(repo / "product/scripts/build_vesselflow_evidence_comparator.py"), "--repo", str(repo)])
            if code2 != 0:
                errors.append("build_vesselflow_evidence_comparator failed: " + out2)

    result = {
        "status": "FAIL" if errors else "PASS",
        "checks": len(required) + 2,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
