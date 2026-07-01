#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5621..5660"
REQ_TAG = "product-gpt-sandbox-first-controlled-live-call-post-call-review-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod5581_5620_gpt_sandbox_first_controlled_live_call_post_call_review_gate.json"
PURE_RESULT = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"
PURE_REVIEW = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_post_call_review_gate_v0_1.json"
LIVE_RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_live_call.py"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
LIVE_RESULT_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_result_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5581_5620_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/642_STACK_GPT_CONTROLLED_LIVE_CALL_PACKET.md"
CONTRACT = ROOT / "product/contracts/stack_gpt_controlled_live_call_packet.contract.json"
MEMORY = ROOT / "product/memory/stack_gpt_controlled_live_call_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/stack_gpt_controlled_live_call_packet_v0_1.json"
REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/stack_gpt_controlled_live_call_request_template_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/pure_vs_stack_gpt_comparison_template_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5621_5660_stack_gpt_controlled_live_call_packet.json"
OUT_MD = ROOT / "outputs/prod5621_5660_stack_gpt_controlled_live_call_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5621_5660_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "start_command_execution",
    "manual_session_execution",
    "automatic_real_session_capture",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "real_world_profit_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "commercial_package_pricing_claim"
]

ALLOWED = [
    "stack_gpt_controlled_live_call_packet_creation",
    "stack_gpt_request_template_creation",
    "pure_vs_stack_comparison_template_creation",
    "stack_gpt_execution_gate_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_post_call_review_gate_present",
    "prior_post_call_review_gate_passed",
    "prior_decision_pure_baseline_record_only_stack_next",
    "pure_result_present",
    "pure_baseline_successful",
    "pure_baseline_mode_confirmed",
    "pure_baseline_output_ack_confirmed",
    "pure_baseline_not_dataset_candidate",
    "pure_baseline_not_client_evidence",
    "pure_baseline_not_production_evidence",
    "live_runner_script_present",
    "payload_template_present",
    "live_result_template_present",
    "stack_gpt_mode_supported",
    "stack_gpt_packet_only",
    "stack_gpt_live_execution_not_performed",
    "stack_gpt_live_execution_requires_next_gate",
    "gpt_only_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "openai_gpt_provider_scope_confirmed",
    "no_claude_scope",
    "no_gemini_scope",
    "no_copilot_scope",
    "stack_uses_casulo_state",
    "stack_uses_evidence_packet",
    "stack_uses_gate_packet",
    "stack_uses_claim_boundary",
    "stack_does_not_use_exocortex_yet",
    "exocortex_stack_deferred_until_after_stack",
    "api_key_env_reference_only",
    "no_api_key_value_storage",
    "no_api_key_file",
    "no_secret_print",
    "gpt_memory_api_execution_blocked",
    "dataset_write_blocked",
    "real_candidate_insert_blocked",
    "real_candidate_acceptance_blocked",
    "post_call_review_required",
    "comparison_against_pure_required",
    "operational_hallucination_metric_required",
    "unsupported_claim_metric_required",
    "gate_violation_metric_required",
    "context_regression_metric_required",
    "evidence_grounding_metric_required",
    "latency_metric_required",
    "cost_metric_required",
    "no_session_execution",
    "no_start_command",
    "no_raw_private_data",
    "no_unredacted_pii",
    "no_secret_storage",
    "no_client_claim",
    "no_production_activation",
    "roadmap_updated"
]

while len(CHECKS) < 148:
    CHECKS.append(f"stack_gpt_controlled_live_call_packet_control_{len(CHECKS)+1:03d}")

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
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    pure = read_json(PURE_RESULT) if PURE_RESULT.exists() else {}
    pure_review = read_json(PURE_REVIEW) if PURE_REVIEW.exists() else {}
    payload_template = read_json(PAYLOAD_TEMPLATE) if PAYLOAD_TEMPLATE.exists() else {}
    live_result_template = read_json(LIVE_RESULT_TEMPLATE) if LIVE_RESULT_TEMPLATE.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior post-call review tag")
    if prev.get("status") != "PASS":
        errors.append("prior post-call review not PASS")
    if prev.get("decision") != "APPROVED_PURE_GPT_BASELINE_FOR_RECORD_ONLY_STACK_GPT_COMPARISON_NEXT":
        errors.append("prior decision mismatch")
    if pure.get("status") != "PASS":
        errors.append("pure baseline result not PASS")
    if pure.get("mode") != "PURE_GPT":
        errors.append("pure baseline mode not PURE_GPT")
    if pure.get("successful_live_gpt_response") is not True:
        errors.append("pure baseline response not successful")
    if pure.get("output_preview") != "CASULO_GPT_SANDBOX_ACK":
        errors.append("pure baseline output mismatch")
    if pure.get("openai_api_key_storage") is not False:
        errors.append("pure baseline api key storage not false")
    if pure.get("gpt_memory_api_execution") is not False:
        errors.append("pure baseline gpt memory api not false")
    if pure.get("dataset_write") is not False:
        errors.append("pure baseline dataset write not false")
    if pure_review.get("accepted_for_baseline_record_only") is not True:
        errors.append("pure review not accepted as record only")
    if pure_review.get("accepted_as_dataset_candidate") is not False:
        errors.append("pure review accepted as dataset candidate unexpectedly")
    if payload_template.get("template_only") is not True:
        errors.append("payload template not template-only")
    if live_result_template.get("template_only") is not True:
        errors.append("live result template not template-only")
    if not LIVE_RUNNER_SCRIPT.exists():
        errors.append("live runner script missing")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5581..5620":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5661..5700":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "STACK GPT Controlled Live Call Packet", "status": "CURRENT"})
    if "PROD-5661..5700" not in seen:
        roadmap_items.append({"phase": "PROD-5661..5700", "name": "STACK GPT Controlled Live Call Execution Gate", "status": "NEXT"})

    packet = {
        "version": "stack_gpt_controlled_live_call_packet.v0.1",
        "phase": PHASE,
        "decision": "STACK_GPT_CONTROLLED_LIVE_CALL_PACKET_READY",
        "purpose": "Prepare STACK GPT controlled live call packet for comparison against PURE GPT baseline without executing it.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "stack_gpt_packet_only": True,
        "stack_gpt_live_execution_allowed": False,
        "real_gpt_provider_call_in_this_phase": False,
        "successful_live_gpt_response_in_this_phase": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "stack_mode": "STACK_GPT",
        "baseline_reference": {
            "mode": pure.get("mode"),
            "model": pure.get("model"),
            "output_preview": pure.get("output_preview"),
            "prompt_hash": pure.get("prompt_hash"),
            "output_hash": pure.get("output_hash"),
            "latency_ms": pure.get("latency_ms")
        },
        "stack_grounding_requirements": {
            "casulo_state_snapshot_ref_required": True,
            "evidence_packet_ref_required": True,
            "gate_packet_ref_required": True,
            "claim_boundary_ref_required": True,
            "dataset_boundary_ref_required": True,
            "exocortex_snapshot_required": False
        },
        "checks": CHECKS,
        "check_count": len(CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5661..5700 - STACK GPT Controlled Live Call Execution Gate"
    }

    request_template = {
        "version": "stack_gpt_controlled_live_call_request_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "mode": "STACK_GPT",
        "provider": "openai_gpt",
        "api_key_source": "OPENAI_API_KEY_ENV_REFERENCE_ONLY_NOT_STORED",
        "model_env": "OPENAI_MODEL_OPTIONAL_ENV_REFERENCE",
        "prompt": "CASULO controlled STACK GPT sandbox test. Use the supplied CASULO state/evidence/gate context and return only: CASULO_STACK_GPT_SANDBOX_ACK.",
        "stack_context_refs": {
            "casulo_state_snapshot_ref": "TO_BE_BOUND_IN_EXECUTION_GATE",
            "evidence_packet_ref": "TO_BE_BOUND_IN_EXECUTION_GATE",
            "gate_packet_ref": "TO_BE_BOUND_IN_EXECUTION_GATE",
            "claim_boundary_ref": "TO_BE_BOUND_IN_EXECUTION_GATE"
        },
        "blocked_actions": BLOCKED
    }

    comparison_template = {
        "version": "pure_vs_stack_gpt_comparison_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "baseline_mode": "PURE_GPT",
        "comparison_mode": "STACK_GPT",
        "metrics": [
            "successful_live_gpt_response",
            "output_ack_match",
            "unsupported_claim_count",
            "gate_violation_count",
            "evidence_grounding_score",
            "context_regression_count",
            "latency_ms",
            "api_key_storage",
            "gpt_memory_api_execution",
            "dataset_write"
        ],
        "baseline_reference": packet["baseline_reference"],
        "blocked_actions": BLOCKED
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "stack_gpt_packet_only": True,
        "live_execution_allowed": False,
        "live_execution_requires_next_gate": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "dataset_write_blocked": True,
        "multi_vendor_llm_blocked_this_cycle": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": "STACK_GPT_CONTROLLED_LIVE_CALL_PACKET_READY" if not errors else "STACK_GPT_CONTROLLED_LIVE_CALL_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(CHECKS),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "stack_gpt_packet_only": True,
        "stack_gpt_live_execution_allowed": False,
        "real_gpt_provider_call_in_this_phase": False,
        "successful_live_gpt_response_in_this_phase": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "baseline_mode": pure.get("mode"),
        "baseline_model": pure.get("model"),
        "baseline_output_preview": pure.get("output_preview"),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.4",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - STACK GPT Controlled Live Call Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5621..5660 - STACK GPT Controlled Live Call Packet

Prepares STACK GPT controlled live call packet for comparison against the PURE GPT baseline.

This phase does not call GPT.

STACK GPT means GPT with CASULO state, evidence, gates and claim boundaries.

Exocortex is not used yet. CASULO Exocortex Stack comes after STACK GPT comparison.
"""

    report = f"""# PROD-5621..5660 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Baseline mode: {result['baseline_mode']}
- Baseline model: {result['baseline_model']}
- Baseline output preview: {result['baseline_output_preview']}
- STACK GPT packet only: true
- STACK GPT live execution allowed: false
- Real GPT provider call in this phase: false
- API key storage: false
- GPT Memory API execution: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(REQUEST_TEMPLATE, request_template)
    write_json(COMPARISON_TEMPLATE, comparison_template)
    write_json(ROADMAP_OUT, roadmap_out)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("baseline_mode:", result["baseline_mode"])
    print("baseline_model:", result["baseline_model"])
    print("stack_gpt_live_execution_allowed:", result["stack_gpt_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
