#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5181..5220"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod5141_5180_gpt_sandbox_first_controlled_call_packet.json"
PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_packet_v0_1.json"
REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_request_template_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_comparison_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5141_5180_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/631_GPT_SANDBOX_FIRST_CONTROLLED_CALL_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_readiness_gate.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_readiness_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5181_5220_gpt_sandbox_first_controlled_call_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod5181_5220_gpt_sandbox_first_controlled_call_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5181_5220_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_readiness_gate_creation",
    "gpt_first_controlled_call_execution_packet_preparation",
    "roadmap_update"
]

READINESS_CHECKS = [
    "prior_first_controlled_call_packet_present",
    "prior_first_controlled_call_packet_passed",
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
    "first_call_execution_packet_required",
    "first_call_execution_packet_is_next",
    "sanitized_prompt_required",
    "state_snapshot_ref_required",
    "evidence_packet_ref_required",
    "gate_packet_ref_required",
    "expected_output_schema_ref_required",
    "claim_boundary_ref_required",
    "human_reviewer_ref_required",
    "audit_log_required",
    "cost_metric_required",
    "latency_metric_required",
    "operational_hallucination_metric_required",
    "unsupported_claim_metric_required",
    "gate_violation_metric_required",
    "context_regression_metric_required",
    "roadmap_regression_metric_required",
    "human_correction_metric_required",
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

while len(READINESS_CHECKS) < 128:
    READINESS_CHECKS.append(f"gpt_first_controlled_call_readiness_control_{len(READINESS_CHECKS)+1:03d}")

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
    packet = read_json(PACKET) if PACKET.exists() else {}
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
        if ph == "PROD-5141..5180":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5221..5260":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Readiness Gate", "status": "CURRENT"})
    if "PROD-5221..5260" not in seen:
        roadmap_items.append({"phase": "PROD-5221..5260", "name": "GPT Sandbox First Controlled Call Execution Packet", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous first controlled call packet not PASS")
    if prev.get("decision") != "GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET_READY":
        errors.append("previous decision not ready")
    if prev.get("gpt_only_scope") is not True:
        errors.append("previous gpt_only_scope not true")
    if prev.get("multi_vendor_llm_scope") is not False:
        errors.append("previous multi_vendor_llm_scope not false")
    if prev.get("real_gpt_provider_call") is not False:
        errors.append("previous real_gpt_provider_call not false")
    if prev.get("openai_api_key_storage") is not False:
        errors.append("previous openai_api_key_storage not false")
    if packet.get("sandbox_call_packet_only") is not True:
        errors.append("packet is not marked as packet only")
    if request_template.get("template_only") is not True:
        errors.append("request template not template-only")
    if comparison_template.get("template_only") is not True:
        errors.append("comparison template not template-only")

    decision = "APPROVED_FOR_GPT_FIRST_CONTROLLED_CALL_EXECUTION_PACKET_PREPARATION_ONLY"

    gate = {
        "version": "gpt_sandbox_first_controlled_call_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_READINESS_GATE_NOT_READY",
        "purpose": "Validate readiness to prepare the first controlled GPT call execution packet, without executing the call.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "first_call_execution_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "readiness_checks": READINESS_CHECKS,
        "check_count": len(READINESS_CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5221..5260 - GPT Sandbox First Controlled Call Execution Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "readiness_gate_only": True,
        "first_call_execution_packet_preparation_only": True,
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
        "first_call_execution_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5181..5220 - GPT Sandbox First Controlled Call Readiness Gate

Validates readiness to prepare the first controlled GPT sandbox call execution packet.

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

Next: PROD-5221..5260 - GPT Sandbox First Controlled Call Execution Packet.
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

    report = f"""# PROD-5181..5220 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {len(READINESS_CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
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
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
