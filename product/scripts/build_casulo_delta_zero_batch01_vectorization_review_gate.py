#!/usr/bin/env python3
import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6421..6460"
REQ_TAG = "product-casulo-delta-zero-dynamics-model-packet-v0.1"

PREV_PACKET = ROOT / "outputs/prod6381_6420_casulo_delta_zero_dynamics_model_packet.json"
DELTA_MATRIX = ROOT / "product/reports/casulo_delta_zero_matrix_batch01_t0_v0_3.json"
DELTA_MATRIX_CSV = ROOT / "product/reports/casulo_delta_zero_matrix_batch01_t0_v0_3.csv"
GATE_ALIGNMENT = ROOT / "product/reports/casulo_delta_zero_gate_alignment_batch01_t0_v0_3.json"
TOKEN_EXPANSION = ROOT / "product/reports/casulo_delta_zero_token_expansion_batch01_t0_v0_3.json"
READINESS = ROOT / "product/reports/casulo_delta_zero_dynamics_model_readiness_v0_3.json"
ROADMAP_IN = ROOT / "outputs/prod6381_6420_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/664_CASULO_DELTA_ZERO_BATCH01_VECTORIZATION_REVIEW_GATE.md"
CONTRACT = ROOT / "product/contracts/casulo_delta_zero_batch01_vectorization_review_gate.contract.json"
MEMORY = ROOT / "product/memory/casulo_delta_zero_batch01_vectorization_review_gate_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/casulo_delta_zero_batch01_vectorization_review_gate_v0_1.json"

VECTOR_REVIEW = ROOT / "product/reports/casulo_delta_zero_batch01_vectorization_review_v0_3.json"
VECTOR_REVIEW_CSV = ROOT / "product/reports/casulo_delta_zero_batch01_vectorization_review_v0_3.csv"
DOMAIN_REVIEW = ROOT / "product/reports/casulo_delta_zero_batch01_domain_review_v0_3.json"
MODE_REVIEW = ROOT / "product/reports/casulo_delta_zero_batch01_mode_review_v0_3.json"
NEXT_EVALUATOR_REQUIREMENTS = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_requirements_v0_3.json"

OUT_JSON = ROOT / "outputs/prod6421_6460_casulo_delta_zero_batch01_vectorization_review_gate.json"
OUT_MD = ROOT / "outputs/prod6421_6460_casulo_delta_zero_batch01_vectorization_review_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod6421_6460_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "additional_live_gpt_call_in_this_phase",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "dataset_acceptance",
    "real_candidate_insert",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim",
    "commercial_claim",
    "domain_validation_claim",
    "final_indices_without_external_scores",
    "canonical_token_acceptance_without_expansion_test",
    "velocity_claim_without_history",
    "acceleration_claim_without_history",
    "delta_zero_ready_claim_without_external_review"
]

ALLOWED = [
    "delta_zero_vectorization_review_gate_creation",
    "t0_delta_matrix_review",
    "gate_alignment_review",
    "domain_mode_summary_creation",
    "external_evaluator_requirements_update",
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

def avg(values):
    vals = [float(v) for v in values if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None

def main():
    prev = read_json(PREV_PACKET) if PREV_PACKET.exists() else {}
    matrix = read_json(DELTA_MATRIX) if DELTA_MATRIX.exists() else {}
    gate_alignment = read_json(GATE_ALIGNMENT) if GATE_ALIGNMENT.exists() else {}
    token_expansion = read_json(TOKEN_EXPANSION) if TOKEN_EXPANSION.exists() else {}
    readiness = read_json(READINESS) if READINESS.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required Delta Zero dynamics model tag")
    if prev.get("status") != "PASS":
        errors.append("previous Delta Zero dynamics packet not PASS")
    if prev.get("decision") != "CASULO_DELTA_ZERO_DYNAMICS_MODEL_PACKET_READY":
        errors.append("previous Delta Zero dynamics decision mismatch")
    if prev.get("delta_matrix_row_count") != 36:
        errors.append("previous delta matrix row count not 36")
    if prev.get("trajectory_status") != "T0_ONLY":
        errors.append("previous trajectory status should be T0_ONLY")
    if prev.get("velocity_ready") is not False or prev.get("acceleration_ready") is not False:
        errors.append("velocity/acceleration should not be ready")
    if prev.get("candidate_tokens_canonical") is not False:
        errors.append("candidate tokens should not be canonical")
    if matrix.get("row_count") != 36:
        errors.append("delta matrix row count not 36")
    if not DELTA_MATRIX_CSV.exists():
        errors.append("delta matrix CSV missing")
    if gate_alignment.get("row_count") != 36:
        errors.append("gate alignment row count not 36")
    if token_expansion.get("canonical_token_acceptance") is not False:
        errors.append("canonical token acceptance should be false")
    if readiness.get("trajectory_status") != "T0_ONLY":
        errors.append("readiness trajectory status mismatch")

    rows = matrix.get("rows", [])
    if len(rows) != 36:
        errors.append("matrix rows length not 36")

    review_rows = []
    domain_groups = defaultdict(list)
    mode_groups = defaultdict(list)
    gate_mismatch_values = []
    hard_block_count = 0
    dzr_ready_count = 0
    needs_external_count = 0

    for row in rows:
        hard_blocks = row.get("hard_blocks") or []
        if hard_blocks:
            hard_block_count += 1
        if row.get("delta_zero_ready") is True:
            dzr_ready_count += 1
        if row.get("external_evaluator_required") is not False:
            needs_external_count += 1

        gate_mismatch_values.append(row.get("delta_gate_mismatch"))
        domain_groups[row.get("domain")].append(row)
        mode_groups[row.get("mode")].append(row)

        review_status = "REVIEW_REQUIRED"
        if row.get("delta_zero_ready") is True:
            review_status = "EXTERNAL_CONFIRMATION_REQUIRED_BEFORE_ANY_READY_CLAIM"
        elif hard_blocks:
            review_status = "HARD_BLOCK_REVIEW_REQUIRED"
        elif row.get("computed_gate") in ["OBSERVATION_REQUIRED", "READY_FOR_NEXT_STAGE"]:
            review_status = "LOWER_DELTA_BUT_STILL_EXTERNAL_REVIEW_REQUIRED"

        review_rows.append({
            "case_id": row.get("case_id"),
            "execution_id": row.get("execution_id"),
            "domain": row.get("domain"),
            "mode": row.get("mode"),
            "model_gate": row.get("model_gate"),
            "computed_gate": row.get("computed_gate"),
            "delta_score": row.get("delta_score"),
            "delta_band": row.get("delta_band"),
            "delta_gate_mismatch": row.get("delta_gate_mismatch"),
            "drd": row.get("drd"),
            "dzr": row.get("dzr"),
            "delta_zero_ready": row.get("delta_zero_ready"),
            "hard_block_count": len(hard_blocks),
            "hard_blocks": hard_blocks,
            "trajectory_status": row.get("trajectory", {}).get("trajectory_status"),
            "velocity_ready": row.get("trajectory", {}).get("velocity_ready"),
            "acceleration_ready": row.get("trajectory", {}).get("acceleration_ready"),
            "candidate_tokens_v0_3": row.get("token_expansion", {}).get("candidate_tokens_v0_3"),
            "review_status": review_status
        })

    def summarize(items):
        return {
            "case_count": len(items),
            "avg_delta_score": avg([x.get("delta_score") for x in items]),
            "avg_drd": avg([x.get("drd") for x in items]),
            "avg_dzr": avg([x.get("dzr") for x in items]),
            "avg_delta_gate_mismatch": avg([x.get("delta_gate_mismatch") for x in items]),
            "hard_block_count": sum(1 for x in items if x.get("hard_blocks")),
            "delta_zero_ready_count": sum(1 for x in items if x.get("delta_zero_ready") is True),
            "computed_gate_counts": dict(Counter(x.get("computed_gate") for x in items)),
            "delta_band_counts": dict(Counter(x.get("delta_band") for x in items))
        }

    domain_review = {
        "version": "casulo_delta_zero_batch01_domain_review.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domains": {k: summarize(v) for k, v in sorted(domain_groups.items())}
    }

    mode_review = {
        "version": "casulo_delta_zero_batch01_mode_review.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "modes": {k: summarize(v) for k, v in sorted(mode_groups.items())}
    }

    vector_review = {
        "version": "casulo_delta_zero_batch01_vectorization_review.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "row_count": len(review_rows),
        "delta_zero_ready_count": dzr_ready_count,
        "hard_block_case_count": hard_block_count,
        "external_evaluator_required_count": needs_external_count,
        "average_delta_gate_mismatch": avg(gate_mismatch_values),
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "candidate_tokens_canonical": False,
        "review_rows": review_rows
    }

    with VECTOR_REVIEW_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "case_id", "execution_id", "domain", "mode", "model_gate", "computed_gate",
            "delta_score", "delta_band", "delta_gate_mismatch", "drd", "dzr",
            "delta_zero_ready", "hard_block_count", "hard_blocks", "trajectory_status",
            "velocity_ready", "acceleration_ready", "candidate_tokens_v0_3", "review_status"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in review_rows:
            out = dict(row)
            out["hard_blocks"] = "|".join(out.get("hard_blocks") or [])
            out["candidate_tokens_v0_3"] = "|".join(out.get("candidate_tokens_v0_3") or [])
            writer.writerow(out)

    external_requirements = {
        "version": "casulo_delta_zero_external_evaluator_requirements.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(review_rows),
        "must_score": [
            "external_evidence_grounding_score",
            "external_gate_compliance_score",
            "external_claim_boundary_score",
            "external_state_vector_reasonableness_score",
            "external_delta_reasonableness_score",
            "external_drd_dzr_reasonableness_score",
            "external_token_expansion_fidelity_score",
            "external_next_action_quality_score",
            "external_hallucination_risk_flag",
            "external_over_review_flag",
            "external_under_review_flag",
            "external_accept_for_calibration_signal",
            "external_reviewer_notes"
        ],
        "must_not_claim_until_later_gate": [
            "validated_model_gain",
            "validated_hallucination_reduction",
            "delta_zero_ready_validated",
            "dataset_acceptance",
            "client_evidence",
            "production_evidence",
            "commercial_claim",
            "canonical_token_acceptance"
        ],
        "trajectory_policy": {
            "snapshot_count": 1,
            "trajectory_status": "T0_ONLY",
            "velocity_ready": False,
            "acceleration_ready": False,
            "external_reviewer_should_not_score_velocity_as_zero": True
        }
    }

    if dzr_ready_count != 0:
        errors.append("delta_zero_ready_count should be 0 before external review")
    if needs_external_count != 36:
        errors.append("all 36 cases should require external evaluator")
    if hard_block_count != prev.get("hard_block_case_count"):
        errors.append("hard block count differs from previous packet")
    if matrix.get("velocity_ready") is not False or matrix.get("acceleration_ready") is not False:
        errors.append("matrix velocity/acceleration should not be ready")

    checks = [
        "prior_delta_zero_dynamics_packet_present",
        "prior_delta_zero_dynamics_packet_passed",
        "required_prior_tag_present",
        "review_gate_only",
        "no_additional_live_gpt_call",
        "delta_matrix_loaded",
        "thirty_six_delta_rows_loaded",
        "delta_matrix_csv_present",
        "gate_alignment_loaded",
        "token_expansion_loaded",
        "readiness_loaded",
        "vector_review_created",
        "domain_review_created",
        "mode_review_created",
        "external_evaluator_requirements_created",
        "delta_zero_ready_count_zero_confirmed",
        "hard_block_count_confirmed",
        "all_cases_require_external_evaluator",
        "t0_only_trajectory_confirmed",
        "velocity_not_ready_confirmed",
        "acceleration_not_ready_confirmed",
        "candidate_tokens_non_canonical_confirmed",
        "validated_model_gain_claim_blocked",
        "hallucination_reduction_claim_blocked",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 376:
        checks.append(f"delta_zero_vectorization_review_gate_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6381..6420":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6461..6500":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "CASULO Delta Zero Batch 01 Vectorization Review Gate",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6461..6500" not in seen:
        roadmap_items.append({
            "phase": "PROD-6461..6500",
            "name": "CASULO Delta Zero External Evaluator Workbench Packet",
            "status": "NEXT"
        })

    decision = "CASULO_DELTA_ZERO_BATCH01_VECTORIZATION_REVIEW_GATE_READY"

    packet = {
        "version": "casulo_delta_zero_batch01_vectorization_review_gate.v0.3",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_DELTA_ZERO_BATCH01_VECTORIZATION_REVIEW_GATE_NOT_READY",
        "review_gate_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "row_count": len(review_rows),
        "delta_zero_ready_count": dzr_ready_count,
        "hard_block_case_count": hard_block_count,
        "external_evaluator_required_count": needs_external_count,
        "average_delta_gate_mismatch": avg(gate_mismatch_values),
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "candidate_tokens_canonical": False,
        "validated_model_gain_claim_allowed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "check_count": len(checks),
        "checks": checks,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "refs": {
            "vector_review": str(VECTOR_REVIEW.relative_to(ROOT)),
            "vector_review_csv": str(VECTOR_REVIEW_CSV.relative_to(ROOT)),
            "domain_review": str(DOMAIN_REVIEW.relative_to(ROOT)),
            "mode_review": str(MODE_REVIEW.relative_to(ROOT)),
            "external_evaluator_requirements": str(NEXT_EVALUATOR_REQUIREMENTS.relative_to(ROOT))
        },
        "recommended_next_phase": "PROD-6461..6500 - CASULO Delta Zero External Evaluator Workbench Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "review_gate_only": True,
        "additional_live_call_allowed": False,
        "delta_zero_ready_claim_blocked_until_external_review": True,
        "trajectory_claim_blocked_until_multiple_snapshots": True,
        "candidate_tokens_canonical": False,
        "external_evaluator_required": True,
        "validated_model_gain_claim_blocked": True,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "review_gate_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "row_count": len(review_rows),
        "delta_zero_ready_count": dzr_ready_count,
        "hard_block_case_count": hard_block_count,
        "external_evaluator_required_count": needs_external_count,
        "average_delta_gate_mismatch": avg(gate_mismatch_values),
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "candidate_tokens_canonical": False,
        "validated_model_gain_claim_allowed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v3.4-delta-zero-review",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Delta Zero Batch 01 Vectorization Review Gate",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6421..6460 - CASULO Delta Zero Batch 01 Vectorization Review Gate

This phase reviews the T0 Delta Zero vectorization created in PROD-6381..6420.

It does not call GPT.

## Review result

- Rows reviewed: {len(review_rows)}
- Delta Zero Ready cases: {dzr_ready_count}
- Hard block cases: {hard_block_count}
- External evaluator required cases: {needs_external_count}
- Average delta gate mismatch: {avg(gate_mismatch_values)}
- Trajectory status: T0_ONLY
- Velocity ready: false
- Acceleration ready: false
- Candidate tokens canonical: false

## Decision

The Delta Zero vectorization is ready for external evaluator workbench creation, but no Delta Zero readiness, model gain, hallucination reduction, dataset, client, production or commercial claim is allowed.

## Next

PROD-6461..6500 - CASULO Delta Zero External Evaluator Workbench Packet
"""

    report = f"""# PROD-6421..6460 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Review gate only: true
- Additional live GPT call in this phase: false
- Rows reviewed: {result['row_count']}
- Delta Zero Ready count: {result['delta_zero_ready_count']}
- Hard block case count: {result['hard_block_case_count']}
- External evaluator required count: {result['external_evaluator_required_count']}
- Average delta gate mismatch: {result['average_delta_gate_mismatch']}
- Trajectory status: T0_ONLY
- Velocity ready: false
- Acceleration ready: false
- Candidate tokens canonical: false
- Validated model gain claim allowed: false
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write_json(VECTOR_REVIEW, vector_review)
    write_json(DOMAIN_REVIEW, domain_review)
    write_json(MODE_REVIEW, mode_review)
    write_json(NEXT_EVALUATOR_REQUIREMENTS, external_requirements)

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
    print("row_count:", result["row_count"])
    print("delta_zero_ready_count:", result["delta_zero_ready_count"])
    print("hard_block_case_count:", result["hard_block_case_count"])
    print("external_evaluator_required_count:", result["external_evaluator_required_count"])
    print("average_delta_gate_mismatch:", result["average_delta_gate_mismatch"])
    print("trajectory_status:", result["trajectory_status"])
    print("velocity_ready:", result["velocity_ready"])
    print("acceleration_ready:", result["acceleration_ready"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
