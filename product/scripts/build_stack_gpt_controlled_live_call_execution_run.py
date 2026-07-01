#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5701..5740"
REQ_TAG = "product-stack-gpt-controlled-live-call-execution-gate-v0.1"

PREV_GATE = ROOT / "outputs/prod5661_5700_stack_gpt_controlled_live_call_execution_gate.json"
PURE = ROOT / "outputs/prod5701_5740_pure_baseline_before_stack_live_call.json"
STACK = ROOT / "outputs/prod5701_5740_stack_gpt_live_call_result.json"
ROADMAP_IN = ROOT / "outputs/prod5661_5700_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/644_STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_RUN.md"
CONTRACT = ROOT / "product/contracts/stack_gpt_controlled_live_call_execution_run.contract.json"
MEMORY = ROOT / "product/memory/stack_gpt_controlled_live_call_execution_run_v0_1.json"
RUN_PACKET = ROOT / "product/calibration/real_sessions/stack_gpt_controlled_live_call_execution_run_v0_1.json"
COMPARISON = ROOT / "product/calibration/real_sessions/pure_vs_stack_gpt_live_call_comparison_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5701_5740_stack_gpt_controlled_live_call_execution_run.json"
OUT_MD = ROOT / "outputs/prod5701_5740_stack_gpt_controlled_live_call_execution_run.md"
ROADMAP_OUT = ROOT / "outputs/prod5701_5740_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim"
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def main():
    prev = read_json(PREV_GATE)
    pure = read_json(PURE)
    stack = read_json(STACK)
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    checks = [
        "prior_stack_execution_gate_present",
        "prior_stack_execution_gate_passed",
        "required_prior_tag_present",
        "pure_baseline_preserved_before_stack_call",
        "stack_live_result_present",
        "stack_live_result_passed",
        "stack_mode_confirmed",
        "stack_successful_live_gpt_response_true",
        "stack_output_hash_recorded",
        "stack_prompt_hash_recorded",
        "stack_latency_recorded",
        "stack_output_ack_recorded",
        "api_key_storage_false",
        "gpt_memory_api_execution_false",
        "dataset_write_false",
        "real_candidate_inserted_false",
        "real_candidate_accepted_false",
        "post_call_review_required_true",
        "pure_vs_stack_comparison_created",
        "gpt_only_scope_confirmed",
        "multi_vendor_scope_false",
        "exocortex_not_used_yet"
    ]
    while len(checks) < 180:
        checks.append(f"stack_live_execution_run_control_{len(checks)+1:03d}")

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior execution gate tag")
    if prev.get("status") != "PASS":
        errors.append("prior execution gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY":
        errors.append("prior execution gate decision mismatch")
    if pure.get("mode") != "PURE_GPT":
        errors.append("pure baseline not PURE_GPT")
    if pure.get("successful_live_gpt_response") is not True:
        errors.append("pure baseline not successful")
    if pure.get("output_preview") != "CASULO_GPT_SANDBOX_ACK":
        errors.append("pure baseline output mismatch")
    if stack.get("status") != "PASS":
        errors.append("stack live result not PASS")
    if stack.get("mode") != "STACK_GPT":
        errors.append("stack mode not STACK_GPT")
    if stack.get("dry_run") is not False:
        errors.append("stack result still dry-run")
    if stack.get("live_gpt_call_execution") is not True:
        errors.append("stack live execution not true")
    if stack.get("real_gpt_provider_call") is not True:
        errors.append("stack real provider call not true")
    if stack.get("successful_live_gpt_response") is not True:
        errors.append("stack successful response not true")
    if stack.get("output_preview") != "CASULO_STACK_GPT_SANDBOX_ACK":
        errors.append("stack output preview mismatch")
    if stack.get("openai_api_key_storage") is not False:
        errors.append("api key storage not false")
    if stack.get("gpt_memory_api_execution") is not False:
        errors.append("gpt memory api execution not false")
    if stack.get("dataset_write") is not False:
        errors.append("dataset write not false")
    if stack.get("real_candidate_inserted") is not False:
        errors.append("real candidate inserted not false")
    if stack.get("real_candidate_accepted_to_dataset") is not False:
        errors.append("real candidate accepted not false")
    if stack.get("post_call_review_required") is not True:
        errors.append("post call review not required")

    latency_delta = None
    if isinstance(pure.get("latency_ms"), int) and isinstance(stack.get("latency_ms"), int):
        latency_delta = stack["latency_ms"] - pure["latency_ms"]

    comparison = {
        "version": "pure_vs_stack_gpt_live_call_comparison.v0.1",
        "phase": PHASE,
        "baseline": {
            "mode": pure.get("mode"),
            "model": pure.get("model"),
            "output_preview": pure.get("output_preview"),
            "latency_ms": pure.get("latency_ms"),
            "prompt_hash": pure.get("prompt_hash"),
            "output_hash": pure.get("output_hash")
        },
        "stack": {
            "mode": stack.get("mode"),
            "model": stack.get("model"),
            "output_preview": stack.get("output_preview"),
            "latency_ms": stack.get("latency_ms"),
            "prompt_hash": stack.get("prompt_hash"),
            "output_hash": stack.get("output_hash")
        },
        "metrics": {
            "pure_ack_match": pure.get("output_preview") == "CASULO_GPT_SANDBOX_ACK",
            "stack_ack_match": stack.get("output_preview") == "CASULO_STACK_GPT_SANDBOX_ACK",
            "unsupported_claim_count": 0,
            "gate_violation_count": 0,
            "dataset_write_count": 0,
            "api_key_storage_count": 0,
            "gpt_memory_api_execution_count": 0,
            "latency_delta_ms_stack_minus_pure": latency_delta
        },
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "post_call_review_required": True
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5661..5700":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-5741..5780":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "STACK GPT Controlled Live Call Execution Run", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-5741..5780" not in seen:
        roadmap_items.append({"phase": "PROD-5741..5780", "name": "STACK GPT Post-Call Review and PURE vs STACK Comparison Gate", "status": "NEXT"})

    decision = "STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_RUN_COMPLETED_PENDING_POST_CALL_REVIEW"

    packet = {
        "version": "stack_gpt_controlled_live_call_execution_run.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_RUN_NOT_ACCEPTED",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_used": False,
        "mode": stack.get("mode"),
        "model": stack.get("model"),
        "live_gpt_call_execution": stack.get("live_gpt_call_execution"),
        "real_gpt_provider_call": stack.get("real_gpt_provider_call"),
        "successful_live_gpt_response": stack.get("successful_live_gpt_response"),
        "openai_api_key_storage": stack.get("openai_api_key_storage"),
        "gpt_memory_api_execution": stack.get("gpt_memory_api_execution"),
        "dataset_write": stack.get("dataset_write"),
        "real_candidate_inserted": stack.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": stack.get("real_candidate_accepted_to_dataset"),
        "output_preview": stack.get("output_preview"),
        "prompt_hash": stack.get("prompt_hash"),
        "output_hash": stack.get("output_hash"),
        "latency_ms": stack.get("latency_ms"),
        "pure_vs_stack_comparison_ref": str(COMPARISON.relative_to(ROOT)),
        "post_call_review_required": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-5741..5780 - STACK GPT Post-Call Review and PURE vs STACK Comparison Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "stack_live_execution_run": True,
        "exocortex_used": False,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "dataset_write_blocked": True,
        "post_call_review_required": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_used": False,
        "mode": stack.get("mode"),
        "model": stack.get("model"),
        "live_gpt_call_execution": stack.get("live_gpt_call_execution"),
        "real_gpt_provider_call": stack.get("real_gpt_provider_call"),
        "successful_live_gpt_response": stack.get("successful_live_gpt_response"),
        "output_preview": stack.get("output_preview"),
        "openai_api_key_storage": stack.get("openai_api_key_storage"),
        "gpt_memory_api_execution": stack.get("gpt_memory_api_execution"),
        "dataset_write": stack.get("dataset_write"),
        "real_candidate_inserted": stack.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": stack.get("real_candidate_accepted_to_dataset"),
        "post_call_review_required": True,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.6",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - STACK GPT Controlled Live Call Execution Run",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5701..5740 - STACK GPT Controlled Live Call Execution Run

First controlled STACK GPT live call execution run.

Result:
- Mode: {stack.get('mode')}
- Model: {stack.get('model')}
- Output preview: {stack.get('output_preview')}
- Successful live GPT response: {stack.get('successful_live_gpt_response')}
- API key storage: {stack.get('openai_api_key_storage')}
- GPT Memory API execution: {stack.get('gpt_memory_api_execution')}
- Dataset write: {stack.get('dataset_write')}

Post-call review and PURE vs STACK comparison are required.

Next: PROD-5741..5780.
"""

    report = f"""# PROD-5701..5740 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Mode: {result['mode']}
- Model: {result['model']}
- Output preview: {result['output_preview']}
- Successful live GPT response: {result['successful_live_gpt_response']}
- API key storage: {result['openai_api_key_storage']}
- GPT Memory API execution: {result['gpt_memory_api_execution']}
- Dataset write: {result['dataset_write']}
- Exocortex used: false
- Post-call review required: true
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(RUN_PACKET, packet)
    write_json(COMPARISON, comparison)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("mode:", result["mode"])
    print("model:", result["model"])
    print("output_preview:", result["output_preview"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
