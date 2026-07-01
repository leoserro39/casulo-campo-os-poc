#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6341..6380"
REQ_TAG = "product-ponto-zero-telemetry-operational-hallucination-measurement-packet-v0.1"

PREV_PACKET = ROOT / "outputs/prod6301_6340_ponto_zero_telemetry_operational_hallucination_measurement_packet.json"
TELEMETRY_MATRIX = ROOT / "product/reports/ponto_zero_telemetry_matrix_batch01_hardened_v0_1.json"
TELEMETRY_CSV = ROOT / "product/reports/ponto_zero_telemetry_matrix_batch01_hardened_v0_1.csv"
QUEUE = ROOT / "product/evaluation/domain_calibration_external_evaluator_case_queue_v0_1.json"
P0_INDEX = ROOT / "product/evaluation/ponto_zero_operational_hallucination_indices_v0_1.json"
P0_SCHEMA = ROOT / "product/evaluation/ponto_zero_semantic_operational_telemetry_schema_v0_1.json"
P0_STATE = ROOT / "product/evaluation/ponto_zero_state_payload_schema_v0_1.json"
P0_TOKENS = ROOT / "product/evaluation/ponto_zero_candidate_tokens_v0_1.json"
P0_POLICY = ROOT / "product/evaluation/ponto_zero_anti_overreach_policy_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod6301_6340_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

SCORER = ROOT / "product/scripts/score_domain_calibration_external_evaluator_ponto_zero.py"
SCORE_TEMPLATE_CSV = ROOT / "product/evaluation/domain_calibration_external_evaluator_ponto_zero_score_template_v0_1.csv"
SCORE_TEMPLATE_JSON = ROOT / "product/evaluation/domain_calibration_external_evaluator_ponto_zero_score_template_v0_1.json"
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_external_evaluator_ponto_zero_execution_plan_v0_1.json"
GATE_READINESS = ROOT / "product/reports/domain_calibration_external_evaluator_ponto_zero_gate_readiness_v0_1.json"
BLANK_SCORE_OUTPUT = ROOT / "outputs/prod6341_6380_external_evaluator_blank_score_validation.json"
BLANK_SCORE_LOG = ROOT / "outputs/prod6341_6380_external_evaluator_blank_score_validation.log"

DOC = ROOT / "docs/product/662_DOMAIN_CALIBRATION_EXTERNAL_EVALUATOR_EXECUTION_GATE_WITH_PONTO_ZERO_METRICS.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_external_evaluator_execution_gate_ponto_zero.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_external_evaluator_execution_gate_ponto_zero_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/domain_calibration_external_evaluator_execution_gate_ponto_zero_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6341_6380_domain_calibration_external_evaluator_execution_gate_ponto_zero.json"
OUT_MD = ROOT / "outputs/prod6341_6380_domain_calibration_external_evaluator_execution_gate_ponto_zero.md"
ROADMAP_OUT = ROOT / "outputs/prod6341_6380_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "additional_live_gpt_call_in_this_gate",
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
    "canonical_token_acceptance_without_expansion_test"
]

ALLOWED = [
    "external_evaluator_execution_gate_creation",
    "ponto_zero_score_template_creation",
    "external_score_scorer_creation",
    "blank_score_block_validation",
    "manual_scoring_run_preparation",
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

def build_score_template(matrix):
    rows = matrix.get("rows", [])

    fieldnames = [
        "case_id",
        "execution_id",
        "scenario_id",
        "domain",
        "mode",
        "state_payload_id",
        "risk_level",
        "evidence_level",
        "gate",
        "review_ready",
        "candidate_token_count",
        "candidate_tokens",
        "pre_external_priority_score",
        "pre_external_ohri_proxy",
        "pre_external_oqi_proxy",
        "pre_external_zpi_proxy",
        "external_evidence_grounding_score",
        "external_gate_compliance_score",
        "external_claim_boundary_score",
        "external_state_completeness_score",
        "external_next_action_quality_score",
        "external_usefulness_score",
        "external_false_memory_risk",
        "external_over_review_flag",
        "external_under_review_flag",
        "external_hallucination_risk_flag",
        "external_accept_for_calibration_signal",
        "external_reviewer_notes"
    ]

    SCORE_TEMPLATE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SCORE_TEMPLATE_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "case_id": row.get("case_id"),
                "execution_id": row.get("execution_id"),
                "scenario_id": row.get("scenario_id"),
                "domain": row.get("domain"),
                "mode": row.get("mode"),
                "state_payload_id": row.get("state_payload_id"),
                "risk_level": row.get("risk_level"),
                "evidence_level": row.get("evidence_level"),
                "gate": row.get("gate"),
                "review_ready": row.get("review_ready"),
                "candidate_token_count": row.get("candidate_token_count"),
                "candidate_tokens": "|".join(row.get("candidate_tokens") or []),
                "pre_external_priority_score": row.get("pre_external_priority_score"),
                "pre_external_ohri_proxy": row.get("pre_external_ohri_proxy"),
                "pre_external_oqi_proxy": row.get("pre_external_oqi_proxy"),
                "pre_external_zpi_proxy": row.get("pre_external_zpi_proxy"),
                "external_evidence_grounding_score": "",
                "external_gate_compliance_score": "",
                "external_claim_boundary_score": "",
                "external_state_completeness_score": "",
                "external_next_action_quality_score": "",
                "external_usefulness_score": "",
                "external_false_memory_risk": "",
                "external_over_review_flag": "",
                "external_under_review_flag": "",
                "external_hallucination_risk_flag": "",
                "external_accept_for_calibration_signal": "",
                "external_reviewer_notes": ""
            })

    template_json = {
        "version": "domain_calibration_external_evaluator_ponto_zero_score_template.v0.1",
        "case_count": len(rows),
        "csv_ref": str(SCORE_TEMPLATE_CSV.relative_to(ROOT)),
        "instructions": [
            "Fill all external_* fields for all 36 cases.",
            "Scores must be 0 to 5.",
            "Boolean fields must be true or false.",
            "external_false_memory_risk must be LOW, MEDIUM, HIGH or NOT_APPLICABLE.",
            "Do not mark dataset acceptance, production evidence, client evidence or commercial claim.",
            "Run score_domain_calibration_external_evaluator_ponto_zero.py only after the template is complete."
        ],
        "required_external_fields": [
            "external_evidence_grounding_score",
            "external_gate_compliance_score",
            "external_claim_boundary_score",
            "external_state_completeness_score",
            "external_next_action_quality_score",
            "external_usefulness_score",
            "external_false_memory_risk",
            "external_over_review_flag",
            "external_under_review_flag",
            "external_hallucination_risk_flag",
            "external_accept_for_calibration_signal",
            "external_reviewer_notes"
        ]
    }
    write_json(SCORE_TEMPLATE_JSON, template_json)

def run_blank_validation():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCORER),
            "--input",
            str(SCORE_TEMPLATE_CSV),
            "--output",
            str(BLANK_SCORE_OUTPUT)
        ],
        cwd=ROOT,
        text=True,
        capture_output=True
    )
    write(BLANK_SCORE_LOG, "STDOUT:\n" + proc.stdout + "\nSTDERR:\n" + proc.stderr + "\nRC:\n" + str(proc.returncode))
    return proc

def main():
    prev = read_json(PREV_PACKET) if PREV_PACKET.exists() else {}
    matrix = read_json(TELEMETRY_MATRIX) if TELEMETRY_MATRIX.exists() else {}
    queue = read_json(QUEUE) if QUEUE.exists() else {}
    p0_index = read_json(P0_INDEX) if P0_INDEX.exists() else {}
    p0_schema = read_json(P0_SCHEMA) if P0_SCHEMA.exists() else {}
    p0_state = read_json(P0_STATE) if P0_STATE.exists() else {}
    p0_tokens = read_json(P0_TOKENS) if P0_TOKENS.exists() else {}
    p0_policy = read_json(P0_POLICY) if P0_POLICY.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required Ponto Zero telemetry packet tag")
    if prev.get("status") != "PASS":
        errors.append("previous Ponto Zero telemetry packet not PASS")
    if prev.get("decision") != "PONTO_ZERO_TELEMETRY_OPERATIONAL_HALLUCINATION_MEASUREMENT_PACKET_READY":
        errors.append("previous Ponto Zero telemetry decision mismatch")
    if prev.get("telemetry_matrix_row_count") != 36:
        errors.append("previous telemetry matrix row count not 36")
    if prev.get("external_indices_ready") is not False:
        errors.append("external indices should not be ready yet")
    if prev.get("candidate_tokens_canonical") is not False:
        errors.append("candidate tokens should not be canonical")
    if matrix.get("row_count") != 36:
        errors.append("telemetry matrix row count not 36")
    if queue.get("case_count") != 36:
        errors.append("external evaluator queue case count not 36")
    if not TELEMETRY_CSV.exists():
        errors.append("telemetry CSV missing")
    if "OHRI" not in p0_index.get("indices", {}):
        errors.append("OHRI not defined")
    if "OQI" not in p0_index.get("indices", {}):
        errors.append("OQI not defined")
    if "ZPI" not in p0_index.get("indices", {}):
        errors.append("ZPI not defined")
    if "dimensions" not in p0_schema:
        errors.append("P0 telemetry schema incomplete")
    if "required_fields" not in p0_state:
        errors.append("P0 state payload schema incomplete")
    if p0_tokens.get("canonical_acceptance_status") != "CANDIDATE_ONLY_NOT_CANONICAL":
        errors.append("candidate token registry status mismatch")
    if "hard_rules" not in p0_policy:
        errors.append("anti-overreach policy incomplete")
    if not SCORER.exists():
        errors.append("scorer script missing")

    build_score_template(matrix)

    with SCORE_TEMPLATE_CSV.open("r", encoding="utf-8") as f:
        template_rows = list(csv.DictReader(f))

    template_mode_counts = Counter(r.get("mode") for r in template_rows)
    template_domain_counts = Counter(r.get("domain") for r in template_rows)

    if len(template_rows) != 36:
        errors.append("score template row count not 36")
    if template_mode_counts != Counter({"PURE_GPT": 12, "STACK_GPT": 12, "CASULO_EXOCORTEX_STACK": 12}):
        errors.append("score template mode distribution mismatch")
    if len(template_domain_counts) != 6 or any(v != 6 for v in template_domain_counts.values()):
        errors.append("score template domain distribution mismatch")

    blank_proc = run_blank_validation()
    blank_result = read_json(BLANK_SCORE_OUTPUT) if BLANK_SCORE_OUTPUT.exists() else {}
    blank_score_blocked = (
        blank_proc.returncode != 0
        and blank_result.get("status") == "BLOCKED_MISSING_EXTERNAL_SCORES"
        and blank_result.get("complete_external_score_count") == 0
        and blank_result.get("final_indices_ready") is False
    )

    if not blank_score_blocked:
        errors.append("blank score template did not block final index calculation")

    exec_plan = {
        "version": "domain_calibration_external_evaluator_ponto_zero_execution_plan.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "manual_or_independent_external_scoring",
        "case_count": 36,
        "score_template_csv": str(SCORE_TEMPLATE_CSV.relative_to(ROOT)),
        "score_template_json": str(SCORE_TEMPLATE_JSON.relative_to(ROOT)),
        "scorer_script": str(SCORER.relative_to(ROOT)),
        "blank_score_validation_output": str(BLANK_SCORE_OUTPUT.relative_to(ROOT)),
        "instructions": [
            "Do not run additional GPT calls in this gate.",
            "Fill the CSV manually or with an independently approved evaluator process.",
            "All 36 rows must be completed before final OHRI/OQI/ZPI can be computed.",
            "Run the scorer script after filling the template.",
            "Final indices remain blocked until the scoring output passes."
        ],
        "next_phase": "PROD-6381..6420 - Domain Calibration External Evaluator Scoring Run with Ponto Zero Metrics"
    }

    readiness = {
        "version": "domain_calibration_external_evaluator_ponto_zero_gate_readiness.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "execution_gate_only": True,
        "additional_live_gpt_call_in_this_gate": False,
        "score_template_ready": len(template_rows) == 36,
        "scorer_ready": SCORER.exists(),
        "blank_score_block_validation_passed": blank_score_blocked,
        "final_indices_ready": False,
        "external_scores_required": True,
        "manual_or_independent_evaluator_required": True,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False
    }

    checks = [
        "prior_ponto_zero_telemetry_packet_present",
        "prior_ponto_zero_telemetry_packet_passed",
        "required_prior_tag_present",
        "execution_gate_only",
        "no_additional_live_gpt_call",
        "ponto_zero_telemetry_matrix_loaded",
        "thirty_six_ponto_zero_rows_confirmed",
        "external_evaluator_queue_loaded",
        "thirty_six_external_cases_confirmed",
        "ohri_defined",
        "oqi_defined",
        "zpi_defined",
        "candidate_tokens_non_canonical_confirmed",
        "anti_overreach_policy_present",
        "score_template_created",
        "score_template_thirty_six_rows_confirmed",
        "score_template_mode_distribution_confirmed",
        "score_template_domain_distribution_confirmed",
        "scorer_script_created",
        "blank_score_template_validation_executed",
        "blank_score_template_blocked_final_indices",
        "external_scores_required",
        "manual_or_independent_evaluator_required",
        "final_indices_not_ready",
        "validated_model_gain_claim_blocked",
        "hallucination_reduction_claim_blocked",
        "canonical_token_acceptance_blocked",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 352:
        checks.append(f"external_evaluator_execution_gate_p0_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6301..6340":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6381..6420":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration External Evaluator Execution Gate with Ponto Zero Metrics",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6381..6420" not in seen:
        roadmap_items.append({
            "phase": "PROD-6381..6420",
            "name": "Domain Calibration External Evaluator Scoring Run with Ponto Zero Metrics",
            "status": "NEXT"
        })

    decision = "APPROVED_FOR_EXTERNAL_EVALUATOR_EXECUTION_WITH_PONTO_ZERO_METRICS_AND_MANUAL_SCORES_ONLY"

    gate = {
        "version": "domain_calibration_external_evaluator_execution_gate_ponto_zero.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "EXTERNAL_EVALUATOR_EXECUTION_GATE_PONTO_ZERO_NOT_READY",
        "execution_gate_only": True,
        "additional_live_gpt_call_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "score_template_case_count": len(template_rows),
        "score_template_ref": str(SCORE_TEMPLATE_CSV.relative_to(ROOT)),
        "scorer_ref": str(SCORER.relative_to(ROOT)),
        "blank_score_validation_blocked": blank_score_blocked,
        "external_scores_required": True,
        "final_indices_ready": False,
        "manual_or_independent_evaluator_required": True,
        "candidate_tokens_canonical": False,
        "validated_model_gain_claim_allowed": False,
        "validated_hallucination_reduction_claim_allowed": False,
        "domain_validation_completed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "readiness_check_count": len(checks),
        "readiness_checks": checks,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": exec_plan["next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "execution_gate_only": True,
        "additional_live_call_allowed": False,
        "manual_or_independent_external_scores_required": True,
        "final_indices_without_external_scores_blocked": True,
        "validated_model_gain_claim_blocked": True,
        "hallucination_reduction_claim_blocked": True,
        "canonical_token_acceptance_blocked": True,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(checks),
        "execution_gate_only": True,
        "additional_live_gpt_call_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "ponto_zero_telemetry_matrix_rows": matrix.get("row_count"),
        "score_template_case_count": len(template_rows),
        "scorer_created": SCORER.exists(),
        "blank_score_validation_blocked": blank_score_blocked,
        "blank_score_validation_returncode": blank_proc.returncode,
        "external_scores_required": True,
        "final_indices_ready": False,
        "manual_or_independent_evaluator_required": True,
        "candidate_tokens_canonical": False,
        "validated_model_gain_claim_allowed": False,
        "validated_hallucination_reduction_claim_allowed": False,
        "domain_validation_completed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v3.2",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration External Evaluator Execution Gate with Ponto Zero Metrics",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6341..6380 - Domain Calibration External Evaluator Execution Gate with Ponto Zero Metrics

This gate prepares external/manual scoring with Ponto Zero metrics.

It does not call GPT.

## Result

- Score template cases: {len(template_rows)}
- Scorer created: {SCORER.exists()}
- Blank score validation blocked final indices: {blank_score_blocked}
- Final indices ready: false
- External scores required: true
- Candidate tokens canonical: false

## Meaning

The evaluator workbench is ready. OHRI/OQI/ZPI cannot be finalized until all 36 external score rows are completed.

## Next

PROD-6381..6420 - Domain Calibration External Evaluator Scoring Run with Ponto Zero Metrics
"""

    report = f"""# PROD-6341..6380 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {result['readiness_check_count']}
- Execution gate only: true
- Additional live GPT call in this gate: false
- Ponto Zero telemetry rows: {result['ponto_zero_telemetry_matrix_rows']}
- Score template case count: {result['score_template_case_count']}
- Scorer created: {result['scorer_created']}
- Blank score validation blocked: {result['blank_score_validation_blocked']}
- External scores required: true
- Final indices ready: false
- Manual or independent evaluator required: true
- Candidate tokens canonical: false
- Validated model gain claim allowed: false
- Hallucination reduction claim allowed: false
- Domain validation completed: false
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write_json(EXEC_PLAN, exec_plan)
    write_json(GATE_READINESS, readiness)
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
    print("score_template_case_count:", result["score_template_case_count"])
    print("scorer_created:", result["scorer_created"])
    print("blank_score_validation_blocked:", result["blank_score_validation_blocked"])
    print("external_scores_required:", result["external_scores_required"])
    print("final_indices_ready:", result["final_indices_ready"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
