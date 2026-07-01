#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3381..3420"
REQ_TAG = "product-synthetic-calibration-readiness-gate-v0.1"

GATE_OUT = ROOT / "outputs/prod3341_3380_synthetic_calibration_readiness_gate.json"
GATE = ROOT / "product/memory/synthetic_calibration_readiness_gate_v0_1.json"
REAL_SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
EMPTY_INTAKE = ROOT / "product/calibration/real_sessions/real_session_empty_intake_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/manual_capture_runbook_v0_1.md"
CHECKLIST = ROOT / "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json"

DOC = ROOT / "docs/product/586_CONTROLLED_REAL_SESSION_PILOT_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_real_session_pilot_packet.contract.json"
PACKET = ROOT / "product/memory/controlled_real_session_pilot_packet_v0_1.json"
PILOT_PACKET = ROOT / "product/calibration/real_sessions/controlled_real_session_pilot_packet_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3381_3420_controlled_real_session_pilot_packet.json"
OUT_MD = ROOT / "outputs/prod3381_3420_controlled_real_session_pilot_packet.md"

BLOCKED = [
    "real_session_data_capture",
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
    "controlled_real_session_pilot_packet_creation",
    "pilot_scope_definition",
    "human_reviewer_assignment_template",
    "privacy_protocol_preparation",
    "source_reference_protocol_preparation",
    "pilot_acceptance_criteria_preparation"
]

PILOT_SCOPE = {
    "pilot_id": "PILOT-001-CONTROLLED-REAL-SESSION-PREPARATION",
    "status": "PREPARATION_ONLY_NO_REAL_CAPTURE",
    "target_session_count": 10,
    "minimum_accepted_sessions": 5,
    "allowed_chat_layers": [
        "ANALYSIS_CHAT",
        "PROJECT_CHAT",
        "GOVERNANCE_CHAT",
        "CALIBRATION_CHAT",
        "EVIDENCE_AUDIT_CHAT"
    ],
    "excluded_chat_layers": [
        "PRODUCTION_ACTIVATION_CHAT",
        "CLIENT_CLAIM_CHAT",
        "SECRET_HANDLING_CHAT"
    ],
    "comparison_modes": [
        "PURE_CHAT_BASELINE",
        "CASULO_EXOCORTEX_ASSISTED"
    ]
}

REQUIRED_EXIT_CRITERIA = [
    "privacy_review_passed",
    "pii_redaction_passed",
    "secret_scan_passed",
    "source_refs_only_confirmed",
    "human_reviewer_assigned",
    "claim_boundary_confirmed",
    "baseline_vs_exocortex_protocol_confirmed",
    "dataset_acceptance_gate_defined",
    "no_client_facing_claim_confirmed",
    "no_production_activation_confirmed"
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
    gate_out = read_json(GATE_OUT) if GATE_OUT.exists() else {}
    gate = read_json(GATE) if GATE.exists() else {}
    schema = read_json(REAL_SCHEMA) if REAL_SCHEMA.exists() else {}
    empty_intake = read_json(EMPTY_INTAKE) if EMPTY_INTAKE.exists() else {}
    checklist = read_json(CHECKLIST) if CHECKLIST.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}

    prior_exit = set(gate.get("pilot_exit_criteria", []))
    checklist_names = {c.get("name") for c in checklist.get("checks", [])}
    schema_required = schema.get("required", [])

    pilot_packet = {
        "version": "controlled_real_session_pilot_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare the first controlled real-session pilot packet without capturing real data.",
        "real_data_captured": False,
        "pilot_scope": PILOT_SCOPE,
        "required_exit_criteria": REQUIRED_EXIT_CRITERIA,
        "human_review": {
            "required": True,
            "reviewer_status": "not_assigned_template_only",
            "reviewer_must_confirm": [
                "source references only",
                "PII redaction",
                "secret scan",
                "claim boundary",
                "decision gate",
                "dataset acceptance or rejection"
            ]
        },
        "privacy_protocol": {
            "source_refs_only": True,
            "raw_private_data_allowed": False,
            "secrets_allowed": False,
            "unredacted_pii_allowed": False
        },
        "dataset_acceptance": {
            "default_gate": "HOLD_PILOT_PREPARATION_NO_REAL_CAPTURE",
            "acceptance_requires": REQUIRED_EXIT_CRITERIA,
            "record_count": 0
        },
        "claim_boundary": "Pilot packet preparation only. No real session data captured. No real-world or client-facing claim.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3421..3460 - Controlled Real Session Pilot Readiness Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_real_session_pilot_packet_preparation",
        "real_data_captured": False,
        "pilot_preparation_only": True,
        "human_review_required": True,
        "privacy_controls_required": True,
        "real_capture_still_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": pilot_packet["recommended_next_phase"]
    }

    doc = """# PROD-3381..3420 - Controlled Real Session Pilot Packet

Prepares the controlled real-session pilot packet.

This phase does not capture real session data.

The packet defines pilot scope, allowed chat layers, excluded risky layers, human review requirements, privacy controls, source-reference-only protocol, dataset acceptance gate and claim boundary.

Boundary: preparation only. Real capture remains blocked.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(PACKET, pilot_packet)
    write_json(PILOT_PACKET, pilot_packet)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "gate_output_exists": GATE_OUT.exists(),
        "gate_output_pass": gate_out.get("status") == "PASS",
        "gate_decision_preparation_only": gate_out.get("decision") == "APPROVED_FOR_CONTROLLED_REAL_SESSION_PILOT_PREPARATION_ONLY",
        "gate_real_data_false": gate_out.get("real_data_captured") is False,
        "gate_exists": GATE.exists(),
        "schema_exists": REAL_SCHEMA.exists(),
        "empty_intake_exists": EMPTY_INTAKE.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "checklist_exists": CHECKLIST.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "schema_required_count": len(schema_required),
        "empty_intake_is_template": empty_intake.get("capture_status") == "EMPTY_TEMPLATE",
        "empty_batch_record_count_zero": empty_batch.get("record_count") == 0,
        "pilot_target_session_count_positive": PILOT_SCOPE["target_session_count"] > 0,
        "allowed_layer_count": len(PILOT_SCOPE["allowed_chat_layers"]),
        "excluded_layer_count": len(PILOT_SCOPE["excluded_chat_layers"]),
        "exit_criteria_count": len(REQUIRED_EXIT_CRITERIA),
        "prior_exit_criteria_preserved": prior_exit.issubset(set(REQUIRED_EXIT_CRITERIA)),
        "has_privacy_exit": "privacy_review_passed" in REQUIRED_EXIT_CRITERIA,
        "has_pii_exit": "pii_redaction_passed" in REQUIRED_EXIT_CRITERIA,
        "has_secret_exit": "secret_scan_passed" in REQUIRED_EXIT_CRITERIA,
        "has_source_refs_exit": "source_refs_only_confirmed" in REQUIRED_EXIT_CRITERIA,
        "has_no_client_claim_exit": "no_client_facing_claim_confirmed" in REQUIRED_EXIT_CRITERIA,
        "has_no_production_exit": "no_production_activation_confirmed" in REQUIRED_EXIT_CRITERIA,
        "checklist_has_source_refs": "source_refs_only" in checklist_names,
        "checklist_has_secret_scan": "secret_scan_completed" in checklist_names,
        "real_data_not_captured": contract["real_data_captured"] is False,
        "pilot_preparation_only": contract["pilot_preparation_only"] is True,
        "real_capture_still_blocked": "real_session_data_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "client_claim_blocked": "client_facing_value_claim" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["allowed_layer_count"] < 5:
        errors.append("allowed_layer_count below 5")
    if checks["exit_criteria_count"] < 10:
        errors.append("exit_criteria_count below 10")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_REAL_SESSION_PILOT_PACKET_READY" if status == "PASS" else "CONTROLLED_REAL_SESSION_PILOT_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packet": "product/calibration/real_sessions/controlled_real_session_pilot_packet_v0_1.json",
        "target_session_count": PILOT_SCOPE["target_session_count"],
        "minimum_accepted_sessions": PILOT_SCOPE["minimum_accepted_sessions"],
        "real_data_captured": False,
        "exit_criteria_count": len(REQUIRED_EXIT_CRITERIA),
        "recommended_next_phase": pilot_packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3381..3420 Controlled Real Session Pilot Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Target sessions: `{PILOT_SCOPE['target_session_count']}`",
        f"- Minimum accepted sessions: `{PILOT_SCOPE['minimum_accepted_sessions']}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Exit criteria: `{len(REQUIRED_EXIT_CRITERIA)}`",
        f"- Next: `{pilot_packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Pilot packet preparation only.",
        "- Real capture remains blocked.",
        "- No client-facing or real-world claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("target_sessions:", PILOT_SCOPE["target_session_count"])
    print("minimum_accepted:", PILOT_SCOPE["minimum_accepted_sessions"])
    print("real_data_captured:", result["real_data_captured"])
    print("exit_criteria:", len(REQUIRED_EXIT_CRITERIA))
    print("next:", pilot_packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
