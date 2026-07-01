#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3501..3540"
REQ_TAG = "product-controlled-real-session-pilot-execution-runbook-v0.1"

PREV_OUT = ROOT / "outputs/prod3461_3500_controlled_real_session_pilot_execution_runbook.json"
EXEC_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_real_session_pilot_execution_runbook_v0_1.md"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
OPERATOR_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_real_session_operator_checklist_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
PILOT_PACKET = ROOT / "product/calibration/real_sessions/controlled_real_session_pilot_packet_v0_1.json"

DOC = ROOT / "docs/product/589_CONTROLLED_PILOT_EVIDENCE_PACKET_REVIEWER_QUEUE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_evidence_packet_reviewer_queue.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_evidence_packet_reviewer_queue_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3501_3540_controlled_pilot_evidence_packet_reviewer_queue.json"
OUT_MD = ROOT / "outputs/prod3501_3540_controlled_pilot_evidence_packet_reviewer_queue.md"

EVIDENCE_FIELDS = [
    "pilot_id",
    "session_id",
    "candidate_record_ref",
    "source_reference_refs",
    "baseline_output_ref",
    "casulo_output_ref",
    "snapshot_or_state_ref",
    "evidence_pointer_refs",
    "operator_checklist_ref",
    "privacy_review_ref",
    "pii_redaction_ref",
    "secret_scan_ref",
    "human_reviewer_notes_ref",
    "decision_gate",
    "claim_boundary",
    "dataset_acceptance_decision"
]

QUEUE_FIELDS = [
    "queue_id",
    "queue_status",
    "reviewer_assignment_status",
    "pending_count",
    "accepted_count",
    "rejected_count",
    "held_count",
    "items"
]

REVIEW_DECISIONS = [
    "ACCEPT_AS_CALIBRATION_CANDIDATE",
    "REJECT_PRIVACY_OR_SECRET_RISK",
    "HOLD_FOR_MISSING_EVIDENCE",
    "HOLD_FOR_CLAIM_BOUNDARY_REVIEW",
    "HOLD_FOR_SCHEMA_REPAIR"
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

ALLOWED = [
    "evidence_packet_template_creation",
    "empty_reviewer_queue_creation",
    "review_decision_taxonomy_definition",
    "manual_review_preparation",
    "calibration_candidate_evidence_protocol"
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

    prev_out = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    candidate = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    operator = read_json(OPERATOR_CHECKLIST) if OPERATOR_CHECKLIST.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    pilot_packet = read_json(PILOT_PACKET) if PILOT_PACKET.exists() else {}

    evidence_packet = {
        "version": "controlled_pilot_evidence_packet_template.v0.1",
        "phase": PHASE,
        "status": "TEMPLATE_ONLY_NO_REAL_SESSION_DATA",
        "real_data_captured_in_this_phase": False,
        "fields": {field: None for field in EVIDENCE_FIELDS},
        "required_refs_only": True,
        "raw_private_data_allowed": False,
        "secret_storage_allowed": False,
        "unredacted_pii_allowed": False,
        "review_decisions": REVIEW_DECISIONS,
        "default_decision_gate": "HOLD_TEMPLATE_NO_REAL_DATA",
        "claim_boundary": "evidence packet template only no real-world claim"
    }

    reviewer_queue = {
        "version": "controlled_pilot_reviewer_queue_empty.v0.1",
        "phase": PHASE,
        "queue_id": "REVIEWER-QUEUE-EMPTY-CONTROLLED-PILOT-V0-1",
        "queue_status": "EMPTY_READY_FOR_MANUAL_REVIEW_PREPARATION",
        "reviewer_assignment_status": "not_assigned_template_only",
        "pending_count": 0,
        "accepted_count": 0,
        "rejected_count": 0,
        "held_count": 0,
        "items": [],
        "review_decisions": REVIEW_DECISIONS,
        "real_data_captured_in_this_phase": False,
        "claim_boundary": "empty reviewer queue only no real session data"
    }

    spec = {
        "version": "controlled_pilot_evidence_packet_reviewer_queue.v0.1",
        "phase": PHASE,
        "purpose": "Create evidence packet template and empty reviewer queue for controlled pilot candidates.",
        "real_data_captured_in_this_phase": False,
        "evidence_fields": EVIDENCE_FIELDS,
        "queue_fields": QUEUE_FIELDS,
        "review_decisions": REVIEW_DECISIONS,
        "evidence_packet_template": "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json",
        "reviewer_queue": "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json",
        "acceptance_rule": "A candidate can enter calibration only after evidence packet refs, privacy review, PII redaction, secret scan, human reviewer notes, claim boundary and decision gate are present.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3541..3580 - Controlled Pilot Dataset Candidate Validator"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_evidence_packet_reviewer_queue",
        "real_data_captured_in_this_phase": False,
        "template_only": True,
        "reviewer_queue_empty": True,
        "refs_only_required": True,
        "human_review_required": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3501..3540 - Controlled Pilot Evidence Packet and Reviewer Queue

Creates the evidence packet template and empty reviewer queue for controlled pilot candidates.

This phase does not capture real session data.

The evidence packet uses references only and requires privacy review, PII redaction, secret scan, human reviewer notes, claim boundary and decision gate before any dataset acceptance.

Boundary: template and empty queue only. No raw private data, secrets, unredacted PII, production activation or real-world/client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(EVIDENCE_PACKET, evidence_packet)
    write_json(REVIEWER_QUEUE, reviewer_queue)

    candidate_fields = set(candidate.keys())
    operator_checks = {c.get("name") for c in operator.get("checks", [])}
    schema_required = schema.get("required", [])
    pilot_scope = pilot_packet.get("pilot_scope", {})

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_real_data_false": prev_out.get("real_data_captured_in_this_phase") is False,
        "execution_runbook_exists": EXEC_RUNBOOK.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "operator_checklist_exists": OPERATOR_CHECKLIST.exists(),
        "schema_exists": SCHEMA.exists(),
        "pilot_packet_exists": PILOT_PACKET.exists(),
        "schema_required_count": len(schema_required),
        "candidate_has_session_id": "session_id" in candidate_fields,
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "operator_has_dataset_gate": "dataset_gate_applied" in operator_checks,
        "pilot_target_sessions_present": pilot_scope.get("target_session_count", 0) >= 10,
        "evidence_field_count": len(EVIDENCE_FIELDS),
        "queue_field_count": len(QUEUE_FIELDS),
        "review_decision_count": len(REVIEW_DECISIONS),
        "evidence_packet_template_only": evidence_packet["status"] == "TEMPLATE_ONLY_NO_REAL_SESSION_DATA",
        "evidence_refs_only": evidence_packet["required_refs_only"] is True,
        "reviewer_queue_empty": reviewer_queue["items"] == [],
        "queue_pending_zero": reviewer_queue["pending_count"] == 0,
        "queue_accepted_zero": reviewer_queue["accepted_count"] == 0,
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "contract_refs_only": contract["refs_only_required"] is True,
        "contract_human_review_required": contract["human_review_required"] is True,
        "has_accept_decision": "ACCEPT_AS_CALIBRATION_CANDIDATE" in REVIEW_DECISIONS,
        "has_reject_decision": "REJECT_PRIVACY_OR_SECRET_RISK" in REVIEW_DECISIONS,
        "has_hold_evidence_decision": "HOLD_FOR_MISSING_EVIDENCE" in REVIEW_DECISIONS,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "client_claim_blocked": "client_facing_value_claim" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["evidence_field_count"] < 16:
        errors.append("evidence_field_count below 16")
    if checks["queue_field_count"] < 8:
        errors.append("queue_field_count below 8")
    if checks["review_decision_count"] < 5:
        errors.append("review_decision_count below 5")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_EVIDENCE_PACKET_REVIEWER_QUEUE_READY" if status == "PASS" else "CONTROLLED_PILOT_EVIDENCE_PACKET_REVIEWER_QUEUE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_packet_template": "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json",
        "reviewer_queue": "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json",
        "evidence_field_count": len(EVIDENCE_FIELDS),
        "queue_field_count": len(QUEUE_FIELDS),
        "review_decision_count": len(REVIEW_DECISIONS),
        "reviewer_queue_pending_count": reviewer_queue["pending_count"],
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3501..3540 Controlled Pilot Evidence Packet and Reviewer Queue",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Evidence fields: `{len(EVIDENCE_FIELDS)}`",
        f"- Queue fields: `{len(QUEUE_FIELDS)}`",
        f"- Review decisions: `{len(REVIEW_DECISIONS)}`",
        f"- Queue pending: `{reviewer_queue['pending_count']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Evidence packet template and empty reviewer queue only.",
        "- No real session data captured.",
        "- References only.",
        "- No validated real-world claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("evidence_fields:", len(EVIDENCE_FIELDS))
    print("queue_fields:", len(QUEUE_FIELDS))
    print("review_decisions:", len(REVIEW_DECISIONS))
    print("queue_pending:", reviewer_queue["pending_count"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
