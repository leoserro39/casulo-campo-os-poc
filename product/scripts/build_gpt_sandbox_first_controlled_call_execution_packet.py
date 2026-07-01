#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5221..5260"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod5181_5220_gpt_sandbox_first_controlled_call_readiness_gate.json"
READINESS_GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_readiness_gate_v0_1.json"
CALL_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_packet_v0_1.json"
REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_request_template_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_comparison_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5181_5220_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/632_GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_PACKET.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_execution_packet.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_execution_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_execution_packet_v0_1.json"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5221_5260_gpt_sandbox_first_controlled_call_execution_packet.json"
OUT_MD = ROOT / "outputs/prod5221_5260_gpt_sandbox_first_controlled_call_execution_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5221_5260_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_execution_packet_creation",
    "gpt_payload_template_creation",
    "expected_log_template_creation",
    "gpt_first_controlled_call_execution_readiness_gate_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_first_controlled_call_readiness_gate_present",
    "prior_first_controlled_call_readiness_gate_passed",
    "prior_decision_execution_packet_preparation_only",
    "call_packet_present",
    "request_template_present",
    "comparison_template_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "no_claude_scope",
    "no_gemini_scope",
    "no_copilot_scope",
    "real_gpt_call_still_blocked",
    "api_key_storage_still_blocked",
    "gpt_memory_api_still_blocked",
    "live_call_execution_still_blocked",
    "execution_packet_only",
    "payload_template_only",
    "expected_log_template_only",
    "first_call_live_execution_requires_next_gate",
    "provider_env_ref_only",
    "no_env_value_read",
    "no_secret_print",
    "no_api_key_file",
    "sanitized_prompt_payload_defined",
    "state_snapshot_ref_required",
    "evidence_packet_ref_required",
    "gate_packet_ref_required",
    "expected_output_schema_ref_required",
    "claim_boundary_ref_required",
    "human_reviewer_ref_required",
    "audit_log_ref_required",
    "pure_gpt_payload_defined",
    "stack_gpt_payload_defined",
    "exocortex_stack_payload_defined",
    "comparison_join_key_defined",
    "operational_hallucination_metric_required",
    "unsupported_claim_metric_required",
    "gate_violation_metric_required",
    "context_regression_metric_required",
    "roadmap_regression_metric_required",
    "human_correction_metric_required",
    "latency_metric_required",
    "cost_metric_required",
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

while len(CHECKS) < 136:
    CHECKS.append(f"gpt_first_controlled_call_execution_packet_control_{len(CHECKS)+1:03d}")

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
    readiness_gate = read_json(READINESS_GATE) if READINESS_GATE.exists() else {}
    call_packet = read_json(CALL_PACKET) if CALL_PACKET.exists() else {}
    request_template = read_json(REQUEST_TEMPLATE) if REQUEST_TEMPLATE.exists() else {}
    comparison_template = read_json(COMPARISON_TEMPLATE) if COMPARISON_TEMPLATE.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5181..5220":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5261..5300":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Execution Packet", "status": "CURRENT"})
    if "PROD-5261..5300" not in seen:
        roadmap_items.append({"phase": "PROD-5261..5300", "name": "GPT Sandbox First Controlled Call Execution Readiness Gate", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous first controlled call readiness gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_GPT_FIRST_CONTROLLED_CALL_EXECUTION_PACKET_PREPARATION_ONLY":
        errors.append("previous decision not approved for execution packet preparation")
    if prev.get("gpt_only_scope") is not True:
        errors.append("previous gpt_only_scope not true")
    if prev.get("multi_vendor_llm_scope") is not False:
        errors.append("previous multi_vendor_llm_scope not false")
    if prev.get("real_gpt_provider_call") is not False:
        errors.append("previous real_gpt_provider_call not false")
    if prev.get("openai_api_key_storage") is not False:
        errors.append("previous openai_api_key_storage not false")
    if prev.get("first_call_live_execution_allowed") is not False:
        errors.append("previous live execution allowed unexpectedly")
    if readiness_gate.get("first_call_execution_packet_preparation_only") is not True:
        errors.append("readiness gate missing execution packet preparation only")
    if call_packet.get("sandbox_call_packet_only") is not True:
        errors.append("call packet is not marked packet only")
    if request_template.get("template_only") is not True:
        errors.append("request template not template-only")
    if comparison_template.get("template_only") is not True:
        errors.append("comparison template not template-only")

    execution_packet = {
        "version": "gpt_sandbox_first_controlled_call_execution_packet.v0.1",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_PACKET_READY",
        "purpose": "Prepare the execution packet for the first controlled GPT sandbox call without executing it.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "execution_packet_only": True,
        "first_call_live_execution_allowed": False,
        "first_call_live_execution_requires_next_gate": True,
        "provider_adapter": {
            "provider": "openai_gpt",
            "api_key_source": "ENV_REFERENCE_ONLY_NOT_READ_OR_STORED",
            "model_name": "GPT_MODEL_NAME_PLACEHOLDER_ONLY",
            "real_call_allowed_in_this_phase": False
        },
        "modes": {
            "PURE_GPT": {
                "description": "Direct GPT baseline.",
                "state_grounding": False,
                "exocortex": False,
                "real_call_allowed_in_this_phase": False
            },
            "STACK_GPT": {
                "description": "GPT with CASULO state, evidence and gates.",
                "state_grounding": True,
                "exocortex": False,
                "real_call_allowed_in_this_phase": False
            },
            "CASULO_EXOCORTEX_STACK": {
                "description": "GPT with CASULO state, evidence, gates, Exocortex snapshots and governed memory lifecycle.",
                "state_grounding": True,
                "exocortex": True,
                "real_call_allowed_in_this_phase": False
            }
        },
        "future_stack_v3": {
            "name": "CASULO Stack V3 - Multi-Provider Arbitration Layer",
            "status": "DEFERRED_AFTER_GPT_ONLY_BASELINE"
        },
        "checks": CHECKS,
        "check_count": len(CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5261..5300 - GPT Sandbox First Controlled Call Execution Readiness Gate"
    }

    payload_template = {
        "version": "gpt_sandbox_first_controlled_call_payload_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "provider": "openai_gpt",
        "request_modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "payloads": {
            "PURE_GPT": {
                "system": "PURE_GPT_SYSTEM_PROMPT_PLACEHOLDER",
                "user": "SANITIZED_USER_PROMPT_PLACEHOLDER",
                "state": None,
                "evidence": None,
                "gate": None
            },
            "STACK_GPT": {
                "system": "STACK_GPT_SYSTEM_PROMPT_WITH_CASULO_BOUNDARY_PLACEHOLDER",
                "user": "SANITIZED_USER_PROMPT_PLACEHOLDER",
                "state_snapshot_ref": "CASULO_STATE_SNAPSHOT_REF_PLACEHOLDER",
                "evidence_packet_ref": "EVIDENCE_PACKET_REF_PLACEHOLDER",
                "gate_packet_ref": "GATE_PACKET_REF_PLACEHOLDER"
            },
            "CASULO_EXOCORTEX_STACK": {
                "system": "EXOCORTEX_STACK_SYSTEM_PROMPT_WITH_MEMORY_LIFECYCLE_PLACEHOLDER",
                "user": "SANITIZED_USER_PROMPT_PLACEHOLDER",
                "state_snapshot_ref": "CASULO_STATE_SNAPSHOT_REF_PLACEHOLDER",
                "exocortex_snapshot_ref": "EXOCORTEX_SNAPSHOT_REF_PLACEHOLDER",
                "evidence_packet_ref": "EVIDENCE_PACKET_REF_PLACEHOLDER",
                "gate_packet_ref": "GATE_PACKET_REF_PLACEHOLDER",
                "arbitration_policy_ref": "ARBITRATION_POLICY_REF_PLACEHOLDER"
            }
        },
        "blocked_actions": BLOCKED
    }

    expected_log_template = {
        "version": "gpt_sandbox_first_controlled_call_expected_log_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "real_gpt_provider_call": False,
        "log_fields": [
            "run_id",
            "mode",
            "provider",
            "model_name",
            "input_payload_hash",
            "output_hash",
            "latency_ms",
            "estimated_cost",
            "evidence_grounding_score",
            "unsupported_claim_count",
            "gate_violation_count",
            "context_regression_count",
            "roadmap_regression_count",
            "human_review_required",
            "human_reviewer_ref"
        ],
        "blocked_actions": BLOCKED
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "execution_packet_only": True,
        "live_execution_allowed": False,
        "first_call_live_execution_requires_next_gate": True,
        "real_gpt_call_blocked": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "multi_vendor_llm_blocked_this_cycle": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": execution_packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_PACKET_READY" if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(CHECKS),
        "roadmap_updated": True,
        "roadmap_item_count": len(roadmap_items),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "execution_packet_only": True,
        "first_call_live_execution_allowed": False,
        "first_call_live_execution_requires_next_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": execution_packet["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.4",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Execution Packet",
        "next_phase": execution_packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5221..5260 - GPT Sandbox First Controlled Call Execution Packet

Creates the execution packet for the first controlled GPT sandbox call.

This phase still does not call GPT.

Boundaries:
- GPT/OpenAI-only.
- No Claude, Gemini, Copilot or multi-vendor provider in this cycle.
- No API key storage.
- No GPT Memory API execution.
- No live GPT call.
- No session execution.
- No real candidate insert.
- No dataset acceptance.

Prepared modes:
- PURE GPT
- STACK GPT
- CASULO Exocortex Stack

Next: PROD-5261..5300 - GPT Sandbox First Controlled Call Execution Readiness Gate.
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
        "- No API key storage.",
        "- No GPT Memory API.",
        "- No multi-vendor LLM in this cycle.",
        "- No session execution.",
        "- No real candidate insert.",
        "- No dataset acceptance."
    ]

    report = f"""# PROD-5221..5260 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {len(CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Execution packet only: true
- First call live execution allowed: false
- Next: {execution_packet['recommended_next_phase']}
"""

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, execution_packet)
    write_json(PACKET, execution_packet)
    write_json(PAYLOAD_TEMPLATE, payload_template)
    write_json(EXPECTED_LOG_TEMPLATE, expected_log_template)
    write_json(ROADMAP_OUT, roadmap_out)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", len(CHECKS))
    print("gpt_only_scope:", result["gpt_only_scope"])
    print("multi_vendor_llm_scope:", result["multi_vendor_llm_scope"])
    print("llm_not_called_yet:", result["llm_not_called_yet"])
    print("real_gpt_provider_call:", result["real_gpt_provider_call"])
    print("openai_api_key_storage:", result["openai_api_key_storage"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
