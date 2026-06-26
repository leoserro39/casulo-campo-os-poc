#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.casulo_workbench_engine import export_codex_task, list_case_names  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Codex executor tasks from CASULO gates.")
    parser.add_argument("--case", default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Validate export plan without writing. Default.")
    mode.add_argument("--write", action="store_true", help="Write Codex task files explicitly.")
    parser.add_argument("--output-dir", default=str(ROOT / "runtime_outputs" / "codex_tasks"))
    parser.add_argument("--stable-time", action="store_true")
    args = parser.parse_args()

    cases = list_case_names() if args.case == "all" else [args.case]
    output_dir = Path(args.output_dir)

    results = []
    if args.write:
        for case_name in cases:
            dst = export_codex_task(case_name, output_dir=output_dir, stable_time=args.stable_time)
            results.append({"case_name": case_name, "written": str(dst)})
    else:
        for case_name in cases:
            results.append({"case_name": case_name, "planned": str(output_dir / f"{case_name}_codex_task.md")})

    print(json.dumps({"status": "PASS", "mode": "write" if args.write else "check", "results": results}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
