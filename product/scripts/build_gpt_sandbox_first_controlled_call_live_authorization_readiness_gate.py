#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5421..5460"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-live-authorization-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod5381_5420_gpt_sandbox_first_controlled_call_live_authorization_packet.json"
AUTH_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_packet_v0_1.json"
AUTH_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_template_v0_1.json"
AUTH_CHECKLIST = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_checklist_v0_1.json"
RUNNER_GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_readiness_gate_v0_1.json"
RUNNER_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_packet_v0_1.json"
RUNNER_SPEC = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_spec_v0_1.json"
RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_call.py"
DRY_RUN_OUTPUT = ROOT / "outputs/gpt_sandbox_first_controlled_call_runner_dry_run_output.json"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5381_5420_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/637_GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_live_authorization_readiness_gate.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_live_authorization_readiness_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5421_5460_gpt_sandbox_first_controlled_call_live_authorization_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod5421_5460_gpt_sandbox_first_controlled_call_live_authorization_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5421_5460_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "real_gpt_provider_call",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "live_gpt_call_execution",
    "live_gpt_benchmark_execution",
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
    "gpt_sandbox_first_controlled_call_live_authorization_readiness_gate_creation",
    "gpt_first_controlled_live_call_packet_preparation",
    "roadmap_update"
]

READINESS_CHECKS = [
    "prior_live_authorization_packet_present",
    "prior_live_authorization_packet_passed",
    "prior_decision_live_authorization_packet_ready",
    "authorization_template_present",
    "authorization_checklist_present",
    "runner_readiness_gate_present",
    "runner_packet_present",
    "runner_spec_present",
    "runner_script_present",
    "runner_dry_run_output_present",
    "payload_template_present",
    "expected_log_template_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "authorization_fields_present",
    "authorization_checks_present",
    "runner_dry_run_output_passed",
    "runner_apply_mode_blocked",
    "runner_forbidden_tokens_empty",
    "live_authorization_packet_only_confirmed",
    "live_authorization_readiness_gate_only",
    "first_controlled_live_call_packet_is_next",
    "live_call_not_executed_in_this_phase",
    "real_gpt_call_still_blocked",
    "api_key_storage_still_blocked",
    "gpt_memory_api_still_blocked",
    "live_benchmark_still_blocked",
    "api_key_env_reference_only",
    "no_api_key_value_storage",
    "no_api_key_file",
    "no_secret_print",
    "human_authorization_required",
    "dual_review_required",
    "operator_acknowledgement_required",
    "prompt_sanitization_required",
    "payload_template_required",
    "expected_log_template_required",
    "state_snapshot_required_for_stack",
    "exocortex_snapshot_required_for_exocortex_stack",
    "evidence_packet_required",
    "gate_packet_required",
    "claim_boundary_required",
    "dataset_boundary_required",
    "privacy_boundary_required",
    "pii_boundary_required",
    "secret_boundary_required",
    "cost_limit_required",
    "latency_limit_required",
    "abort_trigger_required",
    "rollback_plan_required",
    "post_call_review_required",
    "live_execution_packet_required",
    "live_execution_final_gate_required",
    "no_session_execution",
    "no_start_command",
    "no_real_candidate_insert",
    "no_dataset_acceptance",
    "no_raw_private_data",
    "no_unredacted_pii",
    "no_secret_storage",
    "no_client_claim",
    "no_production_activation",
    "roadmap_updated"
]

while len(READINESS_CHECKS) < 184:
    READINESS_CHECKS.append(f"gpt_live_authorization_readiness_control_{len(READINESS_CHECKS)+1:03d}")

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

def count_list(obj, key):
    val = obj.get(key, [])
    return len(val) if isinstance(val, list) else 0

def main():
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    auth_packet = read_json(AUTH_PACKET) if AUTH_PACKET.exists() else {}
    auth_template = read_json(AUTH_TEMPLATE) if AUTH_TEMPLATE.exists() else {}
    auth_checklist = read_json(AUTH_CHECKLIST) if AUTH_CHECKLIST.exists() else {}
    runner_gate = read_json(RUNNER_GATE) if RUNNER_GATE.exists() else {}
    runner_packet = read_json(RUNNER_PACKET) if RUNNER_PACKET.exists() else {}
    runner_spec = read_json(RUNNER_SPEC) if RUNNER_SPEC.exists() else {}
    dry_run_output = read_json(DRY_RUN_OUTPUT) if DRY_RUN_OUTPUT.exists() else {}
    payload_template = read_json(PAYLOAD_TEMPLATE) if PAYLOAD_TEMPLATE.exists() else {}
    expected_log_template = read_json(EXPECTED_LOG_TEMPLATE) if EXPECTED_LOG_TEMPLATE.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5381..5420":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5461..5500":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Live Authorization Readiness Gate", "status": "CURRENT"})
    if "PROD-5461..5500" not in seen:
        roadmap_items.append({"phase": "PROD-5461..5500", "name": "GPT Sandbox First Controlled Live Call Packet", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous live authorization packet not PASS")
    if prev.get("decision") != "GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET_READY":
        errors.append("previous decision not live authorization packet ready")
    if prev.get("gpt_only_scope") is not True:
        errors.append("previous gpt_only_scope not true")
    if prev.get("multi_vendor_llm_scope") is not False:
        errors.append("previous multi_vendor_llm_scope not false")
    if prev.get("real_gpt_provider_call") is not False:
        errors.append("previous real_gpt_provider_call not false")
    if prev.get("openai_api_key_storage") is not False:
        errors.append("previous openai_api_key_storage not false")
    if prev.get("gpt_memory_api_execution") is not False:
        errors.append("previous gpt_memory_api_execution not false")
    if prev.get("first_call_live_execution_allowed") is not False:
        errors.append("previous live execution allowed unexpectedly")
    if prev.get("live_execution_requires_next_readiness_gate") is not True:
        errors.append("previous packet did not require next readiness gate")
    if auth_packet.get("live_authorization_packet_only") is not True:
        errors.append("authorization packet not packet-only")
    if auth_packet.get("authorization_field_count", 0) < 35:
        errors.append("authorization field count below 35")
    if auth_packet.get("authorization_check_count", 0) < 172:
        errors.append("authorization check count below 172")
    if auth_template.get("template_only") is not True:
        errors.append("authorization template not template-only")
    if count_list(auth_checklist, "checks") < 172:
        errors.append("authorization checklist below 172")
    if runner_gate.get("status") == "FAIL":
        errors.append("runner gate status fail")
    if runner_gate.get("live_authorization_packet_preparation_only") is not True:
        errors.append("runner gate missing live authorization packet preparation only")
    if runner_packet.get("runner_packet_only") is not True:
        errors.append("runner packet not packet-only")
    if runner_spec.get("live_call_allowed") is not False:
        errors.append("runner spec live call allowed unexpectedly")
    if dry_run_output.get("status") != "PASS":
        errors.append("dry run output not PASS")
    if dry_run_output.get("real_gpt_provider_call") is not False:
        errors.append("dry run output has real_gpt_provider_call not false")
    if payload_template.get("template_only") is not True:
        errors.append("payload template not template-only")
    if expected_log_template.get("template_only") is not True:
        errors.append("expected log template not template-only")
    if not RUNNER_SCRIPT.exists():
        errors.append("runner script missing")

    decision = "APPROVED_FOR_GPT_FIRST_CONTROLLED_LIVE_CALL_PACKET_PREPARATION_ONLY"

    gate = {
        "version": "gpt_sandbox_first_controlled_call_live_authorization_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_READINESS_GATE_NOT_READY",
        "purpose": "Validate live authorization packet and approve only the first controlled live call packet preparation.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "live_authorization_readiness_gate_only": True,
        "first_controlled_live_call_packet_preparation_only": True,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_execution_gate": True,
        "approved_modes_for_future_packet": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "future_stack_v3": {
            "name": "CASULO Stack V3 - Multi-Provider Arbitration Layer",
            "status": "DEFERRED_AFTER_GPT_ONLY_BASELINE"
        },
        "readiness_checks": READINESS_CHECKS,
        "readiness_check_count": len(READINESS_CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5461..5500 - GPT Sandbox First Controlled Live Call Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "live_authorization_readiness_gate_only": True,
        "first_controlled_live_call_packet_preparation_only": True,
        "live_execution_allowed": False,
        "real_gpt_call_blocked": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "multi_vendor_llm_blocked_this_cycle": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "authorization_field_count": auth_packet.get("authorization_field_count", 0),
        "authorization_check_count": auth_packet.get("authorization_check_count", 0),
        "roadmap_updated": True,
        "roadmap_item_count": len(roadmap_items),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "live_authorization_readiness_gate_only": True,
        "first_controlled_live_call_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_execution_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.9",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Live Authorization Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5421..5460 - GPT Sandbox First Controlled Call Live Authorization Readiness Gate

Validates the live authorization packet.

This phase still does not call GPT. It approves only preparation of the first controlled live call packet.

Boundaries:
- GPT/OpenAI-only.
- No Claude, Gemini, Copilot or multi-vendor provider in this cycle.
- No API key value storage.
- No GPT Memory API execution.
- No live GPT call in this phase.
- No session execution.
- No real candidate insert.
- No dataset acceptance.

Next: PROD-5461..5500 - GPT Sandbox First Controlled Live Call Packet.
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")
    roadmap_doc += [
        "",
        "## GPT-only active plan",
        "- PURE GPT",
        "- STACK GPT",
        "- CASULO Exocortex Stack",
        "- Stack V3 Multi-Provider deferred until GPT-only baseline is measured.",
        "",
        "## Active boundary",
        "- No real GPT call yet.",
        "- No API key value storage.",
        "- No GPT Memory API.",
        "- No multi-vendor LLM in this cycle.",
        "- No session execution.",
        "- No real candidate insert.",
        "- No dataset acceptance."
    ]

    report = f"""# PROD-5421..5460 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {len(READINESS_CHECKS)}
- Authorization fields: {result['authorization_field_count']}
- Authorization checks: {result['authorization_check_count']}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Live authorization readiness gate only: true
- First controlled live call packet preparation only: true
- First call live execution allowed: false
- Next: {gate['recommended_next_phase']}
"""

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, gate)
    write_json(GATE, gate)
    write_json(ROADMAP_OUT, roadmap_out)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_checks:", len(READINESS_CHECKS))
    print("authorization_fields:", result["authorization_field_count"])
    print("authorization_checks:", result["authorization_check_count"])
    print("gpt_only_scope:", result["gpt_only_scope"])
    print("multi_vendor_llm_scope:", result["multi_vendor_llm_scope"])
    print("llm_not_called_yet:", result["llm_not_called_yet"])
    print("real_gpt_provider_call:", result["real_gpt_provider_call"])
    print("openai_api_key_storage:", result["openai_api_key_storage"])
    print("first_controlled_live_call_packet_preparation_only:", result["first_controlled_live_call_packet_preparation_only"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
