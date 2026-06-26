#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.cockpit_state_engine import (  # noqa: E402
    DEFAULT_OUTPUT_ROOT,
    build_all_cockpit_states,
    build_cockpit_state,
    validate_cockpit_state,
    write_cockpit_state,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CASULO Cubo/Cupula cockpit_state artifacts.")
    parser.add_argument("--case", default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Compute and validate without writing. Default.")
    mode.add_argument("--write", action="store_true", help="Write cockpit_state artifacts explicitly.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--stable-time", action="store_true", default=True)
    args = parser.parse_args()

    output_root = Path(args.output_root)

    if args.case == "all":
        results = build_all_cockpit_states(write=bool(args.write), output_root=output_root, stable_time=args.stable_time)
    else:
        state = build_cockpit_state(args.case)
        errors = validate_cockpit_state(state)
        item = {
            "case_name": args.case,
            "case_id": state.get("case", {}).get("case_id"),
            "decision": state.get("summary", {}).get("decision"),
            "data_quality": state.get("summary", {}).get("data_quality"),
            "h_pre": state.get("summary", {}).get("h_pre"),
            "domains": state.get("summary", {}).get("domains"),
            "gates": state.get("summary", {}).get("gates"),
            "errors": errors,
        }
        if args.write and not errors:
            item["written"] = str(write_cockpit_state(args.case, output_root=output_root, stable_time=args.stable_time))
        results = [item]

    has_errors = any(item.get("errors") for item in results)
    print(json.dumps({"status": "FAIL" if has_errors else "PASS", "mode": "write" if args.write else "check", "results": results}, indent=2, ensure_ascii=False))
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
