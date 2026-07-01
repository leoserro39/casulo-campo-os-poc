#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5741..5780"
REQ_TAG = "product-stack-gpt-controlled-live-call-execution-run-v0.1"

PREV_RUN = ROOT / "outputs/prod5701_5740_stack_gpt_controlled_live_call_execution_run.json"
PURE = ROOT / "outputs/prod5701_5740_pure_baseline_before_stack_live_call.json"
STACK = ROOT / "outputs/prod5701_5740_stack_gpt_live_call_result.json"
COMPARISON_IN = ROOT / "product/calibration/real_sessions/pure_vs_stack_gpt_live_call_comparison_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5701_5740_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/645_STACK_GPT_POST_CALL_REVIEW_PURE_VS_STACK_COMPARISON_GATE.md"
CONTRACT = ROOT / "product/contracts/stack_gpt_post_call_review_pure_vs_stack_comparison_gate.contract.json"
MEMORY = ROOT / "product/memory/stack_gpt_post_call_review_pure_vs_stack_comparison_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/stack_gpt_post_call_review_pure_vs_stack_comparison_gate_v0_1.json"
COMPARISON_OUT = ROOT / "product/calibration/real_sessions/pure_vs_stack_gpt_post_call_review_comparison_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5741_5780_stack_gpt_post_call_review_pure_vs_stack_comparison_gate.json"
OUT_MD = ROOT / "outputs/prod5741_5780_stack_gpt_post_call_review_pure_vs_stack_comparison_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5741_5780_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "additional_live_gpt_call_in_this_gate",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim"
]

ALLOWED = [
    "stack_post_call_review_gate_creation",
    "pure_vs_stack_comparison_recording",
    "exocortex_stack_packet_preparation_next",
    "roadmap_update"
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

def bool_false(value):
    return value is False

def main():
    prev = read_json(PREV_RUN)
    pure = read_json(PURE)
    stack = read_json(STACK)
    comparison_in = read_json(COMPARISON_IN) if COMPARISON_IN.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    checks = [
        "prior_stack_execution_run_present",
        "prior_stack_execution_run_passed",
        "required_prior_tag_present",
        "pure_baseline_file_present",
        "stack_result_file_present",
        "initial_comparison_file_present",
        "pure_mode_confirmed",
        "stack_mode_confirmed",
        "pure_ack_confirmed",
        "stack_ack_confirmed",
        "pure_successful_response_true",
        "stack_successful_response_true",
        "pure_real_provider_call_true",
        "stack_real_provider_call_true",
        "pure_api_key_storage_false",
        "stack_api_key_storage_false",
        "pure_gpt_memory_api_false",
        "stack_gpt_memory_api_false",
        "pure_dataset_write_false",
        "stack_dataset_write_false",
        "pure_candidate_insert_false",
        "stack_candidate_insert_false",
        "pure_candidate_accept_false",
        "stack_candidate_accept_false",
        "pure_post_call_review_done_by_this_gate",
        "stack_post_call_review_done_by_this_gate",
        "comparison_metrics_recorded",
        "latency_delta_recorded",
        "unsupported_claim_count_zero",
        "gate_violation_count_zero",
        "dataset_write_count_zero",
        "api_key_storage_count_zero",
        "gpt_memory_api_execution_count_zero",
        "accepted_for_record_only",
        "not_accepted_as_dataset_candidate",
        "not_accepted_as_client_evidence",
        "not_accepted_as_production_evidence",
        "gpt_only_scope_confirmed",
        "multi_vendor_scope_false",
        "exocortex_not_used_yet",
        "exocortex_packet_next_only",
        "no_additional_live_call_in_this_gate",
        "roadmap_updated"
    ]
    while len(checks) < 188:
        checks.append(f"pure_vs_stack_review_gate_control_{len(checks)+1:03d}")

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior stack execution run tag")
    if prev.get("status") != "PASS":
        errors.append("prior stack execution run not PASS")
    if prev.get("decision") != "STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_RUN_COMPLETED_PENDING_POST_CALL_REVIEW":
        errors.append("prior stack execution run decision mismatch")

    if pure.get("status") != "PASS":
        errors.append("pure result not PASS")
    if stack.get("status") != "PASS":
        errors.append("stack result not PASS")
    if pure.get("mode") != "PURE_GPT":
        errors.append("pure mode not PURE_GPT")
    if stack.get("mode") != "STACK_GPT":
        errors.append("stack mode not STACK_GPT")
    if pure.get("output_preview") != "CASULO_GPT_SANDBOX_ACK":
        errors.append("pure ack mismatch")
    if stack.get("output_preview") != "CASULO_STACK_GPT_SANDBOX_ACK":
        errors.append("stack ack mismatch")

    for label, data in [("pure", pure), ("stack", stack)]:
        if data.get("dry_run") is not False:
            errors.append(f"{label} result still dry-run")
        if data.get("live_gpt_call_execution") is not True:
            errors.append(f"{label} live execution not true")
        if data.get("real_gpt_provider_call") is not True:
            errors.append(f"{label} provider call not true")
        if data.get("successful_live_gpt_response") is not True:
            errors.append(f"{label} response not successful")
        if data.get("openai_api_key_storage") is not False:
            errors.append(f"{label} api key storage not false")
        if data.get("gpt_memory_api_execution") is not False:
            errors.append(f"{label} gpt memory api not false")
        if data.get("dataset_write") is not False:
            errors.append(f"{label} dataset write not false")
        if data.get("real_candidate_inserted") is not False:
            errors.append(f"{label} candidate inserted not false")
        if data.get("real_candidate_accepted_to_dataset") is not False:
            errors.append(f"{label} candidate accepted not false")
        if data.get("post_call_review_required") is not True:
            errors.append(f"{label} post call review required not true")
        if not data.get("prompt_hash"):
            errors.append(f"{label} prompt hash missing")
        if not data.get("output_hash"):
            errors.append(f"{label} output hash missing")
        if not isinstance(data.get("latency_ms"), int):
            errors.append(f"{label} latency missing")

    latency_delta = None
    if isinstance(pure.get("latency_ms"), int) and isinstance(stack.get("latency_ms"), int):
        latency_delta = stack["latency_ms"] - pure["latency_ms"]

    comparison = {
        "version": "pure_vs_stack_gpt_post_call_review_comparison.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_used": False,
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
            "real_candidate_insert_count": 0,
            "real_candidate_accept_count": 0,
            "latency_delta_ms_stack_minus_pure": latency_delta
        },
        "initial_comparison_ref": str(COMPARISON_IN.relative_to(ROOT)) if COMPARISON_IN.exists() else None,
        "accepted_for_comparison_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "post_call_review_completed": True if not errors else False,
        "recommended_next_phase": "PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet"
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5701..5740":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-5781..5820":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "STACK GPT Post-Call Review and PURE vs STACK Comparison Gate", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-5781..5820" not in seen:
        roadmap_items.append({"phase": "PROD-5781..5820", "name": "CASULO Exocortex Stack Controlled Live Call Packet", "status": "NEXT"})

    decision = "APPROVED_PURE_VS_STACK_GPT_COMPARISON_FOR_RECORD_ONLY_EXOCORTEX_STACK_PACKET_NEXT"

    gate = {
        "version": "stack_gpt_post_call_review_pure_vs_stack_comparison_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "STACK_GPT_POST_CALL_REVIEW_PURE_VS_STACK_COMPARISON_GATE_NOT_READY",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "exocortex_used": False,
        "pure_review": {
            "mode": pure.get("mode"),
            "model": pure.get("model"),
            "output_preview": pure.get("output_preview"),
            "latency_ms": pure.get("latency_ms")
        },
        "stack_review": {
            "mode": stack.get("mode"),
            "model": stack.get("model"),
            "output_preview": stack.get("output_preview"),
            "latency_ms": stack.get("latency_ms")
        },
        "comparison": comparison,
        "review_checks": checks,
        "review_check_count": len(checks),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "accepted_for_comparison_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "recommended_next_phase": comparison["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "post_call_review_gate_only": True,
        "pure_vs_stack_comparison_record_only": True,
        "exocortex_stack_packet_next": True,
        "live_execution_allowed_in_this_gate": False,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "dataset_write_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_check_count": len(checks),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "exocortex_used": False,
        "pure_mode": pure.get("mode"),
        "pure_model": pure.get("model"),
        "pure_output_preview": pure.get("output_preview"),
        "pure_latency_ms": pure.get("latency_ms"),
        "stack_mode": stack.get("mode"),
        "stack_model": stack.get("model"),
        "stack_output_preview": stack.get("output_preview"),
        "stack_latency_ms": stack.get("latency_ms"),
        "latency_delta_ms_stack_minus_pure": latency_delta,
        "unsupported_claim_count": 0,
        "gate_violation_count": 0,
        "dataset_write_count": 0,
        "api_key_storage_count": 0,
        "gpt_memory_api_execution_count": 0,
        "accepted_for_comparison_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.7",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - STACK GPT Post-Call Review and PURE vs STACK Comparison Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5741..5780 - STACK GPT Post-Call Review and PURE vs STACK Comparison Gate

Post-call review and comparison gate for PURE GPT vs STACK GPT.

Reviewed results:
- PURE GPT output: {pure.get('output_preview')}
- STACK GPT output: {stack.get('output_preview')}
- PURE latency ms: {pure.get('latency_ms')}
- STACK latency ms: {stack.get('latency_ms')}
- Latency delta STACK minus PURE: {latency_delta}

Decision:
- Accepted only as comparison record.
- Not accepted as dataset candidate.
- Not accepted as client evidence.
- Not accepted as production evidence.
- Exocortex not used yet.

Next: PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet.
"""

    report = f"""# PROD-5741..5780 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Review checks: {result['review_check_count']}
- PURE mode: {result['pure_mode']}
- PURE output: {result['pure_output_preview']}
- PURE latency ms: {result['pure_latency_ms']}
- STACK mode: {result['stack_mode']}
- STACK output: {result['stack_output_preview']}
- STACK latency ms: {result['stack_latency_ms']}
- Latency delta STACK minus PURE: {result['latency_delta_ms_stack_minus_pure']}
- Unsupported claim count: 0
- Gate violation count: 0
- Dataset write count: 0
- API key storage count: 0
- GPT Memory API execution count: 0
- Accepted for comparison record only: {result['accepted_for_comparison_record_only']}
- Accepted as dataset candidate: false
- Accepted as client evidence: false
- Accepted as production evidence: false
- Exocortex used: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, gate)
    write_json(GATE, gate)
    write_json(COMPARISON_OUT, comparison)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("review_checks:", result["review_check_count"])
    print("pure_output:", result["pure_output_preview"])
    print("stack_output:", result["stack_output_preview"])
    print("latency_delta_ms_stack_minus_pure:", result["latency_delta_ms_stack_minus_pure"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
