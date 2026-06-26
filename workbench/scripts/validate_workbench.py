#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "api/main.py",
    "api/models/canonical_models.py",
    "api/services/casulo_workbench_engine.py",
    "scripts/run_demo.py",
    "scripts/export_codex_task.py",
    "graph/graph_model.md",
    "graph/schema.cypher",
    "examples/advocacia_demo/case.json",
    "examples/servico_local_demo/case.json",
    "examples/contabilidade_demo/case.json",
    "web/src/App.jsx",
]


def main() -> int:
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")

    for case_path in sorted((ROOT / "examples").glob("*/case.json")):
        try:
            data = json.loads(case_path.read_text(encoding="utf-8"))
            for key in ["case_id", "title", "sources", "domains", "deltas"]:
                if key not in data:
                    errors.append(f"{case_path}: missing key {key}")
        except Exception as exc:
            errors.append(f"{case_path}: invalid json: {exc}")

    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({"status": "PASS", "checks": len(REQUIRED), "cases": 3}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
