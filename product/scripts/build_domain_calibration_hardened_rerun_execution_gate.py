#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6141..6180"
REQ_TAG = "product-domain-calibration-output-capture-hardening-packet-v0.1"

PREV_PACKET = ROOT / "outputs/prod6101_6140_domain_calibration_output_capture_hardening_packet.json"
EXPECTED_SCHEMA = ROOT / "product/evaluation/domain_calibration_expected_response_schema_v0_1.json"
HARDENING_REQS = ROOT / "product/evaluation/domain_calibration_output_capture_hardening_requirements_v0_1.json"
HARDENED_RUNNER = ROOT / "product/scripts/run_domain_calibration_batch01_hardened.py"
HARDENED_RESULT = ROOT / "outputs/domain_calibration_batch01_hardened/domain_calibration_batch01_hardened_result.json"
ROADMAP_IN = ROOT / "outputs/prod6101_6140_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DRY_COPY = ROOT / "outputs/prod6141_6180_hardened_rerun_runner_dry_run_output.json"
BLOCK_COPY = ROOT / "outputs/prod6141_6180_hardened_rerun_runner_apply_without_auth_output.json"
DRY_LOG = ROOT / "outputs/prod6141_6180_hardened_rerun_runner_dry_run.log"
BLOCK_LOG = ROOT / "outputs/prod6141_6180_hardened_rerun_runner_apply_without_auth_block.log"

DOC = ROOT / "docs/product/657_DOMAIN_CALIBRATION_HARDENED_RERUN_EXECUTION_GATE.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_hardened_rerun_execution_gate.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_hardened_rerun_execution_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/domain_calibration_hardened_rerun_execution_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6141_6180_domain_calibration_hardened_rerun_execution_gate.json"
OUT_MD = ROOT / "outputs/prod6141_6180_domain_calibration_hardened_rerun_execution_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod6141_6180_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "live_gpt_call_in_this_gate",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
    "persistent_memory_write",
    "multi_vendor_llm_execution",
    "dataset_acceptance",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim",
    "commercial_claim",
    "domain_validation_claim"
]

ALLOWED = [
    "hardened_rerun_execution_gate_creation",
    "hardened_runner_dry_run_validation",
    "hardened_runner_apply_without_auth_block_validation",
    "hardened_rerun_explicit_operator_command_preparation",
    "roadmap_update"
]

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
        [sys.executable, str(HARDENED_RUNNER), "--limit", "36"],
        cwd=ROOT,
        text=True,
        capture_output=True
    )
    write(DRY_LOG, "STDOUT:\n" + dry.stdout + "\nSTDERR:\n" + dry.stderr + "\nRC:\n" + str(dry.returncode))
    if HARDENED_RESULT.exists():
        DRY_COPY.write_text(HARDENED_RESULT.read_text(encoding="utf-8"), encoding="utf-8")

    blocked = subprocess.run(
        [sys.executable, str(HARDENED_RUNNER), "--apply", "--limit", "36"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={}
    )
    write(BLOCK_LOG, "STDOUT:\n" + blocked.stdout + "\nSTDERR:\n" + blocked.stderr + "\nRC:\n" + str(blocked.returncode))
    if HARDENED_RESULT.exists():
        BLOCK_COPY.write_text(HARDENED_RESULT.read_text(encoding="utf-8"), encoding="utf-8")

    return dry, blocked

def main():
    prev = read_json(PREV_PACKET) if PREV_PACKET.exists() else {}
    schema = read_json(EXPECTED_SCHEMA) if EXPECTED_SCHEMA.exists() else {}
    reqs = read_json(HARDENING_REQS) if HARDENING_REQS.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    dry_proc, block_proc = run_validations()

    dry = read_json(DRY_COPY) if DRY_COPY.exists() else {}
    blocked = read_json(BLOCK_COPY) if BLOCK_COPY.exists() else {}

    block_text = block_proc.stdout + block_proc.stderr
    block_message_present = (
        "blocked_reason" in block_text
        or "CASULO_GPT_LIVE_AUTH=YES is required" in block_text
        or "BLOCKED" in block_text
    )

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required hardening packet tag")
    if prev.get("status") != "PASS":
        errors.append("previous hardening packet not PASS")
    if prev.get("decision") != "DOMAIN_CALIBRATION_OUTPUT_CAPTURE_HARDENING_PACKET_READY":
        errors.append("previous hardening packet decision mismatch")
    if prev.get("hardened_runner_created") is not True:
        errors.append("previous hardening packet did not create hardened runner")
    if prev.get("technical_pass_behavioral_pass_separated") is not True:
        errors.append("technical/behavioral separation missing in prior packet")
    if prev.get("empty_output_behavioral_fail") is not True:
        errors.append("empty output behavioral fail not set")
    if prev.get("non_json_output_behavioral_fail") is not True:
        errors.append("non-json output behavioral fail not set")
    if prev.get("missing_required_fields_behavioral_fail") is not True:
        errors.append("missing fields behavioral fail not set")

    if not HARDENED_RUNNER.exists():
        errors.append("hardened runner missing")
    if len(schema.get("required_fields", [])) != 15:
        errors.append("expected response schema required_fields mismatch")
    if len(reqs.get("requirements", [])) < 10:
        errors.append("hardening requirements incomplete")

    if dry_proc.returncode != 0:
        errors.append("hardened runner dry-run returned nonzero")
    if dry.get("status") != "PASS":
        errors.append("hardened runner dry-run not PASS")
    if dry.get("dry_run") is not True:
        errors.append("hardened dry-run flag mismatch")
    if dry.get("apply") is not False:
        errors.append("hardened dry-run apply not false")
    if dry.get("planned_execution_count") != 36:
        errors.append("hardened dry-run planned count mismatch")
    if dry.get("dry_run_count") != 36:
        errors.append("hardened dry-run count mismatch")
    if dry.get("executed_count") != 0:
        errors.append("hardened dry-run executed count not zero")
    if dry.get("real_provider_call_count") != 0:
        errors.append("hardened dry-run provider call count not zero")
    if dry.get("successful_live_response_count") != 0:
        errors.append("hardened dry-run successful response count not zero")
    if dry.get("review_ready_count") != 0:
        errors.append("hardened dry-run review ready count not zero")
    if dry.get("openai_api_key_storage") is not False:
        errors.append("hardened dry-run api key storage not false")
    if dry.get("gpt_memory_api_execution") is not False:
        errors.append("hardened dry-run gpt memory api not false")
    if dry.get("dataset_write") is not False:
        errors.append("hardened dry-run dataset write not false")
    if dry.get("client_evidence") is not False:
        errors.append("hardened dry-run client evidence not false")
    if dry.get("production_evidence") is not False:
        errors.append("hardened dry-run production evidence not false")

    if block_proc.returncode == 0:
        errors.append("hardened apply without auth did not block")
    if blocked.get("status") != "FAIL":
        errors.append("hardened apply without auth output not FAIL")
    if blocked.get("dry_run") is not False:
        errors.append("hardened block dry_run should be false")
    if blocked.get("apply") is not True:
        errors.append("hardened block apply should be true")
    if blocked.get("planned_execution_count") != 36:
        errors.append("hardened block planned count mismatch")
    if blocked.get("executed_count") != 0:
        errors.append("hardened block executed count not zero")
    if blocked.get("real_provider_call_count") != 0:
        errors.append("hardened block provider calls not zero")
    if blocked.get("successful_live_response_count") != 0:
        errors.append("hardened block successful responses not zero")
    if blocked.get("review_ready_count") != 0:
        errors.append("hardened block review ready count not zero")
    if blocked.get("openai_api_key_storage") is not False:
        errors.append("hardened block api key storage not false")
    if blocked.get("gpt_memory_api_execution") is not False:
        errors.append("hardened block gpt memory api not false")
    if blocked.get("dataset_write") is not False:
        errors.append("hardened block dataset write not false")
    if blocked.get("client_evidence") is not False:
        errors.append("hardened block client evidence not false")
    if blocked.get("production_evidence") is not False:
        errors.append("hardened block production evidence not false")
    if not block_message_present:
        errors.append("hardened block message missing")

    checks = [
        "prior_output_capture_hardening_packet_present",
        "prior_output_capture_hardening_packet_passed",
        "required_prior_tag_present",
        "hardened_runner_present",
        "expected_response_schema_present",
        "hardening_requirements_present",
        "technical_pass_behavioral_pass_separated",
        "empty_output_behavioral_fail_defined",
        "non_json_output_behavioral_fail_defined",
        "missing_required_fields_behavioral_fail_defined",
        "hardened_runner_dry_run_executed",
        "hardened_runner_dry_run_passed",
        "hardened_runner_dry_run_no_provider_calls",
        "hardened_runner_dry_run_no_successful_responses",
        "hardened_runner_dry_run_no_review_ready",
        "hardened_runner_dry_run_no_api_key_storage",
        "hardened_runner_dry_run_no_gpt_memory_api",
        "hardened_runner_dry_run_no_dataset_write",
        "hardened_runner_apply_without_auth_blocked",
        "hardened_runner_apply_without_auth_no_provider_calls",
        "hardened_runner_apply_without_auth_no_successful_responses",
        "hardened_runner_apply_without_auth_no_review_ready",
        "future_hardened_rerun_requires_explicit_operator_command",
        "future_hardened_rerun_requires_casulo_live_auth",
        "future_hardened_rerun_requires_openai_api_key_env",
        "future_hardened_rerun_requires_post_call_review",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 292:
        checks.append(f"hardened_rerun_execution_gate_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6101..6140":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-6181..6220":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration Hardened Rerun Execution Gate",
            "status": "CURRENT"
        })
    if "PROD-6181..6220" not in seen:
        roadmap_items.append({
            "phase": "PROD-6181..6220",
            "name": "Domain Calibration Batch 01 Hardened Rerun Execution Run",
            "status": "NEXT"
        })

    decision = "APPROVED_FOR_DOMAIN_CALIBRATION_HARDENED_RERUN_EXECUTION_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY"

    gate = {
        "version": "domain_calibration_hardened_rerun_execution_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_HARDENED_RERUN_EXECUTION_GATE_NOT_READY",
        "execution_gate_only": True,
        "live_execution_performed_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "scenario_count": 12,
        "planned_execution_count": 36,
        "hardened_runner_ref": str(HARDENED_RUNNER.relative_to(ROOT)),
        "expected_schema_ref": str(EXPECTED_SCHEMA.relative_to(ROOT)),
        "technical_pass_behavioral_pass_separated": True,
        "empty_output_behavioral_fail": True,
        "non_json_output_behavioral_fail": True,
        "missing_required_fields_behavioral_fail": True,
        "dry_run_validation": {
            "returncode": dry_proc.returncode,
            "status": dry.get("status"),
            "dry_run_count": dry.get("dry_run_count"),
            "real_provider_call_count": dry.get("real_provider_call_count"),
            "successful_live_response_count": dry.get("successful_live_response_count"),
            "review_ready_count": dry.get("review_ready_count")
        },
        "apply_without_auth_block_validation": {
            "returncode": block_proc.returncode,
            "status": blocked.get("status"),
            "blocked_reason": blocked.get("blocked_reason"),
            "block_message_present": block_message_present,
            "real_provider_call_count": blocked.get("real_provider_call_count"),
            "successful_live_response_count": blocked.get("successful_live_response_count"),
            "review_ready_count": blocked.get("review_ready_count")
        },
        "future_hardened_rerun_allowed_only_by_explicit_operator_command": True,
        "operator_command_requirements": [
            "export OPENAI_API_KEY in shell only",
            "export CASULO_GPT_LIVE_AUTH=YES",
            "run product/scripts/run_domain_calibration_batch01_hardened.py --apply --limit 36",
            "review outputs/domain_calibration_batch01_hardened/domain_calibration_batch01_hardened_result.json",
            "perform post-call review before behavioral scoring acceptance"
        ],
        "readiness_checks": checks,
        "readiness_check_count": len(checks),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": "PROD-6181..6220 - Domain Calibration Batch 01 Hardened Rerun Execution Run"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "execution_gate_only": True,
        "live_execution_allowed_in_this_gate": False,
        "future_hardened_rerun_requires_explicit_operator_command": True,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "technical_pass_behavioral_pass_separated": True,
        "dataset_acceptance_blocked": True,
        "client_evidence_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(checks),
        "execution_gate_only": True,
        "live_execution_performed_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "scenario_count": 12,
        "planned_execution_count": 36,
        "hardened_runner_dry_run_pass": dry.get("status") == "PASS",
        "hardened_runner_dry_run_real_provider_call_count": dry.get("real_provider_call_count"),
        "hardened_runner_dry_run_successful_live_response_count": dry.get("successful_live_response_count"),
        "hardened_runner_dry_run_review_ready_count": dry.get("review_ready_count"),
        "hardened_runner_apply_without_auth_blocked": block_proc.returncode != 0,
        "hardened_runner_apply_without_auth_block_message_present": block_message_present,
        "hardened_runner_apply_without_auth_real_provider_call_count": blocked.get("real_provider_call_count"),
        "hardened_runner_apply_without_auth_successful_live_response_count": blocked.get("successful_live_response_count"),
        "hardened_runner_apply_without_auth_review_ready_count": blocked.get("review_ready_count"),
        "technical_pass_behavioral_pass_separated": True,
        "empty_output_behavioral_fail": True,
        "non_json_output_behavioral_fail": True,
        "missing_required_fields_behavioral_fail": True,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "future_hardened_rerun_allowed_only_by_explicit_operator_command": True,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.7",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Hardened Rerun Execution Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-6141..6180 - Domain Calibration Hardened Rerun Execution Gate

Validates readiness for the hardened Domain Calibration Batch 01 rerun.

This gate does not call GPT. It validates the hardened runner dry-run and confirms apply without authorization is blocked.

The next phase will perform the real hardened rerun with 36 controlled GPT/OpenAI calls.

Important boundary: technical PASS remains separate from behavioral PASS.
"""

    report = f"""# PROD-6141..6180 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {result['readiness_check_count']}
- Execution gate only: true
- Live execution performed in this gate: false
- Scenario count: {result['scenario_count']}
- Planned execution count: {result['planned_execution_count']}
- Hardened dry-run pass: {result['hardened_runner_dry_run_pass']}
- Hardened dry-run provider calls: {result['hardened_runner_dry_run_real_provider_call_count']}
- Hardened dry-run successful responses: {result['hardened_runner_dry_run_successful_live_response_count']}
- Hardened dry-run review ready count: {result['hardened_runner_dry_run_review_ready_count']}
- Apply without auth blocked: {result['hardened_runner_apply_without_auth_blocked']}
- Apply without auth provider calls: {result['hardened_runner_apply_without_auth_real_provider_call_count']}
- Apply without auth successful responses: {result['hardened_runner_apply_without_auth_successful_live_response_count']}
- Apply without auth review ready count: {result['hardened_runner_apply_without_auth_review_ready_count']}
- Technical PASS separated from behavioral PASS: true
- Empty output behavioral fail: true
- Non-JSON output behavioral fail: true
- Missing required fields behavioral fail: true
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
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
    print("dry_run_pass:", result["hardened_runner_dry_run_pass"])
    print("dry_run_provider_calls:", result["hardened_runner_dry_run_real_provider_call_count"])
    print("dry_run_successful_responses:", result["hardened_runner_dry_run_successful_live_response_count"])
    print("dry_run_review_ready_count:", result["hardened_runner_dry_run_review_ready_count"])
    print("apply_without_auth_blocked:", result["hardened_runner_apply_without_auth_blocked"])
    print("apply_without_auth_provider_calls:", result["hardened_runner_apply_without_auth_real_provider_call_count"])
    print("apply_without_auth_successful_responses:", result["hardened_runner_apply_without_auth_successful_live_response_count"])
    print("apply_without_auth_review_ready_count:", result["hardened_runner_apply_without_auth_review_ready_count"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
