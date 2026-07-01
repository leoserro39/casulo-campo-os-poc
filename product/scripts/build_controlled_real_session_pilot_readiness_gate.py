#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3421..3460"
REQ_TAG = "product-controlled-real-session-pilot-packet-v0.1"

PACKET_OUT = ROOT / "outputs/prod3381_3420_controlled_real_session_pilot_packet.json"
PACKET = ROOT / "product/calibration/real_sessions/controlled_real_session_pilot_packet_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/manual_capture_runbook_v0_1.md"
CHECKLIST = ROOT / "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json"

DOC = ROOT / "docs/product/587_CONTROLLED_REAL_SESSION_PILOT_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_real_session_pilot_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_real_session_pilot_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3421_3460_controlled_real_session_pilot_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod3421_3460_controlled_real_session_pilot_readiness_gate.md"

ALLOWED = [
    "manual_controlled_pilot_execution_preparation",
    "manual_sanitized_source_reference_capture",
    "human_reviewed_pilot_session_creation",
    "privacy_reviewed_dataset_candidate_creation",
    "pilot_evidence_packet_preparation"
]

BLOCKED = [
    "automatic_real_session_capture",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "real_world_profit_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "commercial_package_pricing_claim"
]

REQUIRED_CONTROLS = [
    "source_refs_only",
    "privacy_review_required",
    "pii_redaction_required",
    "secret_scan_required",
    "human_reviewer_required",
    "claim_boundary_required",
    "dataset_acceptance_gate_required",
    "no_raw_private_data",
    "no_client_facing_claim",
    "no_production_activation"
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

def main():
    errors = []

    packet_out = read_json(PACKET_OUT) if PACKET_OUT.exists() else {}
    packet = read_json(PACKET) if PACKET.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    checklist = read_json(CHECKLIST) if CHECKLIST.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}

    pilot_scope = packet.get("pilot_scope", {})
    exit_criteria = set(packet.get("required_exit_criteria", []))
    checklist_names = {c.get("name") for c in checklist.get("checks", [])}
    schema_required = schema.get("required", [])

    decision = "APPROVED_FOR_MANUAL_CONTROLLED_REAL_SESSION_PILOT_EXECUTION_ONLY"
    if packet_out.get("real_data_captured") is not False:
        decision = "BLOCK_REAL_DATA_ALREADY_PRESENT"
    if empty_batch.get("record_count") != 0:
        decision = "BLOCK_NON_EMPTY_REAL_BATCH"

    gate = {
        "version": "controlled_real_session_pilot_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "scope": "Manual controlled pilot execution only. This gate does not capture data.",
        "real_data_captured_in_this_phase": False,
        "pilot_scope": pilot_scope,
        "required_controls": REQUIRED_CONTROLS,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "execution_boundary": {
            "automatic_capture_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_facing_claim_allowed": False,
            "production_activation_allowed": False,
            "manual_sanitized_source_reference_capture_allowed": True,
            "human_review_required": True
        },
        "acceptance_rule": "A pilot record may become a dataset candidate only after source_refs_only, privacy review, PII redaction, secret scan, human reviewer notes, claim boundary and decision gate are all present.",
        "recommended_next_phase": "PROD-3461..3500 - Controlled Real Session Pilot Execution Runbook"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_real_session_pilot_readiness_gate",
        "manual_controlled_execution_only": True,
        "real_data_captured_in_this_phase": False,
        "automatic_capture_blocked": True,
        "human_review_required": True,
        "privacy_controls_required": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-3421..3460 - Controlled Real Session Pilot Readiness Gate

Defines the readiness gate for controlled real-session pilot execution.

This phase does not capture real session data.

The gate approves only manual controlled pilot execution preparation with source references only, privacy review, PII redaction, secret scan, human reviewer notes, claim boundary and dataset acceptance gate.

Blocked: automatic capture, raw private data, secrets, unredacted PII, client-facing claims, production activation, commercial pricing claims and validated savings or hallucination-reduction claims.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "packet_output_exists": PACKET_OUT.exists(),
        "packet_output_pass": packet_out.get("status") == "PASS",
        "packet_exists": PACKET.exists(),
        "schema_exists": SCHEMA.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "checklist_exists": CHECKLIST.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "packet_real_data_false": packet_out.get("real_data_captured") is False,
        "empty_batch_record_count_zero": empty_batch.get("record_count") == 0,
        "schema_required_count": len(schema_required),
        "target_sessions_positive": pilot_scope.get("target_session_count", 0) >= 10,
        "minimum_sessions_positive": pilot_scope.get("minimum_accepted_sessions", 0) >= 5,
        "exit_criteria_count": len(exit_criteria),
        "required_controls_count": len(REQUIRED_CONTROLS),
        "has_privacy_exit": "privacy_review_passed" in exit_criteria,
        "has_pii_exit": "pii_redaction_passed" in exit_criteria,
        "has_secret_exit": "secret_scan_passed" in exit_criteria,
        "has_source_refs_exit": "source_refs_only_confirmed" in exit_criteria,
        "has_no_client_claim_exit": "no_client_facing_claim_confirmed" in exit_criteria,
        "has_no_production_exit": "no_production_activation_confirmed" in exit_criteria,
        "checklist_has_source_refs": "source_refs_only" in checklist_names,
        "checklist_has_secret_scan": "secret_scan_completed" in checklist_names,
        "decision_manual_only": decision == "APPROVED_FOR_MANUAL_CONTROLLED_REAL_SESSION_PILOT_EXECUTION_ONLY",
        "real_data_not_captured_this_phase": gate["real_data_captured_in_this_phase"] is False,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "client_claim_blocked": "client_facing_value_claim" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED,
        "manual_source_ref_allowed": "manual_sanitized_source_reference_capture" in ALLOWED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["exit_criteria_count"] < 10:
        errors.append("exit_criteria_count below 10")
    if checks["required_controls_count"] < 10:
        errors.append("required_controls_count below 10")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_REAL_SESSION_PILOT_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate": "product/memory/controlled_real_session_pilot_readiness_gate_v0_1.json",
        "target_session_count": pilot_scope.get("target_session_count"),
        "minimum_accepted_sessions": pilot_scope.get("minimum_accepted_sessions"),
        "real_data_captured_in_this_phase": False,
        "required_controls_count": len(REQUIRED_CONTROLS),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3421..3460 Controlled Real Session Pilot Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Target sessions: `{result['target_session_count']}`",
        f"- Minimum accepted sessions: `{result['minimum_accepted_sessions']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Required controls: `{len(REQUIRED_CONTROLS)}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Manual controlled pilot execution only.",
        "- No automatic capture.",
        "- No raw private data, secrets or unredacted PII.",
        "- No client-facing or validated real-world claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("target_sessions:", result["target_session_count"])
    print("minimum_accepted:", result["minimum_accepted_sessions"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("required_controls:", len(REQUIRED_CONTROLS))
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
