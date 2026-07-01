#!/usr/bin/env python3
"""
CASULO GPT sandbox first controlled call runner.

Default behavior is dry-run only.

This runner intentionally does NOT:
- import OpenAI SDK
- read environment API keys
- store API keys
- call GPT provider
- call GPT Memory API
- execute any live benchmark
- insert real candidate
- accept dataset

A future live execution requires a separate readiness gate and a different runner activation packet.
"""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
OUT = ROOT / "outputs/gpt_sandbox_first_controlled_call_runner_dry_run_output.json"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if args.apply:
        raise SystemExit("BLOCKED: live GPT call execution is not allowed by this runner packet.")

    payload_template = read_json(PAYLOAD_TEMPLATE)
    expected_log_template = read_json(EXPECTED_LOG_TEMPLATE)

    result = {
        "status": "PASS",
        "mode": "DRY_RUN_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "live_gpt_call_execution": False,
        "request_modes": payload_template.get("request_modes", []),
        "expected_log_fields": expected_log_template.get("log_fields", []),
        "blocked_reason": "Live GPT call requires a future explicit readiness gate.",
        "next_required_phase": "PROD-5341..5380 - GPT Sandbox First Controlled Call Runner Readiness Gate"
    }

    write_json(OUT, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
