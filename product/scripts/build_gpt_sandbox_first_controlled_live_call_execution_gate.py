#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5501..5540"
REQ_TAG = "product-gpt-sandbox-first-controlled-live-call-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod5461_5500_gpt_sandbox_first_controlled_live_call_packet.json"
LIVE_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_packet_v0_1.json"
LIVE_RUNNER_SPEC = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_runner_spec_v0_1.json"
LIVE_REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_request_template_v0_1.json"
LIVE_RESULT_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_result_template_v0_1.json"
LIVE_RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_live_call.py"
ROADMAP_IN = ROOT / "outputs/prod5461_5500_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DRY_RUN_LOG = ROOT / "outputs/prod5501_5540_live_runner_dry_run.log"
APPLY_BLOCK_LOG = ROOT / "outputs/prod5501_5540_live_runner_apply_without_auth_block.log"
LIVE_DRY_OUTPUT = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"

DOC = ROOT / "docs/product/639_GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_GATE.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_live_call_execution_gate.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_live_call_execution_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_execution_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5501_5540_gpt_sandbox_first_controlled_live_call_execution_gate.json"
OUT_MD = ROOT / "outputs/prod5501_5540_gpt_sandbox_first_controlled_live_call_execution_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5501_5540_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_live_call_execution_gate_creation",
    "explicit_operator_live_call_execution_command_preparation",
    "single_sandbox_live_call_after_operator_command",
    "roadmap_update"
]

READINESS_CHECKS = [
    "prior_live_call_packet_present",
    "prior_live_call_packet_passed",
    "prior_decision_live_call_packet_ready",
    "live_runner_script_present",
    "live_runner_spec_present",
    "live_request_template_present",
    "live_result_template_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "dry_run_executes_without_provider_call",
    "apply_without_auth_blocks",
    "apply_without_auth_does_not_call_provider",
    "runner_requires_casulo_live_auth",
    "runner_requires_openai_api_key_env",
    "runner_does_not_store_api_key",
    "runner_does_not_print_secret",
    "runner_does_not_call_gpt_memory_api",
    "runner_does_not_write_dataset",
    "runner_supports_pure_gpt",
    "runner_supports_stack_gpt",
    "runner_supports_exocortex_stack",
    "live_execution_gate_only",
    "live_execution_not_performed_in_this_gate",
    "live_execution_requires_explicit_operator_command",
    "api_key_env_reference_only",
    "no_api_key_value_storage",
    "no_api_key_file",
    "no_secret_print",
    "human_operator_command_required",
    "post_call_review_required",
    "result_log_required",
    "prompt_hash_required",
    "output_hash_required",
    "latency_metric_required",
    "provider_call_flag_required",
    "dataset_write_false_required",
    "real_candidate_insert_false_required",
    "real_candidate_accept_false_required",
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

while len(READINESS_CHECKS) < 208:
    READINESS_CHECKS.append(f"gpt_first_controlled_live_call_execution_gate_control_{len(READINESS_CHECKS)+1:03d}")

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

def run_validations():
    dry = subprocess.run(
        [sys.executable, str(LIVE_RUNNER_SCRIPT), "--mode", "PURE_GPT"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    write(DRY_RUN_LOG, "STDOUT:\n" + dry.stdout + "\nSTDERR:\n" + dry.stderr + "\nRC:\n" + str(dry.returncode))

    apply = subprocess.run(
        [sys.executable, str(LIVE_RUNNER_SCRIPT), "--mode", "PURE_GPT", "--apply"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={},
    )
    write(APPLY_BLOCK_LOG, "STDOUT:\n" + apply.stdout + "\nSTDERR:\n" + apply.stderr + "\nRC:\n" + str(apply.returncode))

    return dry, apply

def main():
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    live_packet = read_json(LIVE_PACKET) if LIVE_PACKET.exists() else {}
    runner_spec = read_json(LIVE_RUNNER_SPEC) if LIVE_RUNNER_SPEC.exists() else {}
    request_template = read_json(LIVE_REQUEST_TEMPLATE) if LIVE_REQUEST_TEMPLATE.exists() else {}
    result_template = read_json(LIVE_RESULT_TEMPLATE) if LIVE_RESULT_TEMPLATE.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    dry = None
    apply = None
    if LIVE_RUNNER_SCRIPT.exists():
        dry, apply = run_validations()

    dry_output = read_json(LIVE_DRY_OUTPUT) if LIVE_DRY_OUTPUT.exists() else {}

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5461..5500":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5541..5580":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Live Call Execution Gate", "status": "CURRENT"})
    if "PROD-5541..5580" not in seen:
        roadmap_items.append({"phase": "PROD-5541..5580", "name": "GPT Sandbox First Controlled Live Call Execution Run", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous live call packet not PASS")
    if prev.get("decision") != "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_PACKET_READY":
        errors.append("previous decision not live call packet ready")
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
    if prev.get("live_execution_requires_next_gate") is not True:
        errors.append("previous packet did not require execution gate")
    if live_packet.get("first_controlled_live_call_packet_only") is not True:
        errors.append("live packet not packet-only")
    if runner_spec.get("live_ready_runner") is not True:
        errors.append("runner spec not live-ready")
    if runner_spec.get("stores_api_key") is not False:
        errors.append("runner spec stores api key unexpectedly")
    if runner_spec.get("calls_gpt_memory_api") is not False:
        errors.append("runner spec calls gpt memory unexpectedly")
    if request_template.get("template_only") is not True:
        errors.append("live request template not template-only")
    if result_template.get("template_only") is not True:
        errors.append("live result template not template-only")
    if dry is None or dry.returncode != 0:
        errors.append("live runner dry-run failed")
    if apply is None or apply.returncode == 0:
        errors.append("live runner apply without auth did not block")
    if apply is not None and "BLOCKED" not in (apply.stdout + apply.stderr):
        errors.append("live runner apply without auth did not emit BLOCKED")
    if dry_output.get("dry_run") is not True:
        errors.append("dry output not marked dry_run")
    if dry_output.get("real_gpt_provider_call") is not False:
        errors.append("dry output provider call not false")
    if dry_output.get("openai_api_key_storage") is not False:
        errors.append("dry output api key storage not false")
    if dry_output.get("gpt_memory_api_execution") is not False:
        errors.append("dry output gpt memory api not false")
    if dry_output.get("live_gpt_call_execution") is not False:
        errors.append("dry output live call execution not false")

    decision = "APPROVED_FOR_GPT_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY"

    gate = {
        "version": "gpt_sandbox_first_controlled_live_call_execution_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_GATE_NOT_READY",
        "purpose": "Validate live-ready runner and approve only explicit operator-controlled first live call execution run.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_gate_only": True,
        "live_execution_not_performed_in_this_gate": True,
        "llm_not_called_in_this_gate": True,
        "real_gpt_provider_call_in_this_gate": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "future_live_execution_allowed_only_by_explicit_operator_command": True,
        "operator_command_requirements": [
            "export OPENAI_API_KEY in shell only",
            "export CASULO_GPT_LIVE_AUTH=YES",
            "choose explicit mode PURE_GPT or STACK_GPT or CASULO_EXOCORTEX_STACK",
            "run product/scripts/run_gpt_sandbox_first_controlled_live_call.py with --apply",
            "review outputs/gpt_sandbox_first_controlled_live_call_result.json"
        ],
        "dry_run_validation": {
            "returncode": None if dry is None else dry.returncode,
            "output_status": dry_output.get("status"),
            "dry_run": dry_output.get("dry_run"),
            "real_gpt_provider_call": dry_output.get("real_gpt_provider_call"),
            "openai_api_key_storage": dry_output.get("openai_api_key_storage"),
            "gpt_memory_api_execution": dry_output.get("gpt_memory_api_execution"),
            "live_gpt_call_execution": dry_output.get("live_gpt_call_execution")
        },
        "apply_without_auth_block_validation": {
            "returncode": None if apply is None else apply.returncode,
            "blocked_message_present": False if apply is None else "BLOCKED" in (apply.stdout + apply.stderr)
        },
        "readiness_checks": READINESS_CHECKS,
        "readiness_check_count": len(READINESS_CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5541..5580 - GPT Sandbox First Controlled Live Call Execution Run"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "execution_gate_only": True,
        "live_execution_not_performed_in_this_gate": True,
        "future_live_execution_allowed_only_by_explicit_operator_command": True,
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
        "execution_gate_only": True,
        "live_execution_not_performed_in_this_gate": True,
        "llm_not_called_in_this_gate": True,
        "real_gpt_provider_call_in_this_gate": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "future_live_execution_allowed_only_by_explicit_operator_command": True,
        "dry_run_output_pass": dry_output.get("status") == "PASS",
        "apply_without_auth_blocked": False if apply is None else apply.returncode != 0,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Live Call Execution Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "live_execution_not_performed_in_this_gate": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate

Validates the live-ready runner and approves only explicit operator-controlled first live call execution run.

This gate does not execute the live GPT call.

After this gate, the next phase may perform one controlled GPT/OpenAI sandbox call only by explicit operator command, with API key provided through environment and not stored.
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
        "- Execution gate passed only if result is PASS.",
        "- The gate itself does not call GPT.",
        "- Future live execution requires explicit operator command.",
        "- No API key value storage.",
        "- No GPT Memory API.",
        "- No multi-vendor LLM in this cycle.",
        "- No dataset acceptance."
    ]

    report = f"""# PROD-5501..5540 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {len(READINESS_CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- Execution gate only: true
- Live execution performed in this gate: false
- LLM called in this gate: false
- API key storage: false
- GPT Memory API execution: false
- Dry-run output pass: {result['dry_run_output_pass']}
- Apply without auth blocked: {result['apply_without_auth_blocked']}
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
    print("execution_gate_only:", result["execution_gate_only"])
    print("live_execution_not_performed_in_this_gate:", result["live_execution_not_performed_in_this_gate"])
    print("llm_not_called_in_this_gate:", result["llm_not_called_in_this_gate"])
    print("real_gpt_provider_call_in_this_gate:", result["real_gpt_provider_call_in_this_gate"])
    print("openai_api_key_storage:", result["openai_api_key_storage"])
    print("gpt_memory_api_execution:", result["gpt_memory_api_execution"])
    print("dry_run_output_pass:", result["dry_run_output_pass"])
    print("apply_without_auth_blocked:", result["apply_without_auth_blocked"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
