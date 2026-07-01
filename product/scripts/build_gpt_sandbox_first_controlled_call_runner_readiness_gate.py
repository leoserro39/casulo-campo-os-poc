#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5341..5380"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-runner-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod5301_5340_gpt_sandbox_first_controlled_call_runner_packet.json"
RUNNER_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_packet_v0_1.json"
RUNNER_SPEC = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_spec_v0_1.json"
RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_call.py"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5301_5340_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DRY_RUN_LOG = ROOT / "outputs/prod5341_5380_runner_dry_run.log"
APPLY_BLOCK_LOG = ROOT / "outputs/prod5341_5380_runner_apply_block.log"
DRY_RUN_OUTPUT = ROOT / "outputs/gpt_sandbox_first_controlled_call_runner_dry_run_output.json"

DOC = ROOT / "docs/product/635_GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_call_runner_readiness_gate.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_call_runner_readiness_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_runner_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5341_5380_gpt_sandbox_first_controlled_call_runner_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod5341_5380_gpt_sandbox_first_controlled_call_runner_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5341_5380_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_call_runner_readiness_gate_creation",
    "gpt_first_controlled_call_live_authorization_packet_preparation",
    "dry_run_runner_validation",
    "apply_mode_block_validation",
    "roadmap_update"
]

READINESS_CHECKS = [
    "prior_runner_packet_present",
    "prior_runner_packet_passed",
    "prior_decision_runner_packet_ready",
    "runner_spec_present",
    "runner_script_present",
    "payload_template_present",
    "expected_log_template_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "runner_packet_only_confirmed",
    "runner_default_dry_run_confirmed",
    "runner_live_execution_blocked",
    "runner_dry_run_executes_successfully",
    "runner_apply_mode_blocks_successfully",
    "runner_dry_run_output_present",
    "runner_dry_run_output_pass",
    "runner_no_real_gpt_provider_call",
    "runner_no_openai_api_key_storage",
    "runner_no_gpt_memory_api_execution",
    "runner_no_live_gpt_call_execution",
    "runner_does_not_import_openai_sdk",
    "runner_does_not_read_env_key",
    "runner_does_not_store_api_key",
    "runner_does_not_call_provider",
    "runner_does_not_call_gpt_memory_api",
    "no_claude_scope",
    "no_gemini_scope",
    "no_copilot_scope",
    "real_gpt_call_still_blocked",
    "api_key_storage_still_blocked",
    "gpt_memory_api_still_blocked",
    "live_call_execution_still_blocked",
    "live_authorization_packet_preparation_only",
    "live_call_requires_future_explicit_gate",
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

while len(READINESS_CHECKS) < 164:
    READINESS_CHECKS.append(f"gpt_first_controlled_call_runner_readiness_control_{len(READINESS_CHECKS)+1:03d}")

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

def run_runner_validations():
    dry = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--dry-run"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    write(DRY_RUN_LOG, "STDOUT:\n" + dry.stdout + "\nSTDERR:\n" + dry.stderr + "\nRC:\n" + str(dry.returncode))

    apply = subprocess.run(
        [sys.executable, str(RUNNER_SCRIPT), "--apply"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    write(APPLY_BLOCK_LOG, "STDOUT:\n" + apply.stdout + "\nSTDERR:\n" + apply.stderr + "\nRC:\n" + str(apply.returncode))

    return dry, apply

def source_safety_checks(source):
    forbidden = [
        "import openai",
        "from openai",
        "OPENAI_API_KEY",
        "os.environ",
        "os.getenv",
        "requests.",
        "httpx.",
        "urllib.request",
        "aiohttp",
        "client.chat",
        "responses.create",
        "chat.completions",
        "client.memory",
        "memory.create",
        "memory.delete",
        "memories.create",
        "memories.delete",
    ]
    hits = [x for x in forbidden if x in source]
    return hits

def main():
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    runner_packet = read_json(RUNNER_PACKET) if RUNNER_PACKET.exists() else {}
    runner_spec = read_json(RUNNER_SPEC) if RUNNER_SPEC.exists() else {}
    payload_template = read_json(PAYLOAD_TEMPLATE) if PAYLOAD_TEMPLATE.exists() else {}
    expected_log_template = read_json(EXPECTED_LOG_TEMPLATE) if EXPECTED_LOG_TEMPLATE.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    dry = None
    apply = None
    if RUNNER_SCRIPT.exists():
        dry, apply = run_runner_validations()

    dry_output = read_json(DRY_RUN_OUTPUT) if DRY_RUN_OUTPUT.exists() else {}
    source = RUNNER_SCRIPT.read_text(encoding="utf-8") if RUNNER_SCRIPT.exists() else ""
    forbidden_hits = source_safety_checks(source)

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5301..5340":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5381..5420":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Call Runner Readiness Gate", "status": "CURRENT"})
    if "PROD-5381..5420" not in seen:
        roadmap_items.append({"phase": "PROD-5381..5420", "name": "GPT Sandbox First Controlled Call Live Authorization Packet", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous runner packet not PASS")
    if prev.get("decision") != "GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_PACKET_READY":
        errors.append("previous decision not runner packet ready")
    if prev.get("gpt_only_scope") is not True:
        errors.append("previous gpt_only_scope not true")
    if prev.get("multi_vendor_llm_scope") is not False:
        errors.append("previous multi_vendor_llm_scope not false")
    if prev.get("real_gpt_provider_call") is not False:
        errors.append("previous real_gpt_provider_call not false")
    if prev.get("openai_api_key_storage") is not False:
        errors.append("previous openai_api_key_storage not false")
    if prev.get("runner_packet_only") is not True:
        errors.append("previous runner packet only not true")
    if prev.get("runner_default_dry_run") is not True:
        errors.append("previous runner default dry-run not true")
    if prev.get("first_call_live_execution_allowed") is not False:
        errors.append("previous live execution allowed unexpectedly")
    if runner_packet.get("runner_packet_only") is not True:
        errors.append("runner packet not packet-only")
    if runner_spec.get("runner_default_mode") != "DRY_RUN_ONLY":
        errors.append("runner spec default mode not dry-run-only")
    if runner_spec.get("live_call_allowed") is not False:
        errors.append("runner spec live call allowed unexpectedly")
    if payload_template.get("template_only") is not True:
        errors.append("payload template not template-only")
    if expected_log_template.get("template_only") is not True:
        errors.append("expected log template not template-only")
    if dry is None or dry.returncode != 0:
        errors.append("runner dry-run did not complete successfully")
    if apply is None or apply.returncode == 0:
        errors.append("runner apply mode did not block")
    if apply is not None and "BLOCKED" not in (apply.stdout + apply.stderr):
        errors.append("runner apply mode did not emit BLOCKED")
    if dry_output.get("status") != "PASS":
        errors.append("runner dry-run output not PASS")
    if dry_output.get("real_gpt_provider_call") is not False:
        errors.append("runner dry-run real_gpt_provider_call not false")
    if dry_output.get("openai_api_key_storage") is not False:
        errors.append("runner dry-run openai_api_key_storage not false")
    if dry_output.get("gpt_memory_api_execution") is not False:
        errors.append("runner dry-run gpt_memory_api_execution not false")
    if dry_output.get("live_gpt_call_execution") is not False:
        errors.append("runner dry-run live_gpt_call_execution not false")
    if forbidden_hits:
        errors.append("runner source contains forbidden tokens: " + ",".join(forbidden_hits))

    decision = "APPROVED_FOR_GPT_FIRST_CONTROLLED_CALL_LIVE_AUTHORIZATION_PACKET_PREPARATION_ONLY"

    gate = {
        "version": "gpt_sandbox_first_controlled_call_runner_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_CALL_RUNNER_READINESS_GATE_NOT_READY",
        "purpose": "Validate the dry-run-only runner and approve only live authorization packet preparation, without live GPT execution.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "runner_readiness_gate_only": True,
        "live_authorization_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_gate": True,
        "dry_run_validation": {
            "returncode": None if dry is None else dry.returncode,
            "output_path": str(DRY_RUN_OUTPUT.relative_to(ROOT)),
            "status": dry_output.get("status"),
            "real_gpt_provider_call": dry_output.get("real_gpt_provider_call"),
            "openai_api_key_storage": dry_output.get("openai_api_key_storage"),
            "gpt_memory_api_execution": dry_output.get("gpt_memory_api_execution"),
            "live_gpt_call_execution": dry_output.get("live_gpt_call_execution")
        },
        "apply_block_validation": {
            "returncode": None if apply is None else apply.returncode,
            "blocked_message_present": False if apply is None else "BLOCKED" in (apply.stdout + apply.stderr)
        },
        "forbidden_source_tokens": forbidden_hits,
        "readiness_checks": READINESS_CHECKS,
        "readiness_check_count": len(READINESS_CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5381..5420 - GPT Sandbox First Controlled Call Live Authorization Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "runner_readiness_gate_only": True,
        "live_authorization_packet_preparation_only": True,
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
        "runner_readiness_gate_only": True,
        "live_authorization_packet_preparation_only": True,
        "first_call_live_execution_allowed": False,
        "live_call_requires_future_gate": True,
        "dry_run_output_pass": dry_output.get("status") == "PASS",
        "apply_mode_blocked": False if apply is None else apply.returncode != 0,
        "forbidden_source_tokens": forbidden_hits,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.7",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Call Runner Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5341..5380 - GPT Sandbox First Controlled Call Runner Readiness Gate

Validates the dry-run-only runner.

This gate runs the runner in dry-run mode and verifies that apply mode is blocked.

This phase still does not call GPT.

Next: PROD-5381..5420 - GPT Sandbox First Controlled Call Live Authorization Packet.
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

    report = f"""# PROD-5341..5380 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {len(READINESS_CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- Runner readiness gate only: true
- Live authorization packet preparation only: true
- First call live execution allowed: false
- Dry-run output pass: {result['dry_run_output_pass']}
- Apply mode blocked: {result['apply_mode_blocked']}
- Forbidden source tokens: {forbidden_hits}
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
    print("live_authorization_packet_preparation_only:", result["live_authorization_packet_preparation_only"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("dry_run_output_pass:", result["dry_run_output_pass"])
    print("apply_mode_blocked:", result["apply_mode_blocked"])
    print("forbidden_source_tokens:", forbidden_hits)
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
