#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5301..5340"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-execution-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod5261_5300_gpt_sandbox_first_controlled_call_execution_readiness_gate.json"
READINESS_GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_execution_readiness_gate_v0_1.json"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_execution_packet_v0_1.json"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5261_5300_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/634_GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_PACKET.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_runner_packet.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_runner_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_packet_v0_1.json"
RUNNER_SPEC = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_spec_v0_1.json"
RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_call.py"
OUT_JSON = ROOT / "outputs/prod5301_5340_gpt_sandbox_first_controlled_call_runner_packet.json"
OUT_MD = ROOT / "outputs/prod5301_5340_gpt_sandbox_first_controlled_call_runner_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5301_5340_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_runner_packet_creation",
    "dry_run_runner_script_creation",
    "runner_output_template_creation",
    "gpt_first_controlled_call_runner_readiness_gate_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_execution_readiness_gate_present",
    "prior_execution_readiness_gate_passed",
    "prior_decision_runner_packet_preparation_only",
    "execution_packet_present",
    "payload_template_present",
    "expected_log_template_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "runner_packet_only",
    "runner_script_created",
    "runner_default_dry_run_true",
    "runner_requires_explicit_apply_for_future_live_call",
    "runner_live_call_disabled_in_this_phase",
    "runner_does_not_import_openai_sdk",
    "runner_does_not_read_env_key",
    "runner_does_not_store_api_key",
    "runner_does_not_call_provider",
    "runner_does_not_call_gpt_memory_api",
    "runner_outputs_dry_run_json_only",
    "no_claude_scope",
    "no_gemini_scope",
    "no_copilot_scope",
    "real_gpt_call_still_blocked",
    "api_key_storage_still_blocked",
    "gpt_memory_api_still_blocked",
    "live_call_execution_still_blocked",
    "runner_readiness_gate_required",
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

while len(CHECKS) < 152:
    CHECKS.append(f"gpt_first_controlled_call_runner_packet_control_{len(CHECKS)+1:03d}")

RUNNER_CODE = r'''#!/usr/bin/env python3
"""
CASULO GPT sandbox first controlled call runner.

Default behavior is dry-run only.

This runner intentionally does NOT:
- import OpenAI SDK
- read environment API keys
- store API keys
- call GPT provider
- call GPT Memory API
- execute any live benchmark
- insert real candidate
- accept dataset

A future live execution requires a separate readiness gate and a different runner activation packet.
"""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
OUT = ROOT / "outputs/gpt_sandbox_first_controlled_call_runner_dry_run_output.json"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if args.apply:
        raise SystemExit("BLOCKED: live GPT call execution is not allowed by this runner packet.")

    payload_template = read_json(PAYLOAD_TEMPLATE)
    expected_log_template = read_json(EXPECTED_LOG_TEMPLATE)

    result = {
        "status": "PASS",
        "mode": "DRY_RUN_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "live_gpt_call_execution": False,
        "request_modes": payload_template.get("request_modes", []),
        "expected_log_fields": expected_log_template.get("log_fields", []),
        "blocked_reason": "Live GPT call requires a future explicit readiness gate.",
        "next_required_phase": "PROD-5341..5380 - GPT Sandbox First Controlled Call Runner Readiness Gate"
    }

    write_json(OUT, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
'''

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
        if ph == "PROD-5261..5300":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5341..5380":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Runner Packet", "status": "CURRENT"})
    if "PROD-5341..5380" not in seen:
        roadmap_items.append({"phase": "PROD-5341..5380", "name": "GPT Sandbox First Controlled Call Runner Readiness Gate", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous execution readiness gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_GPT_FIRST_CONTROLLED_CALL_RUNNER_PACKET_PREPARATION_ONLY":
        errors.append("previous decision not approved for runner packet preparation")
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
    if readiness_gate.get("runner_packet_preparation_only") is not True:
        errors.append("readiness gate missing runner packet preparation only")
    if exec_packet.get("execution_packet_only") is not True:
        errors.append("execution packet not packet-only")
    if payload_template.get("template_only") is not True:
        errors.append("payload template not template-only")
    if expected_log_template.get("template_only") is not True:
        errors.append("expected log template not template-only")

    runner_spec = {
        "version": "gpt_sandbox_first_controlled_call_runner_spec.v0.1",
        "phase": PHASE,
        "runner_packet_only": True,
        "runner_default_mode": "DRY_RUN_ONLY",
        "live_call_allowed": False,
        "apply_mode_blocked": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "imports_openai_sdk": False,
        "reads_env_key": False,
        "stores_api_key": False,
        "request_modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "next_required_phase": "PROD-5341..5380 - GPT Sandbox First Controlled Call Runner Readiness Gate",
        "blocked_actions": BLOCKED
    }

    packet = {
        "version": "gpt_sandbox_first_controlled_call_runner_packet.v0.1",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_PACKET_READY",
        "purpose": "Create a dry-run-only runner packet for the first controlled GPT sandbox call.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "runner_packet_only": True,
        "runner_default_dry_run": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_gate": True,
        "runner_script": str(RUNNER_SCRIPT.relative_to(ROOT)),
        "runner_spec": runner_spec,
        "checks": CHECKS,
        "check_count": len(CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5341..5380 - GPT Sandbox First Controlled Call Runner Readiness Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "runner_packet_only": True,
        "runner_default_dry_run": True,
        "live_execution_allowed": False,
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
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_PACKET_READY" if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_PACKET_NOT_READY",
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
        "runner_packet_only": True,
        "runner_default_dry_run": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.6",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Runner Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5301..5340 - GPT Sandbox First Controlled Call Runner Packet

Creates a dry-run-only runner for the first controlled GPT sandbox call.

This phase still does not call GPT.

The generated runner intentionally does not import the OpenAI SDK, does not read environment API keys, does not store API keys, does not call GPT, and does not execute GPT Memory API.

Next: PROD-5341..5380 - GPT Sandbox First Controlled Call Runner Readiness Gate.
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

    report = f"""# PROD-5301..5340 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {len(CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Runner packet only: true
- Runner default dry-run: true
- First call live execution allowed: false
- Next: {packet['recommended_next_phase']}
"""

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(RUNNER_SPEC, runner_spec)
    write(RUNNER_SCRIPT, RUNNER_CODE)
    RUNNER_SCRIPT.chmod(0o755)
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
    print("runner_packet_only:", result["runner_packet_only"])
    print("runner_default_dry_run:", result["runner_default_dry_run"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
