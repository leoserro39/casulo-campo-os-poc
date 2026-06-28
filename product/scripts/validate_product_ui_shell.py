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
        "product/ui/index.html",
        "product/ui/app.js",
        "product/ui/styles.css",
        "product/api/product_runtime_api.py",
        "product/scripts/build_product_ui_shell_state.py",
        "product/contracts/product_ui_shell.contract.json",
        "product/contracts/cube_workspace_ui.contract.json",
        "product/schemas/product_ui_state.schema.json",
    ]
    errors = []
    warnings = []

    for rel in required:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_product_ui_shell_state.py")])
        if code != 0:
            errors.append("build_product_ui_shell_state failed: " + out)

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
