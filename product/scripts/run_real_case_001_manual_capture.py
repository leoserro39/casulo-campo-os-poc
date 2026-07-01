#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
CASE_DIR = ROOT / "product/evaluation/real_tests/real_case_001"
CAPTURED = CASE_DIR / "real_case_001_model_output_CAPTURED_v0_3.md"
REPORT = ROOT / "product/reports/casulo_delta_zero_real_case_001_manual_capture_report_v0_3.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-output-file", required=True)
    ap.add_argument("--operator", default="manual_operator")
    args = ap.parse_args()

    src = Path(args.input_output_file)
    if not src.exists():
        raise SystemExit(f"missing input output file: {src}")

    text = src.read_text(encoding="utf-8")
    CASE_DIR.mkdir(parents=True, exist_ok=True)
    CAPTURED.write_text(text.rstrip() + "\n", encoding="utf-8")

    payload = {
        "version": "casulo_delta_zero_real_case_001_manual_capture_report.v0.3",
        "generated_at": now(),
        "real_case_id": "REAL-CASE-001",
        "operator": args.operator,
        "source_file": str(src),
        "captured_output": str(CAPTURED.relative_to(ROOT)),
        "live_gpt_call_executed_by_script": False,
        "ready_for_scoring_review": True,
        "next_phase": "PROD-7021..7060 - Controlled Real Test Run and Output Capture Review"
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
