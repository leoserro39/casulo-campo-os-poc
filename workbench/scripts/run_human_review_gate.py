#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.human_review_gate import run_human_review_gate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CASULO human review gate for controlled diagnostics.")
    parser.add_argument("--intake", default=str(ROOT / "real_cases" / "template" / "real_intake.json"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Validate without writing. Default.")
    mode.add_argument("--write", action="store_true", help="Write review packet explicitly.")
    parser.add_argument("--output-root", default=str(ROOT / "runtime_outputs" / "human_review"))
    parser.add_argument("--stable-time", action="store_true", default=True)
    args = parser.parse_args()

    result = run_human_review_gate(
        intake_path=Path(args.intake),
        write=bool(args.write),
        output_root=Path(args.output_root),
        stable_time=args.stable_time,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result.get("status") != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
