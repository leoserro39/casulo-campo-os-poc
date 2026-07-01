#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3461..3500"
REQ_TAG = "product-controlled-real-session-pilot-readiness-gate-v0.1"

GATE_OUT = ROOT / "outputs/prod3421_3460_controlled_real_session_pilot_readiness_gate.json"
GATE = ROOT / "product/memory/controlled_real_session_pilot_readiness_gate_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/controlled_real_session_pilot_packet_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
EMPTY_INTAKE = ROOT / "product/calibration/real_sessions/real_session_empty_intake_v0_1.json"
CHECKLIST_PREV = ROOT / "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json"

DOC = ROOT / "docs/product/588_CONTROLLED_REAL_SESSION_PILOT_EXECUTION_RUNBOOK.md"
CONTRACT = ROOT / "product/contracts/controlled_real_session_pilot_execution_runbook.contract.json"
SPEC = ROOT / "product/memory/controlled_real_session_pilot_execution_runbook_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_real_session_pilot_execution_runbook_v0_1.md"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
OPERATOR_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_real_session_operator_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3461_3500_controlled_real_session_pilot_execution_runbook.json"
OUT_MD = ROOT / "outputs/prod3461_3500_controlled_real_session_pilot_execution_runbook.md"

EXECUTION_STEPS = [
    "confirm_manual_controlled_scope",
    "assign_human_reviewer",
    "copy_candidate_template",
    "assign_session_id",
    "classify_chat_layer",
    "classify_work_type",
    "capture_source_references_only",
    "redact_pii_before_any_storage",
    "run_secret_scan_before_any_storage",
    "capture_baseline_vs_exocortex_scores",
    "score_apex_value_delta_cost_hallucination",
    "attach_evidence_pointers_only",
    "write_human_reviewer_notes",
    "apply_dataset_acceptance_gate",
    "accept_reject_or_hold_candidate"
]

ABORT_TRIGGERS = [
    "raw_private_data_detected",
    "secret_or_credential_detected",
    "unredacted_pii_detected",
    "automatic_capture_attempted",
    "human_reviewer_missing",
    "source_refs_not_available",
    "client_facing_claim_requested",
    "production_activation_requested",
    "commercial_pricing_claim_requested",
    "claim_boundary_unclear"
]

OPERATOR_CHECKS = [
    "manual_scope_confirmed",
    "reviewer_assigned",
    "candidate_template_copied",
    "session_id_assigned",
    "chat_layer_classified",
    "work_type_classified",
    "source_refs_only_confirmed",
    "pii_redaction_completed",
    "secret_scan_completed",
    "baseline_vs_exocortex_protocol_followed",
    "scores_completed",
    "evidence_pointers_attached",
    "reviewer_notes_present",
    "claim_boundary_confirmed",
    "dataset_gate_applied"
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
    "controlled_pilot_execution_runbook_creation",
    "candidate_template_creation",
    "operator_checklist_creation",
    "manual_source_reference_protocol",
    "human_review_queue_preparation"
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

def empty_candidate(required_fields):
    defaults = {
        "session_id": "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "capture_status": "EMPTY_TEMPLATE",
        "chat_platform": "",
        "chat_layer": "",
        "work_type": "",
        "baseline_chat_mode": "",
        "casulo_exocortex_mode": "",
        "input_quality_score": None,
        "implementation_complexity_score": None,
        "operational_cost_score": None,
        "apex_maturity_score": None,
        "hallucination_risk_index": None,
        "value_delta_estimate": None,
        "rework_count": None,
        "time_spent_minutes": None,
        "evidence_pointers": [],
        "human_reviewer_notes": [],
        "claim_boundary": "candidate_template_only_no_real_claim",
        "decision_gate": "HOLD_TEMPLATE_NO_REAL_DATA",
        "privacy_review_status": "pending_before_real_candidate",
        "pii_redaction_status": "pending_before_real_candidate",
        "secret_scan_status": "pending_before_real_candidate",
        "source_refs_only": True
    }
    candidate = {f: defaults.get(f, None) for f in required_fields}
    candidate["template_boundary"] = "No real session data captured by this template."
    candidate["automatic_capture_allowed"] = False
    return candidate

def main():
    errors = []

    gate_out = read_json(GATE_OUT) if GATE_OUT.exists() else {}
    gate = read_json(GATE) if GATE.exists() else {}
    packet = read_json(PACKET) if PACKET.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    empty_intake = read_json(EMPTY_INTAKE) if EMPTY_INTAKE.exists() else {}
    checklist_prev = read_json(CHECKLIST_PREV) if CHECKLIST_PREV.exists() else {}

    schema_required = schema.get("required", [])
    candidate = empty_candidate(schema_required)

    operator_checklist = {
        "version": "controlled_real_session_operator_checklist.v0.1",
        "phase": PHASE,
        "status": "TEMPLATE_ONLY_NO_REAL_SESSION_DATA",
        "checks": [
            {"id": f"OP-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(OPERATOR_CHECKS)
        ],
        "abort_triggers": ABORT_TRIGGERS,
        "blocked_actions": BLOCKED
    }

    runbook_text = """# Controlled Real Session Pilot Execution Runbook v0.1

Boundary: manual controlled pilot execution only.

This runbook does not capture real session data by itself.

Execution rules:
1. Confirm manual controlled scope.
2. Assign a human reviewer.
3. Copy the candidate template.
4. Assign session_id.
5. Classify chat_layer and work_type.
6. Store source references only.
7. Redact PII before any storage.
8. Run secret scan before any storage.
9. Capture baseline vs CASULO Exocortex scores manually.
10. Score Apex, Value Delta, operational cost and hallucination risk.
11. Attach evidence pointers only.
12. Add human reviewer notes.
13. Apply dataset acceptance gate.
14. Accept, reject or hold candidate.

Abort immediately if raw private data, secrets, unredacted PII, automatic capture, missing reviewer, client-facing claim, production activation or commercial pricing claim appears.
"""

    spec = {
        "version": "controlled_real_session_pilot_execution_runbook.v0.1",
        "phase": PHASE,
        "purpose": "Define manual execution runbook for controlled real-session pilot candidates.",
        "real_data_captured_in_this_phase": False,
        "execution_steps": EXECUTION_STEPS,
        "abort_triggers": ABORT_TRIGGERS,
        "operator_checks": OPERATOR_CHECKS,
        "candidate_template": "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json",
        "operator_checklist": "product/calibration/real_sessions/controlled_real_session_operator_checklist_v0_1.json",
        "runbook": "product/calibration/real_sessions/controlled_real_session_pilot_execution_runbook_v0_1.md",
        "dataset_acceptance_gate": "ACCEPT_REJECT_OR_HOLD_AFTER_HUMAN_REVIEW",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3501..3540 - Controlled Pilot Evidence Packet and Reviewer Queue"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_real_session_pilot_execution_runbook",
        "real_data_captured_in_this_phase": False,
        "manual_execution_only": True,
        "automatic_capture_blocked": True,
        "human_review_required": True,
        "source_refs_only_required": True,
        "abort_triggers_required": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3461..3500 - Controlled Real Session Pilot Execution Runbook

Defines the manual execution runbook for controlled real-session pilot candidates.

This phase creates the runbook, operator checklist and candidate template. It does not capture real session data.

Execution remains manual, source-reference-only, privacy-reviewed, PII-redacted, secret-scanned and human-reviewed.

Boundary: no automatic capture, no raw private data, no secrets, no unredacted PII, no production activation and no client-facing or validated real-world claim.
"""

    write(DOC, doc)
    write(RUNBOOK, runbook_text)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(CANDIDATE_TEMPLATE, candidate)
    write_json(OPERATOR_CHECKLIST, operator_checklist)

    candidate_fields = set(candidate.keys())
    checklist_names = {c["name"] for c in operator_checklist["checks"]}
    gate_allowed = set(gate.get("allowed_actions", []))
    gate_blocked = set(gate.get("blocked_actions", []))
    prior_packet_scope = packet.get("pilot_scope", {})

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "gate_output_exists": GATE_OUT.exists(),
        "gate_output_pass": gate_out.get("status") == "PASS",
        "gate_decision_manual_execution_only": gate_out.get("decision") == "APPROVED_FOR_MANUAL_CONTROLLED_REAL_SESSION_PILOT_EXECUTION_ONLY",
        "gate_real_data_false": gate_out.get("real_data_captured_in_this_phase") is False,
        "gate_exists": GATE.exists(),
        "packet_exists": PACKET.exists(),
        "schema_exists": SCHEMA.exists(),
        "empty_intake_exists": EMPTY_INTAKE.exists(),
        "previous_checklist_exists": CHECKLIST_PREV.exists(),
        "schema_required_count": len(schema_required),
        "candidate_has_all_required_fields": set(schema_required).issubset(candidate_fields),
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "candidate_no_evidence": candidate.get("evidence_pointers") == [],
        "candidate_no_reviewer_notes": candidate.get("human_reviewer_notes") == [],
        "candidate_no_real_data": candidate.get("session_id") == "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "candidate_automatic_capture_blocked": candidate.get("automatic_capture_allowed") is False,
        "empty_intake_template": empty_intake.get("capture_status") == "EMPTY_TEMPLATE",
        "execution_step_count": len(EXECUTION_STEPS),
        "abort_trigger_count": len(ABORT_TRIGGERS),
        "operator_check_count": len(OPERATOR_CHECKS),
        "has_source_refs_check": "source_refs_only_confirmed" in checklist_names,
        "has_pii_check": "pii_redaction_completed" in checklist_names,
        "has_secret_check": "secret_scan_completed" in checklist_names,
        "has_dataset_gate_check": "dataset_gate_applied" in checklist_names,
        "prior_target_sessions_present": prior_packet_scope.get("target_session_count", 0) >= 10,
        "gate_allowed_manual_source_refs": "manual_sanitized_source_reference_capture" in gate_allowed,
        "gate_blocks_raw_private": "raw_private_data_storage" in gate_blocked,
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "manual_execution_only": contract["manual_execution_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "client_claim_blocked": "client_facing_value_claim" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["execution_step_count"] < 15:
        errors.append("execution_step_count below 15")
    if checks["abort_trigger_count"] < 10:
        errors.append("abort_trigger_count below 10")
    if checks["operator_check_count"] < 15:
        errors.append("operator_check_count below 15")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_REAL_SESSION_PILOT_EXECUTION_RUNBOOK_READY" if status == "PASS" else "CONTROLLED_REAL_SESSION_PILOT_EXECUTION_RUNBOOK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runbook": "product/calibration/real_sessions/controlled_real_session_pilot_execution_runbook_v0_1.md",
        "candidate_template": "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json",
        "operator_checklist": "product/calibration/real_sessions/controlled_real_session_operator_checklist_v0_1.json",
        "execution_step_count": len(EXECUTION_STEPS),
        "abort_trigger_count": len(ABORT_TRIGGERS),
        "operator_check_count": len(OPERATOR_CHECKS),
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3461..3500 Controlled Real Session Pilot Execution Runbook",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Execution steps: `{len(EXECUTION_STEPS)}`",
        f"- Abort triggers: `{len(ABORT_TRIGGERS)}`",
        f"- Operator checks: `{len(OPERATOR_CHECKS)}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Manual controlled execution runbook only.",
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
    print("execution_steps:", len(EXECUTION_STEPS))
    print("abort_triggers:", len(ABORT_TRIGGERS))
    print("operator_checks:", len(OPERATOR_CHECKS))
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
