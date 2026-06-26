#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.casulo_workbench_engine import run_all_cases, run_case  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CASULO Workbench demo cases.")
    parser.add_argument("--case", default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Compute without writing outputs. Default.")
    mode.add_argument("--write", action="store_true", help="Write outputs explicitly.")
    parser.add_argument("--output-root", default=str(ROOT / "runtime_outputs"))
    parser.add_argument("--stable-time", action="store_true", help="Use stable timestamp for reproducible fixture writes.")
    args = parser.parse_args()

    write = bool(args.write)
    output_root = Path(args.output_root)

    if args.case == "all":
        result = run_all_cases(write=write, output_root=output_root, stable_time=args.stable_time)
    else:
        result = [run_case(args.case, write=write, output_root=output_root, stable_time=args.stable_time)]

    print(json.dumps({"status": "PASS", "mode": "write" if write else "check", "results": result}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
