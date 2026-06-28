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
        "product/verticals/tic_si/vertical_manifest.json",
        "product/verticals/tic_si/domain_map.json",
        "product/verticals/tic_si/gate_map.json",
        "product/verticals/tic_si/operational_cube_seed.json",
        "product/contracts/tic_si_operational_mesh.contract.json",
        "product/contracts/tic_si_gate_matrix.contract.json",
        "product/schemas/tic_si_state_mesh.schema.json",
        "product/scripts/build_tic_si_operational_mesh.py",
        "outputs/prod051_060_tic_state_mesh.json",
    ]

    errors = []
    warnings = []

    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_tic_si_operational_mesh.py"), "--repo", str(repo)])
        if code != 0:
            errors.append("build_tic_si_operational_mesh failed: " + out)

    result = {"status": "FAIL" if errors else "PASS", "checks": len(required) + 1, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
