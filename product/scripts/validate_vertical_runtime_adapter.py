#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> tuple[int, str]:
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
        "product/scripts/build_vertical_state_request.py",
        "product/scripts/inspect_vertical_pack.py",
        "product/scripts/prepare_vesselflow_import_manifest.py",
        "product/contracts/vertical_runtime_adapter.contract.json",
        "product/contracts/vesselflow_import_protocol.contract.json",
        "product/contracts/vertical_state_request.contract.json",
        "product/schemas/vertical_state_request.schema.json",
    ]
    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        for vertical in ["small_service", "legal_office", "vesselflow"]:
            code, out = run([sys.executable, str(repo / "product/scripts/build_vertical_state_request.py"), "--vertical", vertical, "--repo", str(repo), "--output-dir", str(repo / "outputs")])
            if code != 0:
                errors.append(f"build_vertical_state_request failed for {vertical}: {out}")
        code, out = run([sys.executable, str(repo / "product/scripts/prepare_vesselflow_import_manifest.py"), "--output-dir", str(repo / "outputs")])
        if code != 0:
            errors.append(f"prepare_vesselflow_import_manifest failed: {out}")

    result = {
        "status": "FAIL" if errors else "PASS",
        "checks": len(required) + 4,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
