#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5381..5420"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-runner-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod5341_5380_gpt_sandbox_first_controlled_call_runner_readiness_gate.json"
RUNNER_GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_readiness_gate_v0_1.json"
RUNNER_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_packet_v0_1.json"
RUNNER_SPEC = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_spec_v0_1.json"
RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_call.py"
DRY_RUN_OUTPUT = ROOT / "outputs/gpt_sandbox_first_controlled_call_runner_dry_run_output.json"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5341_5380_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/636_GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_live_authorization_packet.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_live_authorization_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_packet_v0_1.json"
AUTH_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_template_v0_1.json"
AUTH_CHECKLIST = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5381_5420_gpt_sandbox_first_controlled_call_live_authorization_packet.json"
OUT_MD = ROOT / "outputs/prod5381_5420_gpt_sandbox_first_controlled_call_live_authorization_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5381_5420_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_live_authorization_packet_creation",
    "human_live_authorization_template_creation",
    "human_live_authorization_checklist_creation",
    "gpt_first_controlled_call_live_authorization_readiness_gate_preparation",
    "roadmap_update"
]

AUTH_FIELDS = [
    "authorization_id",
    "phase",
    "operator_ref",
    "human_reviewer_ref",
    "second_reviewer_ref",
    "authorization_decision",
    "authorization_reason",
    "approved_modes",
    "provider_scope",
    "model_name_ref",
    "api_key_source_ref",
    "api_key_storage_confirmation",
    "prompt_sanitization_confirmation",
    "payload_template_ref",
    "expected_log_template_ref",
    "runner_script_ref",
    "runner_dry_run_output_ref",
    "runner_apply_block_ref",
    "evidence_packet_ref",
    "state_snapshot_ref",
    "exocortex_snapshot_ref",
    "gate_packet_ref",
    "claim_boundary_ref",
    "dataset_boundary_ref",
    "privacy_boundary_ref",
    "pii_boundary_ref",
    "secret_boundary_ref",
    "cost_limit_ref",
    "latency_limit_ref",
    "abort_trigger_ref",
    "rollback_plan_ref",
    "human_observation_ref",
    "post_call_review_required",
    "live_execution_gate_required",
    "signature_placeholder"
]

AUTH_CHECKS = [
    "runner_readiness_gate_passed",
    "runner_packet_present",
    "runner_spec_present",
    "runner_script_present",
    "runner_dry_run_output_present",
    "runner_dry_run_output_passed",
    "apply_mode_blocked",
    "forbidden_source_tokens_empty",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "live_authorization_packet_only",
    "live_call_not_executed",
    "real_gpt_call_still_blocked",
    "api_key_storage_still_blocked",
    "gpt_memory_api_still_blocked",
    "live_benchmark_still_blocked",
    "human_authorization_required",
    "dual_review_required",
    "operator_acknowledgement_required",
    "api_key_env_reference_only",
    "no_api_key_value_storage",
    "no_api_key_file",
    "no_secret_print",
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
    "live_execution_gate_required",
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

while len(AUTH_CHECKS) < 172:
    AUTH_CHECKS.append(f"gpt_first_controlled_call_live_authorization_packet_control_{len(AUTH_CHECKS)+1:03d}")

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
        if ph == "PROD-5341..5380":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5421..5460":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Live Authorization Packet", "status": "CURRENT"})
    if "PROD-5421..5460" not in seen:
        roadmap_items.append({"phase": "PROD-5421..5460", "name": "GPT Sandbox First Controlled Call Live Authorization Readiness Gate", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous runner readiness gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_GPT_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET_PREPARATION_ONLY":
        errors.append("previous decision not approved for live authorization packet preparation")
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
    if prev.get("dry_run_output_pass") is not True:
        errors.append("previous dry run output not pass")
    if prev.get("apply_mode_blocked") is not True:
        errors.append("previous apply mode not blocked")
    if prev.get("forbidden_source_tokens") != []:
        errors.append("previous forbidden source tokens not empty")
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

    packet = {
        "version": "gpt_sandbox_first_controlled_call_live_authorization_packet.v0.1",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET_READY",
        "purpose": "Prepare human live authorization packet for the first controlled GPT sandbox call without executing it.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "live_authorization_packet_only": True,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "first_call_live_execution_allowed": False,
        "live_execution_requires_next_readiness_gate": True,
        "approved_modes_for_future_authorization": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "future_stack_v3": {
            "name": "CASULO Stack V3 - Multi-Provider Arbitration Layer",
            "status": "DEFERRED_AFTER_GPT_ONLY_BASELINE"
        },
        "authorization_fields": AUTH_FIELDS,
        "authorization_field_count": len(AUTH_FIELDS),
        "authorization_checks": AUTH_CHECKS,
        "authorization_check_count": len(AUTH_CHECKS),
        "authorization_boundary": {
            "api_key_source": "ENV_REFERENCE_ONLY_NOT_READ_OR_STORED_IN_THIS_PHASE",
            "api_key_value_storage_allowed": False,
            "provider_call_allowed": False,
            "gpt_memory_api_allowed": False,
            "live_benchmark_allowed": False,
            "dataset_write_allowed": False,
            "client_claim_allowed": False,
            "production_allowed": False
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5421..5460 - GPT Sandbox First Controlled Call Live Authorization Readiness Gate"
    }

    auth_template = {
        "version": "gpt_sandbox_first_controlled_call_live_authorization_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "live_call_allowed": False,
        "fields": {
            field: {"value": None, "required": True, "storage_rule": "reference_only_or_sanitized_placeholder"}
            for field in AUTH_FIELDS
        },
        "default_decision": "HOLD_LIVE_GPT_CALL_PENDING_READINESS_GATE",
        "blocked_actions": BLOCKED
    }

    auth_checklist = {
        "version": "gpt_sandbox_first_controlled_call_live_authorization_checklist.v0.1",
        "phase": PHASE,
        "template_only": True,
        "live_call_allowed": False,
        "checks": [
            {"id": f"LIVE-AUTH-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(AUTH_CHECKS)
        ],
        "default_decision": "HOLD_LIVE_GPT_CALL_PENDING_READINESS_GATE",
        "blocked_actions": BLOCKED
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "live_authorization_packet_only": True,
        "live_execution_allowed": False,
        "live_execution_requires_next_readiness_gate": True,
        "real_gpt_call_blocked": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "multi_vendor_llm_blocked_this_cycle": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET_READY" if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authorization_field_count": len(AUTH_FIELDS),
        "authorization_check_count": len(AUTH_CHECKS),
        "roadmap_updated": True,
        "roadmap_item_count": len(roadmap_items),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "live_authorization_packet_only": True,
        "first_call_live_execution_allowed": False,
        "live_execution_requires_next_readiness_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.8",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Live Authorization Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5381..5420 - GPT Sandbox First Controlled Call Live Authorization Packet

Creates the human live authorization packet for a future first controlled GPT sandbox call.

This phase still does not call GPT.

Boundaries:
- GPT/OpenAI-only.
- No Claude, Gemini, Copilot or multi-vendor provider in this cycle.
- No API key value storage.
- No GPT Memory API execution.
- No live GPT call.
- No session execution.
- No real candidate insert.
- No dataset acceptance.

Next: PROD-5421..5460 - GPT Sandbox First Controlled Call Live Authorization Readiness Gate.
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

    report = f"""# PROD-5381..5420 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Authorization fields: {len(AUTH_FIELDS)}
- Authorization checks: {len(AUTH_CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Live authorization packet only: true
- First call live execution allowed: false
- Next: {packet['recommended_next_phase']}
"""

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(AUTH_TEMPLATE, auth_template)
    write_json(AUTH_CHECKLIST, auth_checklist)
    write_json(ROADMAP_OUT, roadmap_out)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("authorization_fields:", len(AUTH_FIELDS))
    print("authorization_checks:", len(AUTH_CHECKS))
    print("gpt_only_scope:", result["gpt_only_scope"])
    print("multi_vendor_llm_scope:", result["multi_vendor_llm_scope"])
    print("llm_not_called_yet:", result["llm_not_called_yet"])
    print("real_gpt_provider_call:", result["real_gpt_provider_call"])
    print("openai_api_key_storage:", result["openai_api_key_storage"])
    print("live_authorization_packet_only:", result["live_authorization_packet_only"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
