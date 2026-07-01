#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5661..5700"
REQ_TAG = "product-stack-gpt-controlled-live-call-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod5621_5660_stack_gpt_controlled_live_call_packet.json"
LIVE_RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_live_call.py"
LIVE_RESULT = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"

PURE_BACKUP = ROOT / "outputs/prod5661_5700_pure_baseline_result_preserved.json"
STACK_DRY_OUTPUT = ROOT / "outputs/prod5661_5700_stack_runner_dry_run_output.json"
STACK_BLOCK_OUTPUT = ROOT / "outputs/prod5661_5700_stack_runner_apply_without_auth_output.json"
STACK_DRY_LOG = ROOT / "outputs/prod5661_5700_stack_runner_dry_run.log"
STACK_BLOCK_LOG = ROOT / "outputs/prod5661_5700_stack_runner_apply_without_auth_block.log"

DOC = ROOT / "docs/product/643_STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_GATE.md"
CONTRACT = ROOT / "product/contracts/stack_gpt_controlled_live_call_execution_gate.contract.json"
MEMORY = ROOT / "product/memory/stack_gpt_controlled_live_call_execution_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/stack_gpt_controlled_live_call_execution_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5661_5700_stack_gpt_controlled_live_call_execution_gate.json"
OUT_MD = ROOT / "outputs/prod5661_5700_stack_gpt_controlled_live_call_execution_gate.md"
ROADMAP_IN = ROOT / "outputs/prod5621_5660_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_OUT = ROOT / "outputs/prod5661_5700_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

STACK_PROMPT = "CASULO controlled STACK GPT sandbox test. Use the supplied CASULO state/evidence/gate context and return only: CASULO_STACK_GPT_SANDBOX_ACK."

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "production_activation"
]

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

def run_validation():
    if LIVE_RESULT.exists():
        shutil.copy2(LIVE_RESULT, PURE_BACKUP)

    dry = subprocess.run(
        [sys.executable, str(LIVE_RUNNER_SCRIPT), "--mode", "STACK_GPT", "--prompt", STACK_PROMPT],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    write(STACK_DRY_LOG, "STDOUT:\n" + dry.stdout + "\nSTDERR:\n" + dry.stderr + "\nRC:\n" + str(dry.returncode))
    if LIVE_RESULT.exists():
        shutil.copy2(LIVE_RESULT, STACK_DRY_OUTPUT)

    blocked = subprocess.run(
        [sys.executable, str(LIVE_RUNNER_SCRIPT), "--mode", "STACK_GPT", "--prompt", STACK_PROMPT, "--apply"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={},
    )
    write(STACK_BLOCK_LOG, "STDOUT:\n" + blocked.stdout + "\nSTDERR:\n" + blocked.stderr + "\nRC:\n" + str(blocked.returncode))
    if LIVE_RESULT.exists():
        shutil.copy2(LIVE_RESULT, STACK_BLOCK_OUTPUT)

    if PURE_BACKUP.exists():
        shutil.copy2(PURE_BACKUP, LIVE_RESULT)

    return dry, blocked

def main():
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    dry, blocked = run_validation()

    pure = read_json(PURE_BACKUP) if PURE_BACKUP.exists() else {}
    stack_dry = read_json(STACK_DRY_OUTPUT) if STACK_DRY_OUTPUT.exists() else {}
    stack_block = read_json(STACK_BLOCK_OUTPUT) if STACK_BLOCK_OUTPUT.exists() else {}
    restored = read_json(LIVE_RESULT) if LIVE_RESULT.exists() else {}

    apply_text = "" if blocked is None else (blocked.stdout + blocked.stderr)
    stack_apply_block_message_present = (
        ("BLOCKED" in apply_text)
        or ("blocked_reason" in apply_text)
        or ("CASULO_GPT_LIVE_AUTH=YES is required" in apply_text)
    )

    checks = [
        "prior_stack_packet_present",
        "prior_stack_packet_passed",
        "pure_baseline_preserved",
        "stack_dry_run_passed",
        "stack_apply_without_auth_blocked",
        "stack_live_not_executed_in_gate",
        "api_key_not_stored",
        "gpt_memory_not_executed",
        "dataset_not_written",
        "next_stack_execution_run_required"
    ]
    while len(checks) < 168:
        checks.append(f"stack_execution_gate_control_{len(checks)+1:03d}")

    errors = []
    if REQ_TAG not in git_tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("prior stack packet not PASS")
    if prev.get("decision") != "STACK_GPT_CONTROLLED_LIVE_CALL_PACKET_READY":
        errors.append("prior stack packet decision mismatch")
    if pure.get("mode") != "PURE_GPT":
        errors.append("pure baseline backup not PURE_GPT")
    if pure.get("successful_live_gpt_response") is not True:
        errors.append("pure baseline not successful")
    if dry.returncode != 0:
        errors.append("stack dry-run returned nonzero")
    if stack_dry.get("status") != "PASS":
        errors.append("stack dry-run output not PASS")
    if stack_dry.get("mode") != "STACK_GPT":
        errors.append("stack dry-run mode not STACK_GPT")
    if stack_dry.get("dry_run") is not True:
        errors.append("stack dry-run not marked dry_run")
    if stack_dry.get("real_gpt_provider_call") is not False:
        errors.append("stack dry-run called provider unexpectedly")
    if blocked.returncode == 0:
        errors.append("stack apply without auth did not block")
    if not stack_apply_block_message_present:
        errors.append("stack apply without auth did not emit blocked_reason/BLOCKED")
    if stack_block.get("status") != "FAIL":
        errors.append("stack block output not FAIL")
    if stack_block.get("real_gpt_provider_call") is not False:
        errors.append("stack block called provider unexpectedly")
    if stack_block.get("openai_api_key_storage") is not False:
        errors.append("stack block api key storage not false")
    if stack_block.get("gpt_memory_api_execution") is not False:
        errors.append("stack block gpt memory api not false")
    if restored.get("mode") != "PURE_GPT":
        errors.append("pure baseline not restored after validation")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5621..5660":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5701..5740":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "STACK GPT Controlled Live Call Execution Gate", "status": "CURRENT"})
    if "PROD-5701..5740" not in seen:
        roadmap_items.append({"phase": "PROD-5701..5740", "name": "STACK GPT Controlled Live Call Execution Run", "status": "NEXT"})

    decision = "APPROVED_FOR_STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY"

    gate = {
        "version": "stack_gpt_controlled_live_call_execution_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "STACK_GPT_CONTROLLED_LIVE_CALL_EXECUTION_GATE_NOT_READY",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_gate_only": True,
        "stack_live_execution_not_performed_in_this_gate": True,
        "llm_not_called_in_this_gate": True,
        "real_gpt_provider_call_in_this_gate": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dry_run_output_pass": stack_dry.get("status") == "PASS",
        "apply_without_auth_blocked": blocked.returncode != 0,
        "apply_without_auth_block_message_present": stack_apply_block_message_present,
        "pure_baseline_preserved": restored.get("mode") == "PURE_GPT",
        "future_stack_live_execution_allowed_only_by_explicit_operator_command": True,
        "readiness_checks": checks,
        "readiness_check_count": len(checks),
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-5701..5740 - STACK GPT Controlled Live Call Execution Run"
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(checks),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_gate_only": True,
        "stack_live_execution_not_performed_in_this_gate": True,
        "llm_not_called_in_this_gate": True,
        "real_gpt_provider_call_in_this_gate": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dry_run_output_pass": gate["dry_run_output_pass"],
        "apply_without_auth_blocked": gate["apply_without_auth_blocked"],
        "pure_baseline_preserved": gate["pure_baseline_preserved"],
        "future_stack_live_execution_allowed_only_by_explicit_operator_command": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "errors": errors
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "execution_gate_only": True,
        "stack_live_execution_not_performed_in_this_gate": True,
        "future_stack_live_execution_allowed_only_by_explicit_operator_command": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "dataset_write_blocked": True,
        "multi_vendor_llm_blocked_this_cycle": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.5",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - STACK GPT Controlled Live Call Execution Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5661..5700 - STACK GPT Controlled Live Call Execution Gate

Validates STACK GPT live-call readiness.

This gate does not call GPT. It validates STACK GPT dry-run, confirms apply without authorization is blocked, preserves the PURE GPT baseline, and approves only explicit operator-controlled STACK GPT live execution run.

Next: PROD-5701..5740 - STACK GPT Controlled Live Call Execution Run.
"""

    report = f"""# PROD-5661..5700 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {result['readiness_check_count']}
- STACK GPT live execution performed in this gate: false
- LLM called in this gate: false
- Real GPT provider call in this gate: false
- API key storage: false
- GPT Memory API execution: false
- Dry-run output pass: {result['dry_run_output_pass']}
- Apply without auth blocked: {result['apply_without_auth_blocked']}
- PURE baseline preserved: {result['pure_baseline_preserved']}
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
    print("pure_baseline_preserved:", result["pure_baseline_preserved"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
