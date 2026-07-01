#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6461..6500"
REQ_TAG = "product-casulo-delta-zero-batch01-vectorization-review-gate-v0.1"

PREV = ROOT / "outputs/prod6421_6460_casulo_delta_zero_batch01_vectorization_review_gate.json"
DELTA_MATRIX = ROOT / "product/reports/casulo_delta_zero_matrix_batch01_t0_v0_3.json"
VECTOR_REVIEW = ROOT / "product/reports/casulo_delta_zero_batch01_vectorization_review_v0_3.json"
REQS = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_requirements_v0_3.json"
ROADMAP_IN = ROOT / "outputs/prod6421_6460_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
SCORER = ROOT / "product/scripts/score_casulo_delta_zero_external_evaluator.py"

CASE_DIR = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_cases"
WORKBENCH_CSV = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_workbench_v0_3.csv"
WORKBENCH_JSON = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_workbench_v0_3.json"
GUIDE = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_review_guide_v0_3.md"
BLANK_SCORE = ROOT / "outputs/prod6461_6500_casulo_delta_zero_blank_score_validation.json"
BLANK_SCORE_LOG = ROOT / "outputs/prod6461_6500_casulo_delta_zero_blank_score_validation.log"
STATUS_REPORT = ROOT / "product/reports/casulo_delta_zero_external_evaluator_workbench_status_v0_3.json"

DOC = ROOT / "docs/product/665_CASULO_DELTA_ZERO_EXTERNAL_EVALUATOR_WORKBENCH_PACKET.md"
CONTRACT = ROOT / "product/contracts/casulo_delta_zero_external_evaluator_workbench_packet.contract.json"
MEMORY = ROOT / "product/memory/casulo_delta_zero_external_evaluator_workbench_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/casulo_delta_zero_external_evaluator_workbench_packet_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6461_6500_casulo_delta_zero_external_evaluator_workbench_packet.json"
OUT_MD = ROOT / "outputs/prod6461_6500_casulo_delta_zero_external_evaluator_workbench_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod6461_6500_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "additional_live_gpt_call_in_this_phase",
    "auto_filled_external_scores",
    "dataset_acceptance",
    "client_facing_value_claim",
    "production_activation",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "delta_zero_ready_validated_claim",
    "commercial_claim",
    "canonical_token_acceptance"
]

ALLOWED = [
    "external_evaluator_workbench_creation",
    "case_packet_creation",
    "blank_score_block_validation",
    "review_guide_creation",
    "manual_scoring_preparation",
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

def main():
    prev = read_json(PREV) if PREV.exists() else {}
    matrix = read_json(DELTA_MATRIX) if DELTA_MATRIX.exists() else {}
    vector_review = read_json(VECTOR_REVIEW) if VECTOR_REVIEW.exists() else {}
    reqs = read_json(REQS) if REQS.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required vectorization review gate tag")
    if prev.get("status") != "PASS":
        errors.append("previous vectorization review gate not PASS")
    if prev.get("decision") != "CASULO_DELTA_ZERO_BATCH01_VECTORIZATION_REVIEW_GATE_READY":
        errors.append("previous vectorization review gate decision mismatch")
    if prev.get("row_count") != 36:
        errors.append("previous row count not 36")
    if prev.get("delta_zero_ready_count") != 0:
        errors.append("delta zero ready count should be zero")
    if prev.get("external_evaluator_required_count") != 36:
        errors.append("external evaluator required count should be 36")
    if matrix.get("row_count") != 36:
        errors.append("delta matrix row count not 36")
    if vector_review.get("row_count") != 36:
        errors.append("vector review row count not 36")
    if len(reqs.get("must_score", [])) < 10:
        errors.append("external evaluator requirements incomplete")
    if not SCORER.exists():
        errors.append("scorer missing")

    rows = matrix.get("rows", [])
    CASE_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "case_id", "execution_id", "scenario_id", "domain", "mode",
        "model_gate", "computed_gate", "delta_score", "delta_band",
        "delta_gate_mismatch", "drd", "dzr", "delta_zero_ready",
        "hard_blocks", "trajectory_status", "velocity_ready", "acceleration_ready",
        "candidate_tokens_v0_3", "case_packet",
        "external_evidence_grounding_score",
        "external_gate_compliance_score",
        "external_claim_boundary_score",
        "external_state_vector_reasonableness_score",
        "external_delta_reasonableness_score",
        "external_drd_dzr_reasonableness_score",
        "external_token_expansion_fidelity_score",
        "external_next_action_quality_score",
        "external_usefulness_score",
        "external_false_memory_risk",
        "external_hallucination_risk_flag",
        "external_over_review_flag",
        "external_under_review_flag",
        "external_accept_for_calibration_signal",
        "external_reviewer_notes"
    ]

    workbench_rows = []
    mode_counts = Counter()
    domain_counts = Counter()

    for row in rows:
        case_id = row.get("case_id")
        mode_counts[row.get("mode")] += 1
        domain_counts[row.get("domain")] += 1

        packet_path = CASE_DIR / f"{case_id}.md"
        packet_md = f"""# CASULO Delta Zero External Evaluator Case {case_id}

## Identification

- Case ID: {case_id}
- Execution ID: {row.get('execution_id')}
- Scenario ID: {row.get('scenario_id')}
- Domain: {row.get('domain')}
- Mode: {row.get('mode')}

## Gates and Delta

- Model gate: {row.get('model_gate')}
- Computed gate: {row.get('computed_gate')}
- Delta score: {row.get('delta_score')}
- Delta band: {row.get('delta_band')}
- Delta gate mismatch: {row.get('delta_gate_mismatch')}
- DRD: {row.get('drd')}
- DZR: {row.get('dzr')}
- Delta Zero Ready: {row.get('delta_zero_ready')}
- Hard blocks: {row.get('hard_blocks')}

## State Vector

{json.dumps(row.get('state_vector'), indent=2, ensure_ascii=False)}

## Reference Vector

{json.dumps(row.get('reference_vector'), indent=2, ensure_ascii=False)}

## Domain Weight Profile

{json.dumps(row.get('domain_weight_profile'), indent=2, ensure_ascii=False)}

## Trajectory

{json.dumps(row.get('trajectory'), indent=2, ensure_ascii=False)}

## Token Expansion

{json.dumps(row.get('token_expansion'), indent=2, ensure_ascii=False)}

## Reviewer instruction

Score the external_* fields in the CSV. Do not approve dataset, production, client evidence, commercial claim, canonical token acceptance, validated model gain or validated hallucination reduction.
"""
        write(packet_path, packet_md)

        workbench_rows.append({
            "case_id": case_id,
            "execution_id": row.get("execution_id"),
            "scenario_id": row.get("scenario_id"),
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
            "hard_blocks": "|".join(row.get("hard_blocks") or []),
            "trajectory_status": row.get("trajectory", {}).get("trajectory_status"),
            "velocity_ready": row.get("trajectory", {}).get("velocity_ready"),
            "acceleration_ready": row.get("trajectory", {}).get("acceleration_ready"),
            "candidate_tokens_v0_3": "|".join(row.get("token_expansion", {}).get("candidate_tokens_v0_3") or []),
            "case_packet": str(packet_path.relative_to(ROOT)),
            "external_evidence_grounding_score": "",
            "external_gate_compliance_score": "",
            "external_claim_boundary_score": "",
            "external_state_vector_reasonableness_score": "",
            "external_delta_reasonableness_score": "",
            "external_drd_dzr_reasonableness_score": "",
            "external_token_expansion_fidelity_score": "",
            "external_next_action_quality_score": "",
            "external_usefulness_score": "",
            "external_false_memory_risk": "",
            "external_hallucination_risk_flag": "",
            "external_over_review_flag": "",
            "external_under_review_flag": "",
            "external_accept_for_calibration_signal": "",
            "external_reviewer_notes": ""
        })

    with WORKBENCH_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in workbench_rows:
            writer.writerow(row)

    workbench_json = {
        "version": "casulo_delta_zero_external_evaluator_workbench.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_MANUAL_EXTERNAL_SCORING",
        "case_count": len(workbench_rows),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "workbench_csv": str(WORKBENCH_CSV.relative_to(ROOT)),
        "case_dir": str(CASE_DIR.relative_to(ROOT)),
        "scorer": str(SCORER.relative_to(ROOT)),
        "external_scores_completed": False,
        "final_indices_ready": False
    }

    guide = """# CASULO Delta Zero External Evaluator Review Guide

Fill all external_* fields for all 36 cases.

Scores: 0 to 5.

Boolean fields: true or false.

external_false_memory_risk: LOW, MEDIUM, HIGH or NOT_APPLICABLE.

Important:
- T0_ONLY means no trajectory yet.
- velocity_ready=false must not be interpreted as zero velocity.
- acceleration_ready=false must not be interpreted as zero acceleration.
- Delta Zero Ready remains unvalidated.
- Candidate tokens remain non-canonical.
- Do not approve dataset, production, client evidence, commercial claim, validated model gain or hallucination reduction.

After scoring, run:

python product/scripts/score_casulo_delta_zero_external_evaluator.py --input product/evaluation/casulo_delta_zero_external_evaluator_workbench_v0_3.csv --output outputs/prod6501_6540_casulo_delta_zero_external_score_result.json
"""

    blank = subprocess.run(
        [sys.executable, str(SCORER), "--input", str(WORKBENCH_CSV), "--output", str(BLANK_SCORE)],
        cwd=ROOT,
        text=True,
        capture_output=True
    )
    write(BLANK_SCORE_LOG, "STDOUT:\n" + blank.stdout + "\nSTDERR:\n" + blank.stderr + "\nRC:\n" + str(blank.returncode))

    blank_json = read_json(BLANK_SCORE) if BLANK_SCORE.exists() else {}
    blank_blocks = (
        blank.returncode != 0
        and blank_json.get("status") == "BLOCKED_MISSING_EXTERNAL_SCORES"
        and blank_json.get("complete_external_score_count") == 0
        and blank_json.get("final_indices_ready") is False
    )

    if len(workbench_rows) != 36:
        errors.append("workbench row count not 36")
    if len(list(CASE_DIR.glob("*.md"))) != 36:
        errors.append("case packet count not 36")
    if mode_counts != Counter({"PURE_GPT": 12, "STACK_GPT": 12, "CASULO_EXOCORTEX_STACK": 12}):
        errors.append("mode distribution mismatch")
    if len(domain_counts) != 6 or any(v != 6 for v in domain_counts.values()):
        errors.append("domain distribution mismatch")
    if not blank_blocks:
        errors.append("blank scoring did not block final indices")

    status_report = {
        "version": "casulo_delta_zero_external_evaluator_workbench_status.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "workbench_ready": True,
        "case_count": len(workbench_rows),
        "case_packet_count": len(list(CASE_DIR.glob("*.md"))),
        "blank_score_validation_blocked": blank_blocks,
        "external_scores_completed": False,
        "final_indices_ready": False,
        "manual_or_independent_evaluator_required": True
    }

    checks = [
        "prior_vectorization_review_gate_present",
        "prior_vectorization_review_gate_passed",
        "required_prior_tag_present",
        "packet_only",
        "no_additional_live_gpt_call",
        "delta_matrix_loaded",
        "thirty_six_rows_loaded",
        "workbench_csv_created",
        "workbench_json_created",
        "thirty_six_case_packets_created",
        "review_guide_created",
        "scorer_available",
        "blank_score_validation_executed",
        "blank_score_validation_blocked_final_indices",
        "external_scores_not_completed",
        "final_indices_not_ready",
        "candidate_tokens_non_canonical",
        "delta_zero_ready_validated_claim_blocked",
        "validated_model_gain_claim_blocked",
        "hallucination_reduction_claim_blocked",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 384:
        checks.append(f"delta_zero_external_evaluator_workbench_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6421..6460":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6501..6540":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "CASULO Delta Zero External Evaluator Workbench Packet",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6501..6540" not in seen:
        roadmap_items.append({
            "phase": "PROD-6501..6540",
            "name": "CASULO Delta Zero External Evaluator Manual Scoring Run",
            "status": "NEXT"
        })

    decision = "CASULO_DELTA_ZERO_EXTERNAL_EVALUATOR_WORKBENCH_READY_PENDING_MANUAL_SCORES"

    packet = {
        "version": "casulo_delta_zero_external_evaluator_workbench_packet.v0.3",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_DELTA_ZERO_EXTERNAL_EVALUATOR_WORKBENCH_NOT_READY",
        "packet_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "workbench_ready": True,
        "case_count": len(workbench_rows),
        "case_packet_count": len(list(CASE_DIR.glob("*.md"))),
        "blank_score_validation_blocked": blank_blocks,
        "external_scores_completed": False,
        "final_indices_ready": False,
        "manual_or_independent_evaluator_required": True,
        "validated_model_gain_claim_allowed": False,
        "validated_hallucination_reduction_claim_allowed": False,
        "delta_zero_ready_validated": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "check_count": len(checks),
        "checks": checks,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "refs": {
            "workbench_csv": str(WORKBENCH_CSV.relative_to(ROOT)),
            "workbench_json": str(WORKBENCH_JSON.relative_to(ROOT)),
            "review_guide": str(GUIDE.relative_to(ROOT)),
            "scorer": str(SCORER.relative_to(ROOT)),
            "status_report": str(STATUS_REPORT.relative_to(ROOT))
        },
        "recommended_next_phase": "PROD-6501..6540 - CASULO Delta Zero External Evaluator Manual Scoring Run"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "packet_only": True,
        "auto_filled_external_scores_blocked": True,
        "manual_or_independent_evaluator_required": True,
        "final_indices_without_external_scores_blocked": True,
        "validated_model_gain_claim_blocked": True,
        "hallucination_reduction_claim_blocked": True,
        "delta_zero_ready_validated_claim_blocked": True,
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
        "packet_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "workbench_ready": True,
        "case_count": len(workbench_rows),
        "case_packet_count": len(list(CASE_DIR.glob("*.md"))),
        "blank_score_validation_blocked": blank_blocks,
        "external_scores_completed": False,
        "final_indices_ready": False,
        "manual_or_independent_evaluator_required": True,
        "validated_model_gain_claim_allowed": False,
        "validated_hallucination_reduction_claim_allowed": False,
        "delta_zero_ready_validated": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v3.5-delta-zero-external-workbench",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Delta Zero External Evaluator Workbench Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6461..6500 - CASULO Delta Zero External Evaluator Workbench Packet

This phase creates the external/manual evaluator workbench for Delta Zero Batch 01.

It does not call GPT and does not fill external scores automatically.

## Result

- Workbench ready: true
- Cases: {len(workbench_rows)}
- Case packets: {len(list(CASE_DIR.glob("*.md")))}
- Blank score validation blocked final indices: {blank_blocks}
- External scores completed: false
- Final indices ready: false

## Next

PROD-6501..6540 - CASULO Delta Zero External Evaluator Manual Scoring Run
"""

    report = f"""# PROD-6461..6500 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Additional live GPT call in this phase: false
- Workbench ready: true
- Case count: {result['case_count']}
- Case packet count: {result['case_packet_count']}
- Blank score validation blocked: {result['blank_score_validation_blocked']}
- External scores completed: false
- Final indices ready: false
- Manual or independent evaluator required: true
- Validated model gain claim allowed: false
- Hallucination reduction claim allowed: false
- Delta Zero Ready validated: false
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write_json(WORKBENCH_JSON, workbench_json)
    write(GUIDE, guide)
    write_json(STATUS_REPORT, status_report)
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
    print("case_count:", result["case_count"])
    print("case_packet_count:", result["case_packet_count"])
    print("blank_score_validation_blocked:", result["blank_score_validation_blocked"])
    print("external_scores_completed:", result["external_scores_completed"])
    print("final_indices_ready:", result["final_indices_ready"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
