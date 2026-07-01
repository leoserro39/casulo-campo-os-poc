#!/usr/bin/env python3
"""
CASULO GPT sandbox first controlled live call runner.

This runner is live-ready but blocked by default.

It requires all of the following for a future controlled live call:
- --apply
- CASULO_GPT_LIVE_AUTH=YES
- OPENAI_API_KEY available in environment
- explicit mode: PURE_GPT, STACK_GPT, or CASULO_EXOCORTEX_STACK

This runner does NOT:
- store API keys
- print secrets
- call GPT Memory API
- write to dataset
- insert real candidates
- activate production
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
LIVE_LOG = OUT_DIR / "gpt_sandbox_first_controlled_live_call_result.json"

ALLOWED_MODES = {"PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"}

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=sorted(ALLOWED_MODES))
    parser.add_argument("--prompt", default="CASULO controlled sandbox test. Return a concise acknowledgement.")
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if not args.apply:
        result = {
            "status": "PASS",
            "mode": args.mode,
            "dry_run": True,
            "live_gpt_call_execution": False,
            "real_gpt_provider_call": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "reason": "Dry-run only. Use --apply only after explicit future gate.",
            "prompt_hash": sha256_text(args.prompt),
            "next_required_phase": "PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate"
        }
        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if os.environ.get("CASULO_GPT_LIVE_AUTH") != "YES":
        raise SystemExit("BLOCKED: CASULO_GPT_LIVE_AUTH=YES is required by future execution gate.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("BLOCKED: OPENAI_API_KEY must be present in environment for future live call. It will not be stored.")

    payload_template = read_json(PAYLOAD_TEMPLATE)
    started = time.time()

    try:
        from openai import OpenAI
    except Exception as exc:
        raise SystemExit("BLOCKED: openai package is not available or import failed: " + str(exc))

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    messages = [
        {"role": "system", "content": "You are running a CASULO controlled sandbox test. Do not make external claims. Do not store memory."},
        {"role": "user", "content": args.prompt},
    ]

    response = client.responses.create(
        model=model,
        input=messages,
        max_output_tokens=160,
    )

    elapsed_ms = int((time.time() - started) * 1000)
    output_text = getattr(response, "output_text", "")

    result = {
        "status": "PASS",
        "mode": args.mode,
        "dry_run": False,
        "live_gpt_call_execution": True,
        "real_gpt_provider_call": True,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "provider": "openai_gpt",
        "model": model,
        "prompt_hash": sha256_text(args.prompt),
        "output_hash": sha256_text(output_text),
        "output_preview": output_text[:500],
        "latency_ms": elapsed_ms,
        "dataset_write": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "payload_template_version": payload_template.get("version"),
        "post_call_review_required": True,
    }

    write_json(LIVE_LOG, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
