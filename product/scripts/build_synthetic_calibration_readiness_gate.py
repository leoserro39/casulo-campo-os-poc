#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3341..3380"
REQ_TAG = "product-synthetic-calibration-dry-run-evaluator-v0.1"

EVAL_OUT = ROOT / "outputs/prod3301_3340_synthetic_calibration_dry_run_evaluator.json"
EVALUATOR = ROOT / "product/memory/synthetic_calibration_dry_run_evaluator_v0_1.json"
DRY_BATCH = ROOT / "product/calibration/synthetic_sessions/synthetic_calibration_dry_run_batch_v0_1.json"
REAL_EMPTY_BATCH = ROOT / "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json"
PLAN = ROOT / "product/memory/calibration_plan_real_sessions_v0_1.json"

DOC = ROOT / "docs/product/585_SYNTHETIC_CALIBRATION_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/synthetic_calibration_readiness_gate.contract.json"
GATE = ROOT / "product/memory/synthetic_calibration_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3341_3380_synthetic_calibration_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod3341_3380_synthetic_calibration_readiness_gate.md"

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
    "controlled_real_session_pilot_preparation",
    "human_review_packet_preparation",
    "sanitized_source_reference_protocol",
    "pilot_acceptance_criteria_definition",
    "calibration_evidence_protocol_definition"
]

PILOT_EXIT_CRITERIA = [
    "privacy_review_passed",
    "pii_redaction_passed",
    "secret_scan_passed",
    "source_refs_only_confirmed",
    "human_reviewer_assigned",
    "claim_boundary_confirmed",
    "baseline_vs_exocortex_protocol_confirmed",
    "dataset_acceptance_gate_defined"
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

    eval_out = read_json(EVAL_OUT) if EVAL_OUT.exists() else {}
    evaluator = read_json(EVALUATOR) if EVALUATOR.exists() else {}
    dry_batch = read_json(DRY_BATCH) if DRY_BATCH.exists() else {}
    real_empty_batch = read_json(REAL_EMPTY_BATCH) if REAL_EMPTY_BATCH.exists() else {}
    plan = read_json(PLAN) if PLAN.exists() else {}

    readiness_score = float(eval_out.get("synthetic_calibration_readiness_score", 0))
    readiness_band = eval_out.get("synthetic_calibration_readiness_band")
    correlations = eval_out.get("correlations", {})

    decision = "APPROVED_FOR_CONTROLLED_REAL_SESSION_PILOT_PREPARATION_ONLY"
    if readiness_score < 80 or readiness_band != "SYNTHETIC_READY_STRONG":
        decision = "HOLD_SYNTHETIC_CALIBRATION_REVIEW"
    if eval_out.get("real_data_captured") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "synthetic_calibration_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "scope": "Preparation only for controlled real-session pilot. No real session capture in this phase.",
        "synthetic_readiness": {
            "readiness_score": readiness_score,
            "readiness_band": readiness_band,
            "record_count": eval_out.get("record_count"),
            "correlations": correlations
        },
        "interpretation": {
            "synthetic_result": "Pipeline signals are internally coherent under synthetic data.",
            "not_evidence_of": [
                "real_world_savings",
                "real_world_profit",
                "validated_hallucination_reduction",
                "client_value",
                "production_readiness"
            ],
            "next_allowed_step": "Prepare controlled real-session pilot packet with human review and privacy controls."
        },
        "pilot_exit_criteria": PILOT_EXIT_CRITERIA,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3381..3420 - Controlled Real Session Pilot Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "synthetic_calibration_readiness_gate",
        "real_data_captured": False,
        "synthetic_only": True,
        "pilot_preparation_only": True,
        "real_capture_still_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-3341..3380 - Synthetic Calibration Readiness Gate

Defines the readiness gate after the synthetic calibration dry run evaluator.

The synthetic dry run is strong enough to prepare a controlled real-session pilot packet, but it does not authorize real capture in this phase.

Boundary: synthetic readiness gate only. No real session data, no production activation, no client-facing claim, no validated savings and no validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "evaluator_output_exists": EVAL_OUT.exists(),
        "evaluator_output_pass": eval_out.get("status") == "PASS",
        "evaluator_exists": EVALUATOR.exists(),
        "dry_batch_exists": DRY_BATCH.exists(),
        "real_empty_batch_exists": REAL_EMPTY_BATCH.exists(),
        "plan_exists": PLAN.exists(),
        "evaluator_real_data_false": eval_out.get("real_data_captured") is False,
        "dry_batch_real_data_false": dry_batch.get("real_data_captured") is False,
        "real_empty_batch_record_count_zero": real_empty_batch.get("record_count") == 0,
        "readiness_score_strong": readiness_score >= 80,
        "readiness_band_strong": readiness_band == "SYNTHETIC_READY_STRONG",
        "apex_hallucination_negative": correlations.get("apex_vs_hallucination", 0) < 0,
        "complexity_hallucination_positive": correlations.get("complexity_vs_hallucination", 0) > 0,
        "cost_hallucination_positive": correlations.get("cost_vs_hallucination", 0) > 0,
        "input_hallucination_negative": correlations.get("input_quality_vs_hallucination", 0) < 0,
        "minimum_plan_sessions_present": plan.get("minimum_viable_calibration_sessions", 0) >= 30,
        "pilot_exit_criteria_count": len(PILOT_EXIT_CRITERIA),
        "has_privacy_exit": "privacy_review_passed" in PILOT_EXIT_CRITERIA,
        "has_pii_exit": "pii_redaction_passed" in PILOT_EXIT_CRITERIA,
        "has_secret_exit": "secret_scan_passed" in PILOT_EXIT_CRITERIA,
        "has_source_refs_exit": "source_refs_only_confirmed" in PILOT_EXIT_CRITERIA,
        "has_human_reviewer_exit": "human_reviewer_assigned" in PILOT_EXIT_CRITERIA,
        "decision_is_preparation_only": decision == "APPROVED_FOR_CONTROLLED_REAL_SESSION_PILOT_PREPARATION_ONLY",
        "real_capture_still_blocked": "real_session_data_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED,
        "commercial_pricing_blocked": "commercial_package_pricing_claim" in BLOCKED
    }

    if checks["pilot_exit_criteria_count"] < 8:
        errors.append("pilot_exit_criteria_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "SYNTHETIC_CALIBRATION_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate": "product/memory/synthetic_calibration_readiness_gate_v0_1.json",
        "synthetic_calibration_readiness_score": readiness_score,
        "synthetic_calibration_readiness_band": readiness_band,
        "real_data_captured": False,
        "pilot_exit_criteria_count": len(PILOT_EXIT_CRITERIA),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3341..3380 Synthetic Calibration Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Synthetic readiness score: `{readiness_score}`",
        f"- Synthetic readiness band: `{readiness_band}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Synthetic readiness only.",
        "- Real capture remains blocked.",
        "- Next step is pilot packet preparation only.",
        "- No validated savings, ROI or hallucination-reduction claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_score:", readiness_score)
    print("readiness_band:", readiness_band)
    print("real_data_captured:", result["real_data_captured"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
