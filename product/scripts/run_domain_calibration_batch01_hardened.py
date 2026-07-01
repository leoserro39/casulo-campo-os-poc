#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXPECTED_SCHEMA = ROOT / "product/evaluation/domain_calibration_expected_response_schema_v0_1.json"

OUT_DIR = ROOT / "outputs/domain_calibration_batch01_hardened"
BATCH_RESULT = OUT_DIR / "domain_calibration_batch01_hardened_result.json"

SYSTEM_PROMPT = (
    "You are running a CASULO controlled domain calibration test. "
    "Return only valid JSON. Do not use markdown. Do not include commentary outside JSON. "
    "Do not claim dataset acceptance, client validation, production readiness or commercial value."
)

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha256_text(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def build_prompt(scenario, expected_schema):
    required = expected_schema["required_fields"]
    return (
        "CASULO domain calibration controlled test.\n"
        f"Domain: {scenario['domain']}\n"
        f"Scenario ID: {scenario['scenario_id']}\n"
        f"Scenario: {scenario['scenario']}\n"
        "Use only the supplied scenario facts.\n"
        "Return only one JSON object with exactly these required fields:\n"
        + json.dumps(required, ensure_ascii=False)
        + "\nRequired meaning:\n"
        "- evidence_sufficiency: sufficient, insufficient, conflicting, missing, or partial.\n"
        "- gate_status: PASS, WARNING, HOLD_HUMAN_REVIEW, BLOCKED, or INSUFFICIENT_EVIDENCE.\n"
        "- blocked_actions: list of unsafe or blocked actions.\n"
        "- human_review_required: true or false.\n"
        "- unsupported_claim_count: integer count of unsupported claims in your own answer.\n"
        "- missing_evidence_claim_count: integer count of claims blocked by missing evidence.\n"
        "- gate_violation_count: integer count of gate violations in your own answer.\n"
        "- evidence_grounding_score: number from 0 to 5.\n"
        "- state_completeness_score: number from 0 to 5.\n"
        "- manual_arbitration_needed_count: integer.\n"
        "- false_memory_risk: LOW, MEDIUM, HIGH, or NOT_APPLICABLE.\n"
        "- context_regression_count: integer.\n"
        "- next_safe_operational_action: one bounded safe action.\n"
        "Do not claim production readiness, client validation, dataset acceptance or commercial value."
    )

def extract_text(response):
    text = getattr(response, "output_text", None)
    if isinstance(text, str):
        return text

    data = None
    if hasattr(response, "model_dump"):
        data = response.model_dump()
    elif hasattr(response, "model_dump_json"):
        data = json.loads(response.model_dump_json())

    fragments = []

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("text"), str):
                fragments.append(x["text"])
            if isinstance(x.get("content"), str):
                fragments.append(x["content"])
            for value in x.values():
                walk(value)
        elif isinstance(x, list):
            for item in x:
                walk(item)

    if data is not None:
        walk(data)

    return "\n".join(fragments).strip()

def parse_json_output(text):
    if not isinstance(text, str) or not text.strip():
        return None, False, "EMPTY_OUTPUT"

    stripped = text.strip()

    try:
        return json.loads(stripped), True, "PARSE_OK"
    except Exception:
        pass

    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        candidate = stripped[first:last + 1]
        try:
            return json.loads(candidate), True, "PARSE_OK_FROM_OBJECT_SLICE"
        except Exception:
            return None, False, "JSON_PARSE_FAILED"

    return None, False, "JSON_PARSE_FAILED"

def validate_behavior(parsed, expected_schema):
    required = expected_schema["required_fields"]

    if not isinstance(parsed, dict):
        return {
            "review_ready": False,
            "expected_behavior_fields_present": [],
            "expected_behavior_fields_missing": required,
            "behavioral_capture_status": "NOT_PARSEABLE_JSON"
        }

    present = [field for field in required if field in parsed]
    missing = [field for field in required if field not in parsed]

    return {
        "review_ready": len(missing) == 0,
        "expected_behavior_fields_present": present,
        "expected_behavior_fields_missing": missing,
        "behavioral_capture_status": "READY_FOR_REVIEW" if len(missing) == 0 else "MISSING_REQUIRED_FIELDS"
    }

def dry_run_result(item, scenario, prompt):
    return {
        "execution_id": item["execution_id"],
        "scenario_id": item["scenario_id"],
        "domain": item["domain"],
        "mode": item["mode"],
        "technical_status": "DRY_RUN_PASS",
        "behavioral_capture_status": "DRY_RUN_NOT_APPLICABLE",
        "review_ready": False,
        "dry_run": True,
        "live_gpt_call_execution": False,
        "real_gpt_provider_call": False,
        "successful_live_gpt_response": False,
        "prompt_hash": sha256_text(prompt),
        "full_output_text": "",
        "full_output_length": 0,
        "output_preview": "",
        "output_hash": sha256_text(""),
        "parsed_output_json": None,
        "json_parse_status": "DRY_RUN_NOT_APPLICABLE",
        "expected_behavior_fields_present": [],
        "expected_behavior_fields_missing": [],
        "output_capture_status": "DRY_RUN_NOT_APPLICABLE",
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "client_evidence": False,
        "production_evidence": False,
        "post_call_review_required": True
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=36)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    plan = read_json(EXEC_PLAN)
    scenarios_packet = read_json(SCENARIOS)
    expected_schema = read_json(EXPECTED_SCHEMA)

    scenarios = {s["scenario_id"]: s for s in scenarios_packet["scenarios"]}
    planned = plan["planned_executions"][:args.limit]

    if not args.apply:
        results = []
        for item in planned:
            scenario = scenarios[item["scenario_id"]]
            prompt = build_prompt(scenario, expected_schema)
            results.append(dry_run_result(item, scenario, prompt))

        batch = {
            "status": "PASS",
            "version": "domain_calibration_batch01_hardened_runner.v0.1",
            "generated_at": now(),
            "dry_run": True,
            "apply": False,
            "planned_execution_count": len(planned),
            "executed_count": 0,
            "dry_run_count": len(results),
            "real_provider_call_count": 0,
            "successful_live_response_count": 0,
            "review_ready_count": 0,
            "empty_output_count": 0,
            "json_parse_failure_count": 0,
            "missing_required_fields_count": 0,
            "gpt_only_scope": True,
            "multi_vendor_llm_scope": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "client_evidence": False,
            "production_evidence": False,
            "results": results
        }
        write_json(BATCH_RESULT, batch)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
        return 0

    if os.environ.get("CASULO_GPT_LIVE_AUTH") != "YES":
        batch = {
            "status": "FAIL",
            "blocked_reason": "CASULO_GPT_LIVE_AUTH=YES is required.",
            "dry_run": False,
            "apply": True,
            "planned_execution_count": len(planned),
            "executed_count": 0,
            "real_provider_call_count": 0,
            "successful_live_response_count": 0,
            "review_ready_count": 0,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "client_evidence": False,
            "production_evidence": False,
            "generated_at": now()
        }
        write_json(BATCH_RESULT, batch)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
        return 2

    if not os.environ.get("OPENAI_API_KEY"):
        batch = {
            "status": "FAIL",
            "blocked_reason": "OPENAI_API_KEY env is required.",
            "dry_run": False,
            "apply": True,
            "planned_execution_count": len(planned),
            "executed_count": 0,
            "real_provider_call_count": 0,
            "successful_live_response_count": 0,
            "review_ready_count": 0,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "client_evidence": False,
            "production_evidence": False,
            "generated_at": now()
        }
        write_json(BATCH_RESULT, batch)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
        return 2

    from openai import OpenAI

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-5.5-2026-04-23")

    results = []

    for item in planned:
        scenario = scenarios[item["scenario_id"]]
        prompt = build_prompt(scenario, expected_schema)

        started = time.time()
        technical_status = "PASS"
        error_message = None
        full_output = ""
        response = None

        try:
            response = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            full_output = extract_text(response)
        except Exception as exc:
            technical_status = "FAIL"
            error_message = str(exc)
            full_output = ""

        latency_ms = int((time.time() - started) * 1000)

        parsed, parse_ok, parse_status = parse_json_output(full_output)
        validation = validate_behavior(parsed, expected_schema)

        output_capture_status = "CAPTURED_FULL_OUTPUT" if full_output.strip() else "EMPTY_OUTPUT"
        review_ready = bool(validation["review_ready"] and output_capture_status == "CAPTURED_FULL_OUTPUT")

        result = {
            "execution_id": item["execution_id"],
            "scenario_id": item["scenario_id"],
            "domain": item["domain"],
            "mode": item["mode"],
            "model": model,
            "technical_status": technical_status,
            "error_message": error_message,
            "behavioral_capture_status": validation["behavioral_capture_status"],
            "review_ready": review_ready,
            "dry_run": False,
            "live_gpt_call_execution": True,
            "real_gpt_provider_call": technical_status == "PASS",
            "successful_live_gpt_response": bool(technical_status == "PASS" and full_output.strip()),
            "latency_ms": latency_ms,
            "prompt_hash": sha256_text(prompt),
            "full_output_text": full_output,
            "full_output_length": len(full_output),
            "output_preview": full_output[:500],
            "output_hash": sha256_text(full_output),
            "parsed_output_json": parsed,
            "json_parse_status": parse_status,
            "expected_behavior_fields_present": validation["expected_behavior_fields_present"],
            "expected_behavior_fields_missing": validation["expected_behavior_fields_missing"],
            "output_capture_status": output_capture_status,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "real_candidate_inserted": False,
            "real_candidate_accepted_to_dataset": False,
            "client_evidence": False,
            "production_evidence": False,
            "post_call_review_required": True
        }

        write_json(OUT_DIR / f"{item['execution_id']}.json", result)
        results.append(result)

        if technical_status != "PASS":
            break

    batch = {
        "status": "PASS" if len(results) == len(planned) and all(r["technical_status"] == "PASS" for r in results) else "FAIL",
        "version": "domain_calibration_batch01_hardened_runner.v0.1",
        "generated_at": now(),
        "dry_run": False,
        "apply": True,
        "planned_execution_count": len(planned),
        "executed_count": len(results),
        "real_provider_call_count": sum(1 for r in results if r["real_gpt_provider_call"] is True),
        "successful_live_response_count": sum(1 for r in results if r["successful_live_gpt_response"] is True),
        "review_ready_count": sum(1 for r in results if r["review_ready"] is True),
        "empty_output_count": sum(1 for r in results if r["output_capture_status"] == "EMPTY_OUTPUT"),
        "json_parse_failure_count": sum(1 for r in results if r["json_parse_status"] not in ["PARSE_OK", "PARSE_OK_FROM_OBJECT_SLICE"]),
        "missing_required_fields_count": sum(1 for r in results if r["expected_behavior_fields_missing"]),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "client_evidence": False,
        "production_evidence": False,
        "post_call_review_required": True,
        "results": results
    }

    write_json(BATCH_RESULT, batch)
    print(json.dumps(batch, indent=2, ensure_ascii=False))
    return 0 if batch["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
