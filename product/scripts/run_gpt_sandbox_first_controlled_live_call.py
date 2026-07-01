#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
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
    parser.add_argument("--prompt", default="CASULO controlled sandbox test. Return only: CASULO_GPT_SANDBOX_ACK.")
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if not args.apply:
        result = {
            "status": "PASS",
            "mode": args.mode,
            "dry_run": True,
            "live_gpt_call_execution": False,
            "real_gpt_provider_call": False,
            "successful_live_gpt_response": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "reason": "Dry-run only. Use --apply only after explicit execution gate.",
            "prompt_hash": sha256_text(args.prompt),
            "next_required_phase": "PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate"
        }
        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if os.environ.get("CASULO_GPT_LIVE_AUTH") != "YES":
        result = {
            "status": "FAIL",
            "mode": args.mode,
            "dry_run": False,
            "live_gpt_call_execution": False,
            "real_gpt_provider_call": False,
            "successful_live_gpt_response": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "blocked_reason": "CASULO_GPT_LIVE_AUTH=YES is required.",
            "prompt_hash": sha256_text(args.prompt)
        }
        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        result = {
            "status": "FAIL",
            "mode": args.mode,
            "dry_run": False,
            "live_gpt_call_execution": False,
            "real_gpt_provider_call": False,
            "successful_live_gpt_response": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "blocked_reason": "OPENAI_API_KEY missing in environment. It will not be stored.",
            "prompt_hash": sha256_text(args.prompt)
        }
        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    payload_template = read_json(PAYLOAD_TEMPLATE)
    model = os.environ.get("OPENAI_MODEL", "gpt-5.5-2026-04-23")
    started = time.time()

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": "You are running a CASULO controlled sandbox test. Return only the requested acknowledgement. Do not store memory."
            },
            {
                "role": "user",
                "content": args.prompt
            }
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
            "successful_live_gpt_response": True,
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
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    except Exception as exc:
        elapsed_ms = int((time.time() - started) * 1000)
        result = {
            "status": "FAIL",
            "mode": args.mode,
            "dry_run": False,
            "live_gpt_call_execution": True,
            "real_gpt_provider_call": True,
            "successful_live_gpt_response": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "provider": "openai_gpt",
            "model": model,
            "prompt_hash": sha256_text(args.prompt),
            "provider_error_type": type(exc).__name__,
            "provider_error_message": str(exc)[:1000],
            "latency_ms": elapsed_ms,
            "dataset_write": False,
            "real_candidate_inserted": False,
            "real_candidate_accepted_to_dataset": False,
            "post_call_review_required": True,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
