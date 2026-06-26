#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.casulo_workbench_engine import run_all_cases, run_case  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="all")
    args = parser.parse_args()

    results = run_all_cases() if args.case == "all" else [run_case(args.case)]
    out_dir = ROOT / "outputs" / "codex_tasks"
    out_dir.mkdir(parents=True, exist_ok=True)

    for item in results:
        src = Path(item["outputs"]) / "codex_task.md"
        dst = out_dir / f"{item['case_name']}_codex_task.md"
        shutil.copyfile(src, dst)
        print(f"created: {dst}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
