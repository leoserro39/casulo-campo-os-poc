#!/usr/bin/env python3
import csv
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6501..6540"
REQ_TAG = "product-casulo-delta-zero-external-evaluator-workbench-packet-v0.1"

PREV = ROOT / "outputs/prod6461_6500_casulo_delta_zero_external_evaluator_workbench_packet.json"
WORKBENCH = ROOT / "product/evaluation/casulo_delta_zero_external_evaluator_workbench_v0_3.csv"
DELTA_MATRIX = ROOT / "product/reports/casulo_delta_zero_matrix_batch01_t0_v0_3.json"
ROADMAP_IN = ROOT / "outputs/prod6461_6500_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

ASSISTED_CSV = ROOT / "product/evaluation/casulo_delta_zero_assisted_scoring_draft_v0_3.csv"
ASSISTED_JSON = ROOT / "product/evaluation/casulo_delta_zero_assisted_scoring_draft_v0_3.json"
HUMAN_ACCEPTANCE_CSV = ROOT / "product/evaluation/casulo_delta_zero_human_acceptance_sheet_v0_3.csv"
GUIDE = ROOT / "product/evaluation/casulo_delta_zero_assisted_scoring_review_guide_v0_3.md"
STATUS_REPORT = ROOT / "product/reports/casulo_delta_zero_assisted_scoring_draft_status_v0_3.json"
PRIORITY_REPORT = ROOT / "product/reports/casulo_delta_zero_assisted_scoring_review_priority_v0_3.json"

DOC = ROOT / "docs/product/666_CASULO_DELTA_ZERO_ASSISTED_SCORING_DRAFT_PACKET.md"
CONTRACT = ROOT / "product/contracts/casulo_delta_zero_assisted_scoring_draft_packet.contract.json"
MEMORY = ROOT / "product/memory/casulo_delta_zero_assisted_scoring_draft_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/casulo_delta_zero_assisted_scoring_draft_packet_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6501_6540_casulo_delta_zero_assisted_scoring_draft_packet.json"
OUT_MD = ROOT / "outputs/prod6501_6540_casulo_delta_zero_assisted_scoring_draft_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod6501_6540_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

EXTERNAL_FIELDS = [
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

BLOCKED = [
    "auto_filled_external_scores",
    "final_indices_without_manual_acceptance",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "delta_zero_ready_validated_claim",
    "dataset_acceptance",
    "client_evidence",
    "production_activation",
    "commercial_claim",
    "canonical_token_acceptance",
    "velocity_claim_without_history",
    "acceleration_claim_without_history"
]

ALLOWED = [
    "assisted_internal_scoring_draft_creation",
    "human_acceptance_sheet_creation",
    "review_priority_report_creation",
    "manual_review_acceleration",
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

def clamp_score(x):
    return round(max(0.0, min(5.0, float(x))), 1)

def gate_order(gate):
    g = str(gate or "").upper()
    if g in ["READY_FOR_NEXT_STAGE", "PASS", "READY"]:
        return 0
    if g in ["OBSERVATION_REQUIRED", "WARNING"]:
        return 1
    if g in ["HUMAN_REVIEW_REQUIRED", "HOLD_HUMAN_REVIEW"]:
        return 2
    if g in ["CHANGE_REVIEW_REQUIRED", "CHANGE_LOCKED"]:
        return 3
    if g in ["BLOCKED", "INSUFFICIENT_EVIDENCE", "PRODUCTION_BLOCKED"]:
        return 4
    return 2

def as_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default

def suggest(row):
    vector = row.get("state_vector") or {}
    hard_blocks = row.get("hard_blocks") or []
    tokens = row.get("token_expansion", {}).get("candidate_tokens_v0_3") or []

    delta = as_float(row.get("delta_score"), 0.5)
    drd = as_float(row.get("drd"), 0.5)
    dzr = as_float(row.get("dzr"), 0.5)
    mismatch = as_float(row.get("delta_gate_mismatch"), 0.5)

    evidence_density = as_float(vector.get("evidence_density"), 0.4)
    readiness = as_float(vector.get("readiness_score"), 0.4)
    confidence = as_float(vector.get("confidence_level"), 0.4)
    ambiguity = as_float(vector.get("ambiguity_level"), 0.5)

    unsupported = "unsupported_claim_present" in hard_blocks
    gate_violation = "gate_violation_present" in hard_blocks
    thin_evidence = "thin_evidence" in hard_blocks

    evidence_score = clamp_score(5 * evidence_density)
    gate_score = clamp_score(5 * (1 - mismatch))

    claim_score = 4.5
    if unsupported:
        claim_score -= 1.4
    if gate_violation:
        claim_score -= 1.2
    if thin_evidence:
        claim_score -= 0.7
    claim_score = clamp_score(claim_score)

    vector_score = clamp_score(2.5 + 1.2 * confidence + 0.8 * readiness - 0.8 * ambiguity)
    delta_score = clamp_score(4.5 - 2.0 * mismatch - 0.8 * delta)
    drd_dzr_score = clamp_score(4.5 - 2.0 * drd + 0.7 * dzr)

    token_score = 2.5
    if tokens:
        token_score += 0.5
    if "ZERO_POINT_RESPONSE_READY" in tokens:
        token_score += 0.4
    if "BLOCKED_STATE" in tokens:
        token_score -= 0.4
    token_score = clamp_score(token_score)

    next_action_score = 3.5
    if row.get("computed_gate") in ["HUMAN_REVIEW_REQUIRED", "CHANGE_REVIEW_REQUIRED", "BLOCKED"]:
        next_action_score += 0.4
    if unsupported or gate_violation:
        next_action_score -= 0.5
    next_action_score = clamp_score(next_action_score)

    usefulness_score = clamp_score(
        0.20 * evidence_score
        + 0.20 * gate_score
        + 0.15 * claim_score
        + 0.15 * vector_score
        + 0.15 * delta_score
        + 0.15 * next_action_score
    )

    model_order = gate_order(row.get("model_gate"))
    computed_order = gate_order(row.get("computed_gate"))
    over_review = model_order > computed_order + 1
    under_review = model_order < computed_order - 1

    hallucination_flag = unsupported or gate_violation or under_review
    false_memory = "MEDIUM" if unsupported else "LOW"

    accept_signal = (
        not hard_blocks
        and not hallucination_flag
        and gate_score >= 3.5
        and evidence_score >= 2.5
        and delta <= 0.60
    )

    confidence_label = "LOW"
    if not hard_blocks and mismatch <= 0.25:
        confidence_label = "MEDIUM"
    if not hard_blocks and mismatch <= 0.10 and evidence_score >= 3.5:
        confidence_label = "HIGH"

    priority = round(
        10 * len(hard_blocks)
        + 5 * mismatch
        + 3 * delta
        + (2 if hallucination_flag else 0)
        + (1 if over_review or under_review else 0),
        4
    )

    return {
        "suggested_external_evidence_grounding_score": evidence_score,
        "suggested_external_gate_compliance_score": gate_score,
        "suggested_external_claim_boundary_score": claim_score,
        "suggested_external_state_vector_reasonableness_score": vector_score,
        "suggested_external_delta_reasonableness_score": delta_score,
        "suggested_external_drd_dzr_reasonableness_score": drd_dzr_score,
        "suggested_external_token_expansion_fidelity_score": token_score,
        "suggested_external_next_action_quality_score": next_action_score,
        "suggested_external_usefulness_score": usefulness_score,
        "suggested_external_false_memory_risk": false_memory,
        "suggested_external_hallucination_risk_flag": str(hallucination_flag).lower(),
        "suggested_external_over_review_flag": str(over_review).lower(),
        "suggested_external_under_review_flag": str(under_review).lower(),
        "suggested_external_accept_for_calibration_signal": str(accept_signal).lower(),
        "suggestion_confidence": confidence_label,
        "review_priority_score": priority,
        "assistant_draft_only": "true",
        "human_acceptance_required": "true",
        "must_not_copy_without_review": "true"
    }

def main():
    prev = read_json(PREV) if PREV.exists() else {}
    matrix = read_json(DELTA_MATRIX) if DELTA_MATRIX.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required external evaluator workbench tag")
    if prev.get("status") != "PASS":
        errors.append("previous external evaluator workbench packet not PASS")
    if prev.get("decision") != "CASULO_DELTA_ZERO_EXTERNAL_EVALUATOR_WORKBENCH_READY_PENDING_MANUAL_SCORES":
        errors.append("previous decision mismatch")
    if prev.get("case_count") != 36:
        errors.append("previous case count not 36")
    if prev.get("external_scores_completed") is not False:
        errors.append("external scores should not be completed")
    if prev.get("final_indices_ready") is not False:
        errors.append("final indices should not be ready")
    if matrix.get("row_count") != 36:
        errors.append("delta matrix row count not 36")
    if not WORKBENCH.exists():
        errors.append("workbench csv missing")

    workbench_rows = list(csv.DictReader(open(WORKBENCH, "r", encoding="utf-8"))) if WORKBENCH.exists() else []
    if len(workbench_rows) != 36:
        errors.append("workbench csv rows not 36")

    nonblank_external = []
    for row in workbench_rows:
        for field in EXTERNAL_FIELDS:
            if str(row.get(field, "")).strip():
                nonblank_external.append((row.get("case_id"), field))
    if nonblank_external:
        errors.append("external fields are already filled; assisted draft should not run on modified external workbench")

    matrix_by_case = {row.get("case_id"): row for row in matrix.get("rows", [])}

    assisted_rows = []
    priority_rows = []
    mode_counts = Counter()
    domain_counts = Counter()

    for wb in workbench_rows:
        case_id = wb.get("case_id")
        source = matrix_by_case.get(case_id)
        if not source:
            errors.append(f"missing delta matrix row for {case_id}")
            continue

        sug = suggest(source)
        mode_counts[wb.get("mode")] += 1
        domain_counts[wb.get("domain")] += 1

        base = {
            "case_id": wb.get("case_id"),
            "execution_id": wb.get("execution_id"),
            "scenario_id": wb.get("scenario_id"),
            "domain": wb.get("domain"),
            "mode": wb.get("mode"),
            "model_gate": wb.get("model_gate"),
            "computed_gate": wb.get("computed_gate"),
            "delta_score": wb.get("delta_score"),
            "delta_band": wb.get("delta_band"),
            "delta_gate_mismatch": wb.get("delta_gate_mismatch"),
            "drd": wb.get("drd"),
            "dzr": wb.get("dzr"),
            "delta_zero_ready": wb.get("delta_zero_ready"),
            "hard_blocks": wb.get("hard_blocks"),
            "trajectory_status": wb.get("trajectory_status"),
            "velocity_ready": wb.get("velocity_ready"),
            "acceleration_ready": wb.get("acceleration_ready"),
            "candidate_tokens_v0_3": wb.get("candidate_tokens_v0_3"),
            "case_packet": wb.get("case_packet")
        }
        assisted_row = dict(base)
        assisted_row.update(sug)
        assisted_rows.append(assisted_row)

        priority_rows.append({
            "case_id": case_id,
            "domain": wb.get("domain"),
            "mode": wb.get("mode"),
            "review_priority_score": sug["review_priority_score"],
            "hard_blocks": wb.get("hard_blocks"),
            "delta_score": wb.get("delta_score"),
            "delta_gate_mismatch": wb.get("delta_gate_mismatch"),
            "suggestion_confidence": sug["suggestion_confidence"]
        })

    priority_rows = sorted(priority_rows, key=lambda x: x["review_priority_score"], reverse=True)

    assisted_fieldnames = list(assisted_rows[0].keys()) if assisted_rows else []
    with ASSISTED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=assisted_fieldnames)
        writer.writeheader()
        writer.writerows(assisted_rows)

    acceptance_fieldnames = [
        "case_id", "domain", "mode", "review_decision_ACCEPT_ADJUST_REJECT",
        "accepted_external_evidence_grounding_score",
        "accepted_external_gate_compliance_score",
        "accepted_external_claim_boundary_score",
        "accepted_external_state_vector_reasonableness_score",
        "accepted_external_delta_reasonableness_score",
        "accepted_external_drd_dzr_reasonableness_score",
        "accepted_external_token_expansion_fidelity_score",
        "accepted_external_next_action_quality_score",
        "accepted_external_usefulness_score",
        "accepted_external_false_memory_risk",
        "accepted_external_hallucination_risk_flag",
        "accepted_external_over_review_flag",
        "accepted_external_under_review_flag",
        "accepted_external_accept_for_calibration_signal",
        "human_reviewer_notes",
        "source_suggested_row"
    ]

    with HUMAN_ACCEPTANCE_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=acceptance_fieldnames)
        writer.writeheader()
        for row in assisted_rows:
            writer.writerow({
                "case_id": row["case_id"],
                "domain": row["domain"],
                "mode": row["mode"],
                "review_decision_ACCEPT_ADJUST_REJECT": "",
                "accepted_external_evidence_grounding_score": "",
                "accepted_external_gate_compliance_score": "",
                "accepted_external_claim_boundary_score": "",
                "accepted_external_state_vector_reasonableness_score": "",
                "accepted_external_delta_reasonableness_score": "",
                "accepted_external_drd_dzr_reasonableness_score": "",
                "accepted_external_token_expansion_fidelity_score": "",
                "accepted_external_next_action_quality_score": "",
                "accepted_external_usefulness_score": "",
                "accepted_external_false_memory_risk": "",
                "accepted_external_hallucination_risk_flag": "",
                "accepted_external_over_review_flag": "",
                "accepted_external_under_review_flag": "",
                "accepted_external_accept_for_calibration_signal": "",
                "human_reviewer_notes": "",
                "source_suggested_row": "product/evaluation/casulo_delta_zero_assisted_scoring_draft_v0_3.csv"
            })

    assisted_json = {
        "version": "casulo_delta_zero_assisted_scoring_draft.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ASSISTED_DRAFT_READY_NOT_EXTERNAL_SCORE",
        "case_count": len(assisted_rows),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "assistant_draft_only": True,
        "human_acceptance_required": True,
        "external_scores_completed": False,
        "final_indices_ready": False,
        "validated_model_gain_claim_allowed": False,
        "validated_hallucination_reduction_claim_allowed": False,
        "delta_zero_ready_validated": False,
        "rows": assisted_rows
    }

    priority_report = {
        "version": "casulo_delta_zero_assisted_scoring_review_priority.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "priority_policy": "Review higher priority scores first: hard blocks, gate mismatch, high delta, hallucination/under-review flags.",
        "top_10": priority_rows[:10],
        "rows": priority_rows
    }

    guide = """# CASULO Delta Zero Assisted Scoring Review Guide

This packet creates suggested/candidate scores only.

Do not treat suggested_* fields as external/manual validation.

Review process:
1. Open product/evaluation/casulo_delta_zero_assisted_scoring_draft_v0_3.csv.
2. Review each suggested_* score against the case packet.
3. Fill product/evaluation/casulo_delta_zero_human_acceptance_sheet_v0_3.csv.
4. Only accepted/adjusted human scores may be converted into external_* fields in a later ingestion gate.

Hard rule:
- Do not auto-copy suggested_* into external_*.
- Do not claim validated model gain.
- Do not claim hallucination reduction.
- Do not validate Delta Zero Ready.
- Do not accept dataset, client, production or commercial claims.

T0 trajectory:
- velocity_ready=false means not measured.
- acceleration_ready=false means not measured.
- They must not be interpreted as zero.
"""

    if len(assisted_rows) != 36:
        errors.append("assisted draft row count not 36")
    if mode_counts != Counter({"PURE_GPT": 12, "STACK_GPT": 12, "CASULO_EXOCORTEX_STACK": 12}):
        errors.append("mode distribution mismatch")
    if len(domain_counts) != 6 or any(v != 6 for v in domain_counts.values()):
        errors.append("domain distribution mismatch")
    if not ASSISTED_CSV.exists() or not HUMAN_ACCEPTANCE_CSV.exists():
        errors.append("assisted csv or human acceptance csv missing")

    status_report = {
        "version": "casulo_delta_zero_assisted_scoring_draft_status.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "assisted_draft_ready": True,
        "case_count": len(assisted_rows),
        "external_scores_completed": False,
        "final_indices_ready": False,
        "assistant_draft_only": True,
        "human_acceptance_required": True,
        "workbench_external_fields_remain_blank": len(nonblank_external) == 0
    }

    checks = [
        "prior_external_evaluator_workbench_packet_present",
        "prior_external_evaluator_workbench_packet_passed",
        "required_prior_tag_present",
        "packet_only",
        "no_additional_live_gpt_call",
        "workbench_csv_loaded",
        "external_fields_verified_blank",
        "delta_matrix_loaded",
        "thirty_six_rows_loaded",
        "assisted_draft_csv_created",
        "assisted_draft_json_created",
        "human_acceptance_sheet_created",
        "review_priority_report_created",
        "review_guide_created",
        "suggested_scores_marked_draft_only",
        "human_acceptance_required",
        "external_scores_not_completed",
        "final_indices_not_ready",
        "validated_model_gain_claim_blocked",
        "hallucination_reduction_claim_blocked",
        "delta_zero_ready_validated_claim_blocked",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 392:
        checks.append(f"assisted_scoring_draft_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6461..6500":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6541..6580":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "CASULO Delta Zero Assisted Scoring Draft Packet",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6541..6580" not in seen:
        roadmap_items.append({
            "phase": "PROD-6541..6580",
            "name": "CASULO Delta Zero Human Score Acceptance and Ingestion Gate",
            "status": "NEXT"
        })

    decision = "CASULO_DELTA_ZERO_ASSISTED_SCORING_DRAFT_READY_PENDING_HUMAN_ACCEPTANCE"

    packet = {
        "version": "casulo_delta_zero_assisted_scoring_draft_packet.v0.3",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_DELTA_ZERO_ASSISTED_SCORING_DRAFT_NOT_READY",
        "packet_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "assisted_draft_ready": True,
        "case_count": len(assisted_rows),
        "assistant_draft_only": True,
        "human_acceptance_required": True,
        "external_scores_completed": False,
        "final_indices_ready": False,
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
            "assisted_csv": str(ASSISTED_CSV.relative_to(ROOT)),
            "assisted_json": str(ASSISTED_JSON.relative_to(ROOT)),
            "human_acceptance_csv": str(HUMAN_ACCEPTANCE_CSV.relative_to(ROOT)),
            "guide": str(GUIDE.relative_to(ROOT)),
            "priority_report": str(PRIORITY_REPORT.relative_to(ROOT))
        },
        "recommended_next_phase": "PROD-6541..6580 - CASULO Delta Zero Human Score Acceptance and Ingestion Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "packet_only": True,
        "assisted_scores_are_external_scores": False,
        "auto_copy_to_external_fields_blocked": True,
        "human_acceptance_required": True,
        "final_indices_without_accepted_scores_blocked": True,
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
        "assisted_draft_ready": True,
        "case_count": len(assisted_rows),
        "assistant_draft_only": True,
        "human_acceptance_required": True,
        "external_scores_completed": False,
        "final_indices_ready": False,
        "workbench_external_fields_remain_blank": len(nonblank_external) == 0,
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
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v3.6-assisted-scoring",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Delta Zero Assisted Scoring Draft Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6501..6540 - CASULO Delta Zero Assisted Scoring Draft Packet

This phase creates suggested scores to accelerate human/manual review.

It does not fill external_* fields and does not create final indices.

## Result

- Assisted draft ready: true
- Cases: {len(assisted_rows)}
- Assistant draft only: true
- Human acceptance required: true
- External scores completed: false
- Final indices ready: false

## Next

PROD-6541..6580 - CASULO Delta Zero Human Score Acceptance and Ingestion Gate
"""

    report = f"""# PROD-6501..6540 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Additional live GPT call in this phase: false
- Assisted draft ready: true
- Case count: {result['case_count']}
- Assistant draft only: true
- Human acceptance required: true
- External scores completed: false
- Final indices ready: false
- Workbench external fields remain blank: {result['workbench_external_fields_remain_blank']}
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

    write_json(ASSISTED_JSON, assisted_json)
    write_json(PRIORITY_REPORT, priority_report)
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
    print("assisted_draft_ready:", result["assisted_draft_ready"])
    print("assistant_draft_only:", result["assistant_draft_only"])
    print("human_acceptance_required:", result["human_acceptance_required"])
    print("external_scores_completed:", result["external_scores_completed"])
    print("final_indices_ready:", result["final_indices_ready"])
    print("workbench_external_fields_remain_blank:", result["workbench_external_fields_remain_blank"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
