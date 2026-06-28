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

    errors = []
    warnings = []
    required = [
        "product/api/product_runtime_api.py",
        "product/api/services/product_runtime_service.py",
        "product/scripts/snapshot_product_runtime_api.py",
        "product/contracts/product_runtime_api.contract.json",
        "product/contracts/case_adapter.contract.json",
        "product/contracts/local_demo_runtime.contract.json",
        "product/schemas/product_runtime_status.schema.json",
    ]
    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/snapshot_product_runtime_api.py"), "--repo", str(repo), "--output-dir", str(repo / "outputs")])
        if code != 0:
            errors.append("snapshot_product_runtime_api failed: " + out)

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
