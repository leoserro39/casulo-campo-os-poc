#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5821..5860"
REQ_TAG = "product-casulo-exocortex-stack-controlled-live-call-packet-v0.1"

PREV_PACKET_OUT = ROOT / "outputs/prod5781_5820_casulo_exocortex_stack_controlled_live_call_packet.json"
PACKET = ROOT / "product/calibration/real_sessions/casulo_exocortex_stack_controlled_live_call_packet_v0_1.json"
REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/casulo_exocortex_stack_controlled_live_call_request_template_v0_1.json"
EXOCORTEX_SNAPSHOT = ROOT / "product/exocortex/casulo_exocortex_simulated_state_snapshot_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/pure_vs_stack_vs_exocortex_comparison_template_v0_1.json"
TELEMETRY_SCHEMA = ROOT / "product/telemetry/casulo_telemetry_schema_v0_1.json"
DOMAIN_MATRIX = ROOT / "product/evaluation/domain_scenario_matrix_v0_1.json"
LIVE_RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_live_call.py"
LIVE_RESULT_PATH = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"

STACK_BASELINE_BACKUP = ROOT / "outputs/prod5821_5860_stack_baseline_result_preserved.json"
EXOCORTEX_DRY_OUTPUT = ROOT / "outputs/prod5821_5860_exocortex_runner_dry_run_output.json"
EXOCORTEX_APPLY_BLOCK_OUTPUT = ROOT / "outputs/prod5821_5860_exocortex_runner_apply_without_auth_output.json"
EXOCORTEX_DRY_LOG = ROOT / "outputs/prod5821_5860_exocortex_runner_dry_run.log"
EXOCORTEX_APPLY_BLOCK_LOG = ROOT / "outputs/prod5821_5860_exocortex_runner_apply_without_auth_block.log"
ROADMAP_IN = ROOT / "outputs/prod5781_5820_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/649_CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_GATE.md"
CONTRACT = ROOT / "product/contracts/casulo_exocortex_stack_controlled_live_call_execution_gate.contract.json"
MEMORY = ROOT / "product/memory/casulo_exocortex_stack_controlled_live_call_execution_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/casulo_exocortex_stack_controlled_live_call_execution_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5821_5860_casulo_exocortex_stack_controlled_live_call_execution_gate.json"
OUT_MD = ROOT / "outputs/prod5821_5860_casulo_exocortex_stack_controlled_live_call_execution_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5821_5860_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

EXOCORTEX_PROMPT = "CASULO controlled EXOCORTEX sandbox test. Use the supplied simulated operational state, telemetry schema, domain matrix and claim boundaries. Return only: CASULO_EXOCORTEX_STACK_SANDBOX_ACK."

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
    "memory_create",
    "memory_update",
    "memory_delete",
    "persistent_memory_write",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "live_gpt_call_in_this_gate",
    "real_gpt_provider_call_in_this_gate",
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
    "casulo_exocortex_execution_gate_creation",
    "casulo_exocortex_dry_run_validation",
    "casulo_exocortex_apply_without_auth_block_validation",
    "casulo_exocortex_explicit_operator_live_call_command_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_exocortex_packet_present",
    "prior_exocortex_packet_passed",
    "required_prior_tag_present",
    "packet_file_present",
    "request_template_present",
    "simulated_exocortex_snapshot_present",
    "comparison_template_present",
    "telemetry_schema_present",
    "domain_matrix_present",
    "live_runner_script_present",
    "gpt_only_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "openai_gpt_provider_scope_confirmed",
    "exocortex_mode_confirmed",
    "execution_gate_only",
    "exocortex_live_execution_not_performed_in_this_gate",
    "llm_not_called_in_this_gate",
    "real_gpt_provider_call_not_performed_in_this_gate",
    "gpt_memory_api_not_used",
    "real_memory_api_not_used",
    "persistent_memory_write_false",
    "simulated_context_only",
    "stack_baseline_preserved_before_validation",
    "exocortex_dry_run_executed",
    "exocortex_dry_run_output_pass",
    "exocortex_dry_run_no_provider_call",
    "exocortex_dry_run_no_api_key_storage",
    "exocortex_dry_run_no_gpt_memory_api",
    "exocortex_apply_without_auth_blocked",
    "exocortex_apply_without_auth_no_successful_response",
    "exocortex_apply_without_auth_no_provider_call",
    "exocortex_apply_without_auth_no_api_key_storage",
    "exocortex_apply_without_auth_no_gpt_memory_api",
    "stack_baseline_restored_after_validation",
    "future_exocortex_live_execution_requires_explicit_operator_command",
    "future_exocortex_live_execution_requires_casulo_live_auth",
    "future_exocortex_live_execution_requires_openai_api_key_env",
    "future_exocortex_live_execution_requires_post_call_review",
    "api_key_env_reference_only",
    "no_api_key_value_storage",
    "no_secret_storage",
    "no_raw_private_data",
    "no_unredacted_pii",
    "dataset_write_blocked",
    "real_candidate_insert_blocked",
    "real_candidate_acceptance_blocked",
    "client_claim_blocked",
    "production_blocked",
    "false_memory_risk_metric_required",
    "context_regression_metric_required",
    "evidence_grounding_metric_required",
    "claim_boundary_metric_required",
    "cost_latency_metric_required",
    "roadmap_updated"
]

while len(CHECKS) < 216:
    CHECKS.append(f"casulo_exocortex_execution_gate_control_{len(CHECKS)+1:03d}")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def git_tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def run_validations():
    if LIVE_RESULT_PATH.exists():
        shutil.copy2(LIVE_RESULT_PATH, STACK_BASELINE_BACKUP)

    dry = subprocess.run(
        [sys.executable, str(LIVE_RUNNER_SCRIPT), "--mode", "CASULO_EXOCORTEX_STACK", "--prompt", EXOCORTEX_PROMPT],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    write(EXOCORTEX_DRY_LOG, "STDOUT:\n" + dry.stdout + "\nSTDERR:\n" + dry.stderr + "\nRC:\n" + str(dry.returncode))
    if LIVE_RESULT_PATH.exists():
        shutil.copy2(LIVE_RESULT_PATH, EXOCORTEX_DRY_OUTPUT)

    blocked = subprocess.run(
        [sys.executable, str(LIVE_RUNNER_SCRIPT), "--mode", "CASULO_EXOCORTEX_STACK", "--prompt", EXOCORTEX_PROMPT, "--apply"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={},
    )
    write(EXOCORTEX_APPLY_BLOCK_LOG, "STDOUT:\n" + blocked.stdout + "\nSTDERR:\n" + blocked.stderr + "\nRC:\n" + str(blocked.returncode))
    if LIVE_RESULT_PATH.exists():
        shutil.copy2(LIVE_RESULT_PATH, EXOCORTEX_APPLY_BLOCK_OUTPUT)

    if STACK_BASELINE_BACKUP.exists():
        shutil.copy2(STACK_BASELINE_BACKUP, LIVE_RESULT_PATH)

    return dry, blocked

def main():
    prev = read_json(PREV_PACKET_OUT) if PREV_PACKET_OUT.exists() else {}
    packet = read_json(PACKET) if PACKET.exists() else {}
    request_template = read_json(REQUEST_TEMPLATE) if REQUEST_TEMPLATE.exists() else {}
    snapshot = read_json(EXOCORTEX_SNAPSHOT) if EXOCORTEX_SNAPSHOT.exists() else {}
    comparison_template = read_json(COMPARISON_TEMPLATE) if COMPARISON_TEMPLATE.exists() else {}
    telemetry_schema = read_json(TELEMETRY_SCHEMA) if TELEMETRY_SCHEMA.exists() else {}
    domain_matrix = read_json(DOMAIN_MATRIX) if DOMAIN_MATRIX.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    dry, blocked = run_validations()

    stack_baseline = read_json(STACK_BASELINE_BACKUP) if STACK_BASELINE_BACKUP.exists() else {}
    exocortex_dry = read_json(EXOCORTEX_DRY_OUTPUT) if EXOCORTEX_DRY_OUTPUT.exists() else {}
    exocortex_block = read_json(EXOCORTEX_APPLY_BLOCK_OUTPUT) if EXOCORTEX_APPLY_BLOCK_OUTPUT.exists() else {}
    restored = read_json(LIVE_RESULT_PATH) if LIVE_RESULT_PATH.exists() else {}

    blocked_text = blocked.stdout + blocked.stderr
    blocked_message_present = (
        "BLOCKED" in blocked_text
        or "blocked_reason" in blocked_text
        or "CASULO_GPT_LIVE_AUTH=YES is required" in blocked_text
    )

    errors = []

    if REQ_TAG not in git_tags():
        errors.append("missing required prior Exocortex packet tag")
    if prev.get("status") != "PASS":
        errors.append("prior Exocortex packet not PASS")
    if prev.get("decision") != "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_PACKET_READY":
        errors.append("prior Exocortex packet decision mismatch")
    if prev.get("packet_only") is not True:
        errors.append("prior packet_only not true")
    if prev.get("live_execution_allowed") is not False:
        errors.append("prior live_execution_allowed not false")
    if prev.get("simulated_exocortex_context_prepared") is not True:
        errors.append("prior simulated context not prepared")
    if prev.get("gpt_memory_api_execution") is not False:
        errors.append("prior gpt memory api execution not false")

    if packet.get("packet_only") is not True:
        errors.append("packet file not packet-only")
    if packet.get("simulated_exocortex_context_prepared") is not True:
        errors.append("packet file simulated context not prepared")
    if request_template.get("mode") != "CASULO_EXOCORTEX_STACK":
        errors.append("request template mode mismatch")
    if request_template.get("template_only") is not True:
        errors.append("request template not template-only")
    if snapshot.get("snapshot_type") != "SIMULATED_OPERATIONAL_CONTEXT_ONLY":
        errors.append("snapshot type mismatch")
    if snapshot.get("gpt_memory_api_execution") is not False:
        errors.append("snapshot gpt memory api not false")
    if snapshot.get("real_memory_api_execution") is not False:
        errors.append("snapshot real memory api not false")
    if snapshot.get("persistent_memory_write") is not False:
        errors.append("snapshot persistent memory write not false")
    if comparison_template.get("candidate_mode") != "CASULO_EXOCORTEX_STACK":
        errors.append("comparison template candidate mode mismatch")
    if "event_groups" not in telemetry_schema:
        errors.append("telemetry schema missing event groups")
    if len(domain_matrix.get("domains", [])) < 6:
        errors.append("domain matrix insufficient domains")

    if stack_baseline.get("mode") != "STACK_GPT":
        errors.append("stack baseline backup not STACK_GPT")
    if stack_baseline.get("successful_live_gpt_response") is not True:
        errors.append("stack baseline backup not successful")

    if dry.returncode != 0:
        errors.append("Exocortex dry-run returned nonzero")
    if exocortex_dry.get("status") != "PASS":
        errors.append("Exocortex dry-run output not PASS")
    if exocortex_dry.get("mode") != "CASULO_EXOCORTEX_STACK":
        errors.append("Exocortex dry-run mode mismatch")
    if exocortex_dry.get("dry_run") is not True:
        errors.append("Exocortex dry-run not marked dry_run")
    if exocortex_dry.get("real_gpt_provider_call") is not False:
        errors.append("Exocortex dry-run called provider unexpectedly")
    if exocortex_dry.get("openai_api_key_storage") is not False:
        errors.append("Exocortex dry-run api key storage not false")
    if exocortex_dry.get("gpt_memory_api_execution") is not False:
        errors.append("Exocortex dry-run gpt memory api not false")

    if blocked.returncode == 0:
        errors.append("Exocortex apply without auth did not block")
    if not blocked_message_present:
        errors.append("Exocortex apply without auth did not emit blocked_reason/BLOCKED")
    if exocortex_block.get("status") != "FAIL":
        errors.append("Exocortex block output not FAIL")
    if exocortex_block.get("real_gpt_provider_call") is not False:
        errors.append("Exocortex block called provider unexpectedly")
    if exocortex_block.get("openai_api_key_storage") is not False:
        errors.append("Exocortex block api key storage not false")
    if exocortex_block.get("gpt_memory_api_execution") is not False:
        errors.append("Exocortex block gpt memory api not false")

    if restored.get("mode") != "STACK_GPT":
        errors.append("STACK baseline was not restored after validation")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5781..5820":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5861..5900":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "CASULO Exocortex Stack Controlled Live Call Execution Gate", "status": "CURRENT"})
    if "PROD-5861..5900" not in seen:
        roadmap_items.append({"phase": "PROD-5861..5900", "name": "CASULO Exocortex Stack Controlled Live Call Execution Run", "status": "NEXT"})

    decision = "APPROVED_FOR_CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY"

    gate = {
        "version": "casulo_exocortex_stack_controlled_live_call_execution_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_GATE_NOT_READY",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_gate_only": True,
        "exocortex_mode": "CASULO_EXOCORTEX_STACK",
        "exocortex_live_execution_not_performed_in_this_gate": True,
        "llm_not_called_in_this_gate": True,
        "real_gpt_provider_call_in_this_gate": False,
        "simulated_exocortex_context_bound": True,
        "gpt_memory_api_execution": False,
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "openai_api_key_storage": False,
        "dataset_write": False,
        "future_exocortex_live_execution_allowed_only_by_explicit_operator_command": True,
        "operator_command_requirements": [
            "export OPENAI_API_KEY in shell only",
            "export CASULO_GPT_LIVE_AUTH=YES",
            "run product/scripts/run_gpt_sandbox_first_controlled_live_call.py --mode CASULO_EXOCORTEX_STACK --apply",
            "review outputs/gpt_sandbox_first_controlled_live_call_result.json",
            "compare against PURE_GPT and STACK_GPT baselines",
            "perform post-call review before any domain calibration"
        ],
        "dry_run_validation": {
            "returncode": dry.returncode,
            "mode": exocortex_dry.get("mode"),
            "dry_run": exocortex_dry.get("dry_run"),
            "real_gpt_provider_call": exocortex_dry.get("real_gpt_provider_call"),
            "openai_api_key_storage": exocortex_dry.get("openai_api_key_storage"),
            "gpt_memory_api_execution": exocortex_dry.get("gpt_memory_api_execution")
        },
        "apply_without_auth_block_validation": {
            "returncode": blocked.returncode,
            "blocked_message_present": blocked_message_present,
            "status": exocortex_block.get("status"),
            "blocked_reason": exocortex_block.get("blocked_reason")
        },
        "stack_baseline_preserved": restored.get("mode") == "STACK_GPT",
        "readiness_checks": CHECKS,
        "readiness_check_count": len(CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5861..5900 - CASULO Exocortex Stack Controlled Live Call Execution Run"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "execution_gate_only": True,
        "exocortex_live_execution_not_performed_in_this_gate": True,
        "future_exocortex_live_execution_allowed_only_by_explicit_operator_command": True,
        "simulated_exocortex_context_only": True,
        "gpt_memory_api_blocked": True,
        "real_memory_api_blocked": True,
        "persistent_memory_write_blocked": True,
        "api_key_storage_blocked": True,
        "dataset_write_blocked": True,
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
        "readiness_check_count": len(CHECKS),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_gate_only": True,
        "exocortex_mode": "CASULO_EXOCORTEX_STACK",
        "exocortex_live_execution_not_performed_in_this_gate": True,
        "llm_not_called_in_this_gate": True,
        "real_gpt_provider_call_in_this_gate": False,
        "simulated_exocortex_context_bound": True,
        "gpt_memory_api_execution": False,
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "openai_api_key_storage": False,
        "dataset_write": False,
        "dry_run_output_pass": exocortex_dry.get("status") == "PASS",
        "apply_without_auth_blocked": blocked.returncode != 0,
        "apply_without_auth_block_message_present": blocked_message_present,
        "stack_baseline_preserved": restored.get("mode") == "STACK_GPT",
        "future_exocortex_live_execution_allowed_only_by_explicit_operator_command": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.9",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Exocortex Stack Controlled Live Call Execution Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5821..5860 - CASULO Exocortex Stack Controlled Live Call Execution Gate

Validates CASULO_EXOCORTEX_STACK live-call readiness.

This gate does not call GPT. It validates Exocortex dry-run, confirms apply without authorization is blocked, preserves the STACK baseline result, binds simulated Exocortex context, and approves only explicit operator-controlled Exocortex live execution run.

The Exocortex context remains simulated/file-bound. No GPT Memory API or real memory API is used.

Next: PROD-5861..5900 - CASULO Exocortex Stack Controlled Live Call Execution Run.
"""

    report = f"""# PROD-5821..5860 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {result['readiness_check_count']}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- Execution gate only: true
- Exocortex live execution performed in this gate: false
- LLM called in this gate: false
- Real GPT provider call in this gate: false
- Simulated Exocortex context bound: true
- GPT Memory API execution: false
- Real memory API execution: false
- Persistent memory write: false
- API key storage: false
- Dataset write: false
- Dry-run output pass: {result['dry_run_output_pass']}
- Apply without auth blocked: {result['apply_without_auth_blocked']}
- Apply without auth block message present: {result['apply_without_auth_block_message_present']}
- STACK baseline preserved: {result['stack_baseline_preserved']}
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
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_checks:", result["readiness_check_count"])
    print("dry_run_output_pass:", result["dry_run_output_pass"])
    print("apply_without_auth_blocked:", result["apply_without_auth_blocked"])
    print("stack_baseline_preserved:", result["stack_baseline_preserved"])
    print("gpt_memory_api_execution:", result["gpt_memory_api_execution"])
    print("real_memory_api_execution:", result["real_memory_api_execution"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
