#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.poc_finish_bundle import build_poc_completion


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT.parent / "outputs"))
    args = parser.parse_args()
    result = build_poc_completion(output_dir=Path(args.output_dir))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result.get("status") != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
