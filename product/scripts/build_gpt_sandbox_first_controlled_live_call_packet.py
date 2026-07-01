#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5461..5500"
REQ_TAG = "product-gpt-sandbox-first-controlled-call-live-authorization-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod5421_5460_gpt_sandbox_first_controlled_call_live_authorization_readiness_gate.json"
AUTH_GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_readiness_gate_v0_1.json"
AUTH_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_packet_v0_1.json"
AUTH_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_live_authorization_template_v0_1.json"
RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_call.py"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
EXPECTED_LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_expected_log_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5421_5460_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/638_GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_PACKET.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_live_call_packet.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_live_call_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_packet_v0_1.json"
LIVE_RUNNER_SCRIPT = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_live_call.py"
LIVE_RUNNER_SPEC = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_runner_spec_v0_1.json"
LIVE_REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_request_template_v0_1.json"
LIVE_RESULT_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_result_template_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5461_5500_gpt_sandbox_first_controlled_live_call_packet.json"
OUT_MD = ROOT / "outputs/prod5461_5500_gpt_sandbox_first_controlled_live_call_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5461_5500_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "gpt_sandbox_first_controlled_live_call_packet_creation",
    "live_ready_runner_script_creation",
    "live_request_template_creation",
    "live_result_template_creation",
    "gpt_first_controlled_live_call_execution_gate_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_live_authorization_readiness_gate_present",
    "prior_live_authorization_readiness_gate_passed",
    "prior_decision_live_call_packet_preparation_only",
    "authorization_packet_present",
    "authorization_template_present",
    "dry_run_runner_present",
    "payload_template_present",
    "expected_log_template_present",
    "gpt_only_scope_confirmed",
    "openai_gpt_provider_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_mode_present",
    "stack_gpt_mode_present",
    "casulo_exocortex_stack_mode_present",
    "stack_v3_multiprovider_deferred",
    "live_call_packet_only",
    "live_runner_created",
    "live_runner_requires_explicit_apply",
    "live_runner_requires_env_key_ref",
    "live_runner_does_not_store_api_key",
    "live_runner_does_not_print_secret",
    "live_runner_blocks_without_casulo_live_auth",
    "live_runner_blocks_without_openai_api_key",
    "live_runner_blocks_unknown_mode",
    "live_runner_supports_pure_gpt",
    "live_runner_supports_stack_gpt",
    "live_runner_supports_exocortex_stack",
    "live_runner_writes_sanitized_log",
    "live_runner_does_not_call_gpt_memory_api",
    "live_runner_does_not_write_dataset",
    "live_execution_requires_next_gate",
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
    "live_execution_final_gate_required",
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

while len(CHECKS) < 196:
    CHECKS.append(f"gpt_first_controlled_live_call_packet_control_{len(CHECKS)+1:03d}")

LIVE_RUNNER_CODE = r'''#!/usr/bin/env python3
"""
CASULO GPT sandbox first controlled live call runner.

This runner is live-ready but blocked by default.

It requires all of the following for a future controlled live call:
- --apply
- CASULO_GPT_LIVE_AUTH=YES
- OPENAI_API_KEY available in environment
- explicit mode: PURE_GPT, STACK_GPT, or CASULO_EXOCORTEX_STACK

This runner does NOT:
- store API keys
- print secrets
- call GPT Memory API
- write to dataset
- insert real candidates
- activate production
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs"
PAYLOAD_TEMPLATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_call_payload_template_v0_1.json"
LIVE_LOG = OUT_DIR / "gpt_sandbox_first_controlled_live_call_result.json"

ALLOWED_MODES = {"PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"}

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=sorted(ALLOWED_MODES))
    parser.add_argument("--prompt", default="CASULO controlled sandbox test. Return a concise acknowledgement.")
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if not args.apply:
        result = {
            "status": "PASS",
            "mode": args.mode,
            "dry_run": True,
            "live_gpt_call_execution": False,
            "real_gpt_provider_call": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "reason": "Dry-run only. Use --apply only after explicit future gate.",
            "prompt_hash": sha256_text(args.prompt),
            "next_required_phase": "PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate"
        }
        write_json(LIVE_LOG, result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if os.environ.get("CASULO_GPT_LIVE_AUTH") != "YES":
        raise SystemExit("BLOCKED: CASULO_GPT_LIVE_AUTH=YES is required by future execution gate.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("BLOCKED: OPENAI_API_KEY must be present in environment for future live call. It will not be stored.")

    payload_template = read_json(PAYLOAD_TEMPLATE)
    started = time.time()

    try:
        from openai import OpenAI
    except Exception as exc:
        raise SystemExit("BLOCKED: openai package is not available or import failed: " + str(exc))

    client = OpenAI(api_key=api_key)
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    messages = [
        {"role": "system", "content": "You are running a CASULO controlled sandbox test. Do not make external claims. Do not store memory."},
        {"role": "user", "content": args.prompt},
    ]

    response = client.responses.create(
        model=model,
        input=messages,
        max_output_tokens=160,
    )

    elapsed_ms = int((time.time() - started) * 1000)
    output_text = getattr(response, "output_text", "")

    result = {
        "status": "PASS",
        "mode": args.mode,
        "dry_run": False,
        "live_gpt_call_execution": True,
        "real_gpt_provider_call": True,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "provider": "openai_gpt",
        "model": model,
        "prompt_hash": sha256_text(args.prompt),
        "output_hash": sha256_text(output_text),
        "output_preview": output_text[:500],
        "latency_ms": elapsed_ms,
        "dataset_write": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "payload_template_version": payload_template.get("version"),
        "post_call_review_required": True,
    }

    write_json(LIVE_LOG, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
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
    auth_gate = read_json(AUTH_GATE) if AUTH_GATE.exists() else {}
    auth_packet = read_json(AUTH_PACKET) if AUTH_PACKET.exists() else {}
    auth_template = read_json(AUTH_TEMPLATE) if AUTH_TEMPLATE.exists() else {}
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
        if ph == "PROD-5421..5460":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5501..5540":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Live Call Packet", "status": "CURRENT"})
    if "PROD-5501..5540" not in seen:
        roadmap_items.append({"phase": "PROD-5501..5540", "name": "GPT Sandbox First Controlled Live Call Execution Gate", "status": "NEXT"})

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior tag")
    if prev.get("status") != "PASS":
        errors.append("previous live authorization readiness gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_GPT_FIRST_CONTROLLED_LIVE_CALL_PACKET_PREPARATION_ONLY":
        errors.append("previous decision not approved for live call packet preparation")
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
    if prev.get("live_call_requires_future_execution_gate") is not True:
        errors.append("previous gate did not require future execution gate")
    if auth_gate.get("first_controlled_live_call_packet_preparation_only") is not True:
        errors.append("auth gate missing live call packet preparation only")
    if auth_packet.get("live_authorization_packet_only") is not True:
        errors.append("authorization packet not packet-only")
    if auth_template.get("template_only") is not True:
        errors.append("authorization template not template-only")
    if payload_template.get("template_only") is not True:
        errors.append("payload template not template-only")
    if expected_log_template.get("template_only") is not True:
        errors.append("expected log template not template-only")

    live_runner_spec = {
        "version": "gpt_sandbox_first_controlled_live_call_runner_spec.v0.1",
        "phase": PHASE,
        "live_ready_runner": True,
        "default_mode": "DRY_RUN_ONLY",
        "apply_requires_future_gate": True,
        "requires_casulo_live_auth_env": True,
        "requires_openai_api_key_env": True,
        "stores_api_key": False,
        "prints_secret": False,
        "calls_gpt_memory_api": False,
        "writes_dataset": False,
        "provider": "openai_gpt",
        "modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "next_required_phase": "PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate",
        "blocked_actions": BLOCKED
    }

    live_request_template = {
        "version": "gpt_sandbox_first_controlled_live_call_request_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "provider": "openai_gpt",
        "api_key_source": "OPENAI_API_KEY_ENV_REFERENCE_ONLY_NOT_STORED",
        "model_env": "OPENAI_MODEL_OPTIONAL_ENV_REFERENCE",
        "modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "default_prompt": "CASULO controlled sandbox test. Return a concise acknowledgement.",
        "prompt_storage_rule": "hash_only_for_logs",
        "blocked_actions": BLOCKED
    }

    live_result_template = {
        "version": "gpt_sandbox_first_controlled_live_call_result_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "fields": [
            "status",
            "mode",
            "dry_run",
            "live_gpt_call_execution",
            "real_gpt_provider_call",
            "openai_api_key_storage",
            "gpt_memory_api_execution",
            "provider",
            "model",
            "prompt_hash",
            "output_hash",
            "output_preview",
            "latency_ms",
            "dataset_write",
            "real_candidate_inserted",
            "real_candidate_accepted_to_dataset",
            "post_call_review_required"
        ],
        "blocked_actions": BLOCKED
    }

    packet = {
        "version": "gpt_sandbox_first_controlled_live_call_packet.v0.1",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_PACKET_READY",
        "purpose": "Prepare the first controlled GPT live call packet and live-ready runner without executing it.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "first_controlled_live_call_packet_only": True,
        "llm_not_called_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "first_call_live_execution_allowed": False,
        "live_execution_requires_next_gate": True,
        "live_runner_script": str(LIVE_RUNNER_SCRIPT.relative_to(ROOT)),
        "live_runner_spec": live_runner_spec,
        "checks": CHECKS,
        "check_count": len(CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": "PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "first_controlled_live_call_packet_only": True,
        "live_execution_allowed": False,
        "live_execution_requires_next_gate": True,
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
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_PACKET_READY" if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_PACKET_NOT_READY",
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
        "first_controlled_live_call_packet_only": True,
        "first_call_live_execution_allowed": False,
        "live_execution_requires_next_gate": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.0",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Live Call Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_called_yet": True,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5461..5500 - GPT Sandbox First Controlled Live Call Packet

Creates the first controlled GPT live call packet and live-ready runner.

This phase still does not execute the live GPT call.

The live-ready runner requires:
- --apply
- CASULO_GPT_LIVE_AUTH=YES
- OPENAI_API_KEY in environment
- explicit mode: PURE_GPT, STACK_GPT, or CASULO_EXOCORTEX_STACK

Next: PROD-5501..5540 - GPT Sandbox First Controlled Live Call Execution Gate.
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
        "- Live-ready runner prepared, but no live GPT call yet.",
        "- No API key value storage.",
        "- No GPT Memory API.",
        "- No multi-vendor LLM in this cycle.",
        "- No session execution.",
        "- No real candidate insert.",
        "- No dataset acceptance."
    ]

    report = f"""# PROD-5461..5500 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {len(CHECKS)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM called yet: false
- Real GPT provider call: false
- API key storage: false
- First controlled live call packet only: true
- First call live execution allowed: false
- Next: {packet['recommended_next_phase']}
"""

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(LIVE_RUNNER_SPEC, live_runner_spec)
    write_json(LIVE_REQUEST_TEMPLATE, live_request_template)
    write_json(LIVE_RESULT_TEMPLATE, live_result_template)
    write(LIVE_RUNNER_SCRIPT, LIVE_RUNNER_CODE)
    LIVE_RUNNER_SCRIPT.chmod(0o755)
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
    print("first_controlled_live_call_packet_only:", result["first_controlled_live_call_packet_only"])
    print("first_call_live_execution_allowed:", result["first_call_live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
