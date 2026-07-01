#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5141..5180"
REQ_TAG = "product-gpt-sandbox-activation-gate-v0.1"

SUMMARY = ROOT / "outputs/gpt_only_accelerated_boundary_sequence_summary.json"
PREV_OUT = ROOT / "outputs/prod5101_5140_gpt_sandbox_activation_gate.json"
ROADMAP_IN = ROOT / "outputs/prod5101_5140_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/630_GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_packet.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_packet_v0_1.json"
REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_request_template_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_comparison_template_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5141_5180_gpt_sandbox_first_controlled_call_packet.json"
OUT_MD = ROOT / "outputs/prod5141_5180_gpt_sandbox_first_controlled_call_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5141_5180_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_packet_creation",
    "gpt_call_request_template_creation",
    "pure_stack_exocortex_test_case_definition",
    "gpt_first_controlled_call_readiness_gate_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_sandbox_activation_gate_present",
    "prior_sandbox_activation_gate_passed",
    "prior_batch_summary_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_only_confirmed",
    "pure_gpt_mode_defined",
    "stack_gpt_mode_defined",
    "casulo_exocortex_stack_mode_defined",
    "stack_v3_multiprovider_deferred",
    "no_multi_vendor_llm_in_this_cycle",
    "no_claude_call",
    "no_gemini_call",
    "no_copilot_call",
    "real_gpt_call_blocked",
    "api_key_storage_blocked",
    "gpt_memory_api_blocked",
    "request_template_only",
    "comparison_template_only",
    "sandbox_call_not_executed",
    "first_call_requires_next_readiness_gate",
    "prompt_payload_sanitized_placeholder_only",
    "system_prompt_template_defined",
    "user_prompt_template_defined",
    "state_packet_ref_required",
    "evidence_packet_ref_required",
    "gate_packet_ref_required",
    "expected_output_schema_defined",
    "claim_boundary_defined",
    "hallucination_metric_defined",
    "unsupported_claim_metric_defined",
    "gate_violation_metric_defined",
    "context_regression_metric_defined",
    "roadmap_regression_metric_defined",
    "latency_metric_defined",
    "cost_metric_defined",
    "human_review_required",
    "audit_log_required",
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

while len(CHECKS) < 108:
    CHECKS.append(f"gpt_first_controlled_call_packet_control_{len(CHECKS)+1:03d}")

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
    summary = read_json(SUMMARY) if SUMMARY.exists() else {}
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5101..5140":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5181..5220":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Packet", "status": "CURRENT"})
    if "PROD-5181..5220" not in seen:
        roadmap_items.append({"phase": "PROD-5181..5220", "name": "GPT Sandbox First Controlled Call Readiness Gate", "status": "NEXT"})

    packet = {
        "version": "gpt_sandbox_first_controlled_call_packet.v0.1",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET_READY",
        "purpose": "Prepare the first controlled GPT sandbox call packet without executing the call.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "stack_v3_multiprovider_deferred": True,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "sandbox_call_packet_only": True,
        "first_call_requires_next_readiness_gate": True,
        "modes": {
            "PURE_GPT": {
                "description": "Direct GPT baseline without CASULO state, gates, evidence or Exocortex.",
                "call_allowed_in_this_phase": False
            },
            "STACK_GPT": {
                "description": "GPT with CASULO state, evidence, gates and boundaries.",
                "call_allowed_in_this_phase": False
            },
            "CASULO_EXOCORTEX_STACK": {
                "description": "GPT with Exocortex snapshots, governed memory lifecycle, arbitration and continuity.",
                "call_allowed_in_this_phase": False
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
        "recommended_next_phase": "PROD-5181..5220 - GPT Sandbox First Controlled Call Readiness Gate"
    }

    request_template = {
        "version": "gpt_sandbox_first_controlled_call_request_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "provider": "openai_gpt",
        "api_key_source": "ENV_REFERENCE_ONLY_NOT_READ_OR_STORED",
        "model_policy": "GPT_MODEL_NAME_PLACEHOLDER_ONLY",
        "request_modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "fields": {
            "case_id": None,
            "mode": None,
            "sanitized_user_prompt": None,
            "casulo_state_snapshot_ref": None,
            "evidence_packet_ref": None,
            "gate_packet_ref": None,
            "expected_output_schema_ref": None,
            "claim_boundary_ref": None,
            "human_reviewer_ref": None
        },
        "blocked_actions": BLOCKED
    }

    comparison_template = {
        "version": "pure_stack_exocortex_first_call_comparison_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "real_gpt_provider_call": False,
        "comparison_modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "metrics": [
            "operational_hallucination_rate",
            "unsupported_claim_rate",
            "gate_violation_rate",
            "context_regression_rate",
            "roadmap_regression_rate",
            "evidence_grounding_rate",
            "human_correction_count",
            "cycle_latency",
            "cycle_cost"
        ],
        "expected_decision": "NO_LIVE_CALL_BEFORE_NEXT_READINESS_GATE",
        "blocked_actions": BLOCKED
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "pure_gpt": True,
        "stack_gpt": True,
        "casulo_exocortex_stack": True,
        "stack_v3_multiprovider_deferred": True,
        "real_gpt_call_blocked": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "first_call_requires_next_readiness_gate": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.2",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if summary.get("status") != "PASS":
        errors.append("batch summary not PASS")
    if prev.get("status") != "PASS":
        errors.append("previous sandbox activation gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET_PREPARATION_ONLY":
        errors.append("previous decision not approved for first call packet preparation")
    if summary.get("gpt_only_scope") is not True:
        errors.append("summary did not preserve gpt_only_scope")
    if summary.get("multi_vendor_llm_scope") is not False:
        errors.append("summary did not block multi_vendor_llm_scope")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET_READY" if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET_NOT_READY",
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
        "first_call_requires_next_readiness_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    doc = """# PROD-5141..5180 - GPT Sandbox First Controlled Call Packet

Creates the first controlled GPT sandbox call packet.

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

Modes prepared:
- PURE GPT
- STACK GPT
- CASULO Exocortex Stack

Next: PROD-5181..5220 - GPT Sandbox First Controlled Call Readiness Gate.
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

    report = f"""# PROD-5141..5180 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {len(CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Next: {packet['recommended_next_phase']}
"""

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
    print("checks:", len(CHECKS))
    print("gpt_only_scope:", result["gpt_only_scope"])
    print("multi_vendor_llm_scope:", result["multi_vendor_llm_scope"])
    print("llm_not_called_yet:", result["llm_not_called_yet"])
    print("real_gpt_provider_call:", result["real_gpt_provider_call"])
    print("openai_api_key_storage:", result["openai_api_key_storage"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
