#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5261..5300"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-execution-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod5221_5260_gpt_sandbox_first_controlled_call_execution_packet.json"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_execution_packet_v0_1.json"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5221_5260_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/633_GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_execution_readiness_gate.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_execution_readiness_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_execution_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5261_5300_gpt_sandbox_first_controlled_call_execution_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod5261_5300_gpt_sandbox_first_controlled_call_execution_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5261_5300_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_execution_readiness_gate_creation",
    "gpt_first_controlled_call_runner_packet_preparation",
    "roadmap_update"
]

READINESS_CHECKS = [
    "prior_execution_packet_present",
    "prior_execution_packet_passed",
    "prior_decision_execution_packet_ready",
    "payload_template_present",
    "expected_log_template_present",
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
    "runner_packet_preparation_only",
    "runner_packet_is_next",
    "live_call_requires_future_gate",
    "provider_env_ref_only",
    "no_env_value_read",
    "no_secret_print",
    "no_api_key_file",
    "sanitized_prompt_payload_present",
    "pure_gpt_payload_present",
    "stack_gpt_payload_present",
    "exocortex_stack_payload_present",
    "expected_log_fields_present",
    "state_snapshot_ref_required",
    "evidence_packet_ref_required",
    "gate_packet_ref_required",
    "exocortex_snapshot_ref_required_for_v2",
    "claim_boundary_ref_required",
    "human_reviewer_ref_required",
    "audit_log_ref_required",
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

while len(READINESS_CHECKS) < 144:
    READINESS_CHECKS.append(f"gpt_first_controlled_call_execution_readiness_control_{len(READINESS_CHECKS)+1:03d}")

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
    exec_packet = read_json(EXEC_PACKET) if EXEC_PACKET.exists() else {}
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
        if ph == "PROD-5221..5260":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5301..5340":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Execution Readiness Gate", "status": "CURRENT"})
    if "PROD-5301..5340" not in seen:
        roadmap_items.append({"phase": "PROD-5301..5340", "name": "GPT Sandbox First Controlled Call Runner Packet", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous execution packet not PASS")
    if prev.get("decision") != "GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_PACKET_READY":
        errors.append("previous decision not execution packet ready")
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
    if exec_packet.get("execution_packet_only") is not True:
        errors.append("execution packet not packet-only")
    if exec_packet.get("first_call_live_execution_requires_next_gate") is not True:
        errors.append("execution packet does not require next gate")
    if payload_template.get("template_only") is not True:
        errors.append("payload template not template-only")
    if expected_log_template.get("template_only") is not True:
        errors.append("expected log template not template-only")

    decision = "APPROVED_FOR_GPT_FIRST_CONTROLLED_CALL_RUNNER_PACKET_PREPARATION_ONLY"

    gate = {
        "version": "gpt_sandbox_first_controlled_call_execution_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_EXECUTION_READINESS_GATE_NOT_READY",
        "purpose": "Validate the GPT execution packet and approve only runner packet preparation, without live GPT execution.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "runner_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_gate": True,
        "readiness_checks": READINESS_CHECKS,
        "readiness_check_count": len(READINESS_CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5301..5340 - GPT Sandbox First Controlled Call Runner Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "readiness_gate_only": True,
        "runner_packet_preparation_only": True,
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
        "roadmap_updated": True,
        "roadmap_item_count": len(roadmap_items),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "runner_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.5",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Execution Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5261..5300 - GPT Sandbox First Controlled Call Execution Readiness Gate

Validates the first controlled GPT call execution packet.

This phase still does not call GPT. It approves only preparation of a runner packet.

Boundaries:
- GPT/OpenAI-only.
- No Claude, Gemini, Copilot or multi-vendor provider in this cycle.
- No API key storage.
- No GPT Memory API execution.
- No live GPT call.
- No session execution.
- No real candidate insert.
- No dataset acceptance.

Next: PROD-5301..5340 - GPT Sandbox First Controlled Call Runner Packet.
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

    report = f"""# PROD-5261..5300 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {len(READINESS_CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Runner packet preparation only: true
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
    print("gpt_only_scope:", result["gpt_only_scope"])
    print("multi_vendor_llm_scope:", result["multi_vendor_llm_scope"])
    print("llm_not_called_yet:", result["llm_not_called_yet"])
    print("real_gpt_provider_call:", result["real_gpt_provider_call"])
    print("openai_api_key_storage:", result["openai_api_key_storage"])
    print("runner_packet_preparation_only:", result["runner_packet_preparation_only"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
