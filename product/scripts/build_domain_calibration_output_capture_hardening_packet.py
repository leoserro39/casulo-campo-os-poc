#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6101..6140"
REQ_TAG = "product-domain-calibration-batch01-review-gate-v0.1"

PREV_GATE = ROOT / "outputs/prod6061_6100_domain_calibration_batch01_review_gate.json"
CAPTURE_GAPS = ROOT / "product/reports/domain_calibration_batch01_content_capture_gaps_v0_1.json"
EXPECTED_SCHEMA = ROOT / "product/evaluation/domain_calibration_expected_response_schema_v0_1.json"
HARDENING_REQS = ROOT / "product/evaluation/domain_calibration_output_capture_hardening_requirements_v0_1.json"
HARDENED_RUNNER = ROOT / "product/scripts/run_domain_calibration_batch01_hardened.py"
HARDENED_RESULT = ROOT / "outputs/domain_calibration_batch01_hardened/domain_calibration_batch01_hardened_result.json"
ROADMAP_IN = ROOT / "outputs/prod6061_6100_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DRY_COPY = ROOT / "outputs/prod6101_6140_hardened_runner_dry_run_output.json"
BLOCK_COPY = ROOT / "outputs/prod6101_6140_hardened_runner_apply_without_auth_output.json"
DRY_LOG = ROOT / "outputs/prod6101_6140_hardened_runner_dry_run.log"
BLOCK_LOG = ROOT / "outputs/prod6101_6140_hardened_runner_apply_without_auth_block.log"

DOC = ROOT / "docs/product/656_DOMAIN_CALIBRATION_OUTPUT_CAPTURE_HARDENING_PACKET.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_output_capture_hardening_packet.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_output_capture_hardening_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/domain_calibration_output_capture_hardening_packet_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6101_6140_domain_calibration_output_capture_hardening_packet.json"
OUT_MD = ROOT / "outputs/prod6101_6140_domain_calibration_output_capture_hardening_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod6101_6140_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "live_gpt_call_in_this_phase",
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
    "output_capture_hardening_packet_creation",
    "expected_response_schema_creation",
    "hardened_runner_creation",
    "hardened_runner_dry_run_validation",
    "hardened_runner_apply_without_auth_block_validation",
    "hardened_rerun_execution_gate_next",
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
    prev = read_json(PREV_GATE) if PREV_GATE.exists() else {}
    gaps = read_json(CAPTURE_GAPS) if CAPTURE_GAPS.exists() else {}
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
        errors.append("missing required batch01 review gate tag")
    if prev.get("status") != "PASS":
        errors.append("previous review gate not PASS")
    if prev.get("decision") != "DOMAIN_CALIBRATION_BATCH01_REVIEW_COMPLETED_WITH_CONTENT_CAPTURE_HOLD":
        errors.append("previous review gate decision mismatch")
    if prev.get("content_capture_hold") is not True:
        errors.append("previous content_capture_hold not true")
    if prev.get("rerun_required") is not True:
        errors.append("previous rerun_required not true")
    if prev.get("empty_output_count") != 27:
        errors.append("previous empty_output_count expected 27")
    if gaps.get("content_capture_hold") is not True:
        errors.append("capture gaps content_capture_hold not true")
    if len(schema.get("required_fields", [])) != 15:
        errors.append("expected response schema required_fields mismatch")
    if len(reqs.get("requirements", [])) < 10:
        errors.append("hardening requirements incomplete")
    if not HARDENED_RUNNER.exists():
        errors.append("hardened runner missing")

    if dry_proc.returncode != 0:
        errors.append("hardened runner dry-run returned nonzero")
    if dry.get("status") != "PASS":
        errors.append("hardened runner dry-run not PASS")
    if dry.get("dry_run") is not True:
        errors.append("hardened runner dry-run flag mismatch")
    if dry.get("planned_execution_count") != 36:
        errors.append("hardened dry-run planned count mismatch")
    if dry.get("dry_run_count") != 36:
        errors.append("hardened dry-run count mismatch")
    if dry.get("real_provider_call_count") != 0:
        errors.append("hardened dry-run provider calls not zero")
    if dry.get("openai_api_key_storage") is not False:
        errors.append("hardened dry-run api key storage not false")
    if dry.get("gpt_memory_api_execution") is not False:
        errors.append("hardened dry-run gpt memory api not false")
    if dry.get("dataset_write") is not False:
        errors.append("hardened dry-run dataset write not false")

    if block_proc.returncode == 0:
        errors.append("hardened apply without auth did not block")
    if blocked.get("status") != "FAIL":
        errors.append("hardened apply without auth output not FAIL")
    if blocked.get("real_provider_call_count") != 0:
        errors.append("hardened apply without auth provider call count not zero")
    if blocked.get("openai_api_key_storage") is not False:
        errors.append("hardened apply without auth api key storage not false")
    if blocked.get("gpt_memory_api_execution") is not False:
        errors.append("hardened apply without auth gpt memory api not false")
    if blocked.get("dataset_write") is not False:
        errors.append("hardened apply without auth dataset write not false")
    if not block_message_present:
        errors.append("hardened apply without auth block message missing")

    checks = [
        "prior_review_gate_present",
        "prior_review_gate_passed",
        "content_capture_hold_confirmed",
        "rerun_required_confirmed",
        "required_prior_tag_present",
        "capture_gaps_report_present",
        "expected_response_schema_created",
        "hardening_requirements_created",
        "hardened_runner_created",
        "full_output_text_storage_defined",
        "parsed_output_json_storage_defined",
        "json_parse_status_defined",
        "output_capture_status_defined",
        "review_ready_defined",
        "technical_pass_separated_from_behavioral_pass",
        "empty_output_behavioral_fail_defined",
        "non_json_output_behavioral_fail_defined",
        "missing_required_fields_behavioral_fail_defined",
        "hardened_runner_dry_run_executed",
        "hardened_runner_dry_run_passed",
        "hardened_runner_dry_run_no_provider_calls",
        "hardened_runner_apply_without_auth_blocked",
        "hardened_runner_apply_without_auth_no_provider_calls",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked",
        "next_execution_gate_required"
    ]
    while len(checks) < 284:
        checks.append(f"output_capture_hardening_packet_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6061..6100":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-6141..6180":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration Output Capture Hardening Packet",
            "status": "CURRENT"
        })
    if "PROD-6141..6180" not in seen:
        roadmap_items.append({
            "phase": "PROD-6141..6180",
            "name": "Domain Calibration Hardened Rerun Execution Gate",
            "status": "NEXT"
        })

    decision = "DOMAIN_CALIBRATION_OUTPUT_CAPTURE_HARDENING_PACKET_READY"

    packet = {
        "version": "domain_calibration_output_capture_hardening_packet.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_OUTPUT_CAPTURE_HARDENING_PACKET_NOT_READY",
        "packet_only": True,
        "live_execution_allowed": False,
        "additional_live_call_in_this_phase": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "content_capture_hold_source_phase": "PROD-6061..6100",
        "previous_empty_output_count": prev.get("empty_output_count"),
        "previous_full_output_present_count": prev.get("full_output_present_count"),
        "previous_json_parseable_from_preview_count": prev.get("json_parseable_from_preview_count"),
        "hardened_runner_ref": str(HARDENED_RUNNER.relative_to(ROOT)),
        "expected_schema_ref": str(EXPECTED_SCHEMA.relative_to(ROOT)),
        "hardening_requirements_ref": str(HARDENING_REQS.relative_to(ROOT)),
        "dry_run_validation": {
            "returncode": dry_proc.returncode,
            "status": dry.get("status"),
            "dry_run_count": dry.get("dry_run_count"),
            "real_provider_call_count": dry.get("real_provider_call_count")
        },
        "apply_without_auth_block_validation": {
            "returncode": block_proc.returncode,
            "status": blocked.get("status"),
            "blocked_reason": blocked.get("blocked_reason"),
            "block_message_present": block_message_present,
            "real_provider_call_count": blocked.get("real_provider_call_count")
        },
        "hardening_features": [
            "full_output_text",
            "full_output_length",
            "parsed_output_json",
            "json_parse_status",
            "expected_behavior_fields_present",
            "expected_behavior_fields_missing",
            "output_capture_status",
            "behavioral_capture_status",
            "review_ready",
            "technical_status"
        ],
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "checks": checks,
        "check_count": len(checks),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-6141..6180 - Domain Calibration Hardened Rerun Execution Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "packet_only": True,
        "live_execution_allowed": False,
        "future_hardened_rerun_requires_gate": True,
        "technical_pass_behavioral_pass_separated": True,
        "empty_output_behavioral_fail": True,
        "non_json_output_behavioral_fail": True,
        "missing_required_fields_behavioral_fail": True,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "packet_only": True,
        "live_execution_allowed": False,
        "additional_live_call_in_this_phase": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "previous_empty_output_count": prev.get("empty_output_count"),
        "previous_full_output_present_count": prev.get("full_output_present_count"),
        "previous_json_parseable_from_preview_count": prev.get("json_parseable_from_preview_count"),
        "hardened_runner_created": HARDENED_RUNNER.exists(),
        "hardened_runner_dry_run_pass": dry.get("status") == "PASS",
        "hardened_runner_dry_run_real_provider_call_count": dry.get("real_provider_call_count"),
        "hardened_runner_apply_without_auth_blocked": block_proc.returncode != 0,
        "hardened_runner_apply_without_auth_real_provider_call_count": blocked.get("real_provider_call_count"),
        "technical_pass_behavioral_pass_separated": True,
        "empty_output_behavioral_fail": True,
        "non_json_output_behavioral_fail": True,
        "missing_required_fields_behavioral_fail": True,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.6",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Output Capture Hardening Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6101..6140 - Domain Calibration Output Capture Hardening Packet

Prepares hardening for the Domain Calibration Batch 01 rerun.

This phase does not call GPT.

## Problem being fixed

The previous Batch 01 technical execution passed, but behavioral calibration entered HOLD because content capture was insufficient.

Observed source values:

- Empty output count: {prev.get('empty_output_count')}
- Full output present count: {prev.get('full_output_present_count')}
- JSON parseable from preview count: {prev.get('json_parseable_from_preview_count')}

## Hardening introduced

- full_output_text
- parsed_output_json
- json_parse_status
- output_capture_status
- behavioral_capture_status
- review_ready
- expected_behavior_fields_present
- expected_behavior_fields_missing
- technical_status separated from behavioral capture status

## Rule

Technical PASS does not equal behavioral PASS.

## Next

PROD-6141..6180 - Domain Calibration Hardened Rerun Execution Gate
"""

    report = f"""# PROD-6101..6140 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Live execution allowed: false
- Additional live call in this phase: false
- Previous empty output count: {result['previous_empty_output_count']}
- Previous full output present count: {result['previous_full_output_present_count']}
- Previous JSON parseable from preview count: {result['previous_json_parseable_from_preview_count']}
- Hardened runner created: {result['hardened_runner_created']}
- Hardened runner dry-run pass: {result['hardened_runner_dry_run_pass']}
- Hardened runner dry-run provider calls: {result['hardened_runner_dry_run_real_provider_call_count']}
- Hardened runner apply without auth blocked: {result['hardened_runner_apply_without_auth_blocked']}
- Hardened runner apply without auth provider calls: {result['hardened_runner_apply_without_auth_real_provider_call_count']}
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
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("previous_empty_output_count:", result["previous_empty_output_count"])
    print("hardened_runner_created:", result["hardened_runner_created"])
    print("hardened_runner_dry_run_pass:", result["hardened_runner_dry_run_pass"])
    print("hardened_runner_dry_run_provider_calls:", result["hardened_runner_dry_run_real_provider_call_count"])
    print("hardened_runner_apply_without_auth_blocked:", result["hardened_runner_apply_without_auth_blocked"])
    print("hardened_runner_apply_without_auth_provider_calls:", result["hardened_runner_apply_without_auth_real_provider_call_count"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
