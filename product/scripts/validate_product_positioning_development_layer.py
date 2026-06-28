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
        "product/scripts/build_product_positioning_development_layer.py",
        "product/contracts/product_positioning.contract.json",
        "product/contracts/development_layer.contract.json",
        "product/contracts/tic_state_mesh.contract.json",
        "product/contracts/software_review_gate.contract.json",
        "product/schemas/product_positioning.schema.json",
        "outputs/prod046_050_release_candidate.json",
    ]

    errors = []
    warnings = []

    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_product_positioning_development_layer.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_product_positioning_development_layer failed: " + out)

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
