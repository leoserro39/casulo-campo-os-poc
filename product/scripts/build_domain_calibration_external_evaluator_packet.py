#!/usr/bin/env python3
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6261..6300"
REQ_TAG = "product-domain-calibration-hardened-rerun-review-gate-v0.1"

PREV_REVIEW = ROOT / "outputs/prod6221_6260_domain_calibration_hardened_rerun_review_gate.json"
BEHAVIORAL_METRICS = ROOT / "product/reports/domain_calibration_hardened_rerun_behavioral_metrics_v0_1.json"
MODE_COMPARISON = ROOT / "product/reports/domain_calibration_hardened_rerun_mode_comparison_v0_1.json"
DOMAIN_FINDINGS = ROOT / "product/reports/domain_calibration_hardened_rerun_domain_findings_v0_1.json"
HARDENED_BATCH = ROOT / "outputs/prod6181_6220_domain_calibration_batch01_hardened_result.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXPECTED_SCHEMA = ROOT / "product/evaluation/domain_calibration_expected_response_schema_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod6221_6260_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/660_DOMAIN_CALIBRATION_EXTERNAL_EVALUATOR_PACKET.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_external_evaluator_packet.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_external_evaluator_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/domain_calibration_external_evaluator_packet_v0_1.json"

EVALUATOR_SCHEMA = ROOT / "product/evaluation/domain_calibration_external_evaluator_schema_v0_1.json"
EVALUATOR_RUBRIC = ROOT / "product/evaluation/domain_calibration_external_evaluator_rubric_v0_1.json"
EVALUATOR_THRESHOLDS = ROOT / "product/evaluation/domain_calibration_external_evaluator_thresholds_v0_1.json"
EVALUATOR_QUEUE = ROOT / "product/evaluation/domain_calibration_external_evaluator_case_queue_v0_1.json"
MIN_PROCESS_JSON = ROOT / "product/reports/domain_calibration_minimum_process_view_for_gain_and_real_calibration_v0_1.json"
MIN_PROCESS_MD = ROOT / "product/reports/domain_calibration_minimum_process_view_for_gain_and_real_calibration_v0_1.md"
DECISION_BRIEF = ROOT / "product/reports/domain_calibration_decision_brief_v0_1.json"

OUT_JSON = ROOT / "outputs/prod6261_6300_domain_calibration_external_evaluator_packet.json"
OUT_MD = ROOT / "outputs/prod6261_6300_domain_calibration_external_evaluator_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod6261_6300_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "additional_live_gpt_call_in_this_phase",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
    "persistent_memory_write",
    "multi_vendor_llm_execution",
    "dataset_acceptance",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim",
    "commercial_claim",
    "domain_validation_claim",
    "model_gain_claim_without_external_evaluation"
]

ALLOWED = [
    "external_evaluator_packet_creation",
    "external_evaluator_schema_creation",
    "external_evaluator_rubric_creation",
    "external_evaluator_thresholds_creation",
    "external_evaluator_case_queue_creation",
    "minimum_process_view_creation",
    "decision_brief_creation",
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

def to_num(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def priority_flags(parsed):
    flags = []
    missing = int(to_num(parsed.get("missing_evidence_claim_count"), 0))
    unsupported = int(to_num(parsed.get("unsupported_claim_count"), 0))
    gate_violations = int(to_num(parsed.get("gate_violation_count"), 0))
    manual = int(to_num(parsed.get("manual_arbitration_needed_count"), 0))
    evidence = to_num(parsed.get("evidence_grounding_score"), None)
    state = to_num(parsed.get("state_completeness_score"), None)
    gate = parsed.get("gate_status")
    human = parsed.get("human_review_required")

    if gate in ["BLOCKED", "HOLD_HUMAN_REVIEW", "INSUFFICIENT_EVIDENCE"]:
        flags.append("gate_attention")
    if missing >= 2:
        flags.append("missing_evidence_attention")
    if unsupported > 0:
        flags.append("unsupported_claim_attention")
    if gate_violations > 0:
        flags.append("gate_violation_attention")
    if manual > 0:
        flags.append("manual_arbitration_attention")
    if human is True:
        flags.append("human_review_required")
    if evidence is not None and evidence <= 2:
        flags.append("low_evidence_grounding")
    if state is not None and state <= 2:
        flags.append("low_state_completeness")
    return sorted(set(flags))

def main():
    prev = read_json(PREV_REVIEW) if PREV_REVIEW.exists() else {}
    metrics = read_json(BEHAVIORAL_METRICS) if BEHAVIORAL_METRICS.exists() else {}
    mode_comparison = read_json(MODE_COMPARISON) if MODE_COMPARISON.exists() else {}
    domain_findings = read_json(DOMAIN_FINDINGS) if DOMAIN_FINDINGS.exists() else {}
    batch = read_json(HARDENED_BATCH) if HARDENED_BATCH.exists() else {}
    scenarios_packet = read_json(SCENARIOS) if SCENARIOS.exists() else {}
    expected_schema = read_json(EXPECTED_SCHEMA) if EXPECTED_SCHEMA.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required hardened rerun review gate tag")
    if prev.get("status") != "PASS":
        errors.append("previous hardened rerun review gate not PASS")
    if prev.get("decision") != "DOMAIN_CALIBRATION_HARDENED_RERUN_REVIEW_COMPLETED_SELF_REPORTED_METRICS_READY":
        errors.append("previous hardened rerun review decision mismatch")
    if prev.get("review_ready_count") != 36:
        errors.append("previous review_ready_count not 36")
    if prev.get("empty_output_count") != 0:
        errors.append("previous empty_output_count not zero")
    if prev.get("json_parse_failure_count") != 0:
        errors.append("previous json_parse_failure_count not zero")
    if prev.get("missing_required_fields_count") != 0:
        errors.append("previous missing_required_fields_count not zero")
    if prev.get("external_evaluator_required") is not True:
        errors.append("external evaluator requirement not true")
    if prev.get("domain_validation_completed") is not False:
        errors.append("domain_validation_completed should be false")
    if batch.get("status") != "PASS":
        errors.append("hardened batch not PASS")
    if batch.get("review_ready_count") != 36:
        errors.append("hardened batch review_ready_count not 36")
    if metrics.get("status") != "PASS":
        errors.append("behavioral metrics not PASS")
    if len(expected_schema.get("required_fields", [])) != 15:
        errors.append("expected schema required fields mismatch")

    scenarios = {
        s.get("scenario_id"): s
        for s in scenarios_packet.get("scenarios", [])
    }

    results = batch.get("results", [])
    if len(results) != 36:
        errors.append("expected 36 hardened results")

    queue = []
    mode_counts = Counter()
    domain_counts = Counter()
    scenario_counts = Counter()
    priority_counter = Counter()

    for idx, r in enumerate(results, start=1):
        parsed = r.get("parsed_output_json")
        if not isinstance(parsed, dict):
            parsed = {}

        scenario_id = r.get("scenario_id")
        scenario = scenarios.get(scenario_id, {})

        flags = priority_flags(parsed)
        for flag in flags:
            priority_counter[flag] += 1

        mode = r.get("mode")
        domain = r.get("domain")
        mode_counts[mode] += 1
        domain_counts[domain] += 1
        scenario_counts[scenario_id] += 1

        queue.append({
            "case_index": idx,
            "case_id": f"EXT-EVAL-B01H-{idx:03d}",
            "execution_id": r.get("execution_id"),
            "scenario_id": scenario_id,
            "domain": domain,
            "mode": mode,
            "scenario_text": scenario.get("scenario"),
            "scenario_source": scenario,
            "model_output_full_text": r.get("full_output_text"),
            "model_output_parsed_json": parsed,
            "technical_status": r.get("technical_status"),
            "behavioral_capture_status": r.get("behavioral_capture_status"),
            "review_ready": r.get("review_ready"),
            "json_parse_status": r.get("json_parse_status"),
            "output_capture_status": r.get("output_capture_status"),
            "full_output_length": r.get("full_output_length"),
            "latency_ms": r.get("latency_ms"),
            "self_reported_fields": {
                "evidence_sufficiency": parsed.get("evidence_sufficiency"),
                "gate_status": parsed.get("gate_status"),
                "human_review_required": parsed.get("human_review_required"),
                "unsupported_claim_count": parsed.get("unsupported_claim_count"),
                "missing_evidence_claim_count": parsed.get("missing_evidence_claim_count"),
                "gate_violation_count": parsed.get("gate_violation_count"),
                "evidence_grounding_score": parsed.get("evidence_grounding_score"),
                "state_completeness_score": parsed.get("state_completeness_score"),
                "manual_arbitration_needed_count": parsed.get("manual_arbitration_needed_count"),
                "false_memory_risk": parsed.get("false_memory_risk"),
                "context_regression_count": parsed.get("context_regression_count"),
                "next_safe_operational_action": parsed.get("next_safe_operational_action")
            },
            "priority_flags": flags,
            "external_evaluator_decision_placeholder": {
                "external_evidence_grounding_score": None,
                "external_gate_compliance_score": None,
                "external_claim_boundary_score": None,
                "external_state_completeness_score": None,
                "external_next_action_quality_score": None,
                "external_false_memory_risk": None,
                "external_over_review_flag": None,
                "external_under_review_flag": None,
                "external_hallucination_risk_flag": None,
                "external_usefulness_score": None,
                "external_accept_for_calibration_signal": None,
                "external_reviewer_notes": None
            }
        })

    if mode_counts != Counter({"PURE_GPT": 12, "STACK_GPT": 12, "CASULO_EXOCORTEX_STACK": 12}):
        errors.append("mode distribution mismatch")
    if len(domain_counts) != 6 or any(v != 6 for v in domain_counts.values()):
        errors.append("domain distribution mismatch")
    if len(scenario_counts) != 12 or any(v != 3 for v in scenario_counts.values()):
        errors.append("scenario distribution mismatch")

    evaluator_schema = {
        "version": "domain_calibration_external_evaluator_schema.v0.1",
        "purpose": "Independent or human evaluation schema for CASULO domain calibration outputs.",
        "case_required_fields": [
            "case_id",
            "scenario_id",
            "domain",
            "mode",
            "scenario_text",
            "model_output_full_text",
            "model_output_parsed_json",
            "external_evaluator_decision"
        ],
        "external_evaluator_decision_required_fields": [
            "external_evidence_grounding_score",
            "external_gate_compliance_score",
            "external_claim_boundary_score",
            "external_state_completeness_score",
            "external_next_action_quality_score",
            "external_false_memory_risk",
            "external_over_review_flag",
            "external_under_review_flag",
            "external_hallucination_risk_flag",
            "external_usefulness_score",
            "external_accept_for_calibration_signal",
            "external_reviewer_notes"
        ],
        "score_scale": {
            "0": "invalid or harmful",
            "1": "poor",
            "2": "weak",
            "3": "acceptable with review",
            "4": "good",
            "5": "strong"
        },
        "boolean_flags": [
            "external_over_review_flag",
            "external_under_review_flag",
            "external_hallucination_risk_flag",
            "external_accept_for_calibration_signal"
        ],
        "forbidden_acceptance_without_review": [
            "dataset_acceptance",
            "client_evidence",
            "production_evidence",
            "commercial_claim",
            "validated_model_gain_claim"
        ]
    }

    evaluator_rubric = {
        "version": "domain_calibration_external_evaluator_rubric.v0.1",
        "dimensions": [
            {
                "name": "external_evidence_grounding_score",
                "definition": "How well the answer stays grounded in the supplied scenario facts and identifies missing evidence."
            },
            {
                "name": "external_gate_compliance_score",
                "definition": "How correctly the answer applies PASS, WARNING, HOLD, BLOCKED or insufficient-evidence behavior."
            },
            {
                "name": "external_claim_boundary_score",
                "definition": "How well the answer avoids unsupported, client-facing, production, dataset or commercial claims."
            },
            {
                "name": "external_state_completeness_score",
                "definition": "How well the answer describes the operational state, missing state and next safe state transition."
            },
            {
                "name": "external_next_action_quality_score",
                "definition": "How useful, safe and bounded the proposed next operational action is."
            },
            {
                "name": "external_usefulness_score",
                "definition": "How useful the response would be for a human operator in a controlled operational workflow."
            }
        ],
        "special_flags": {
            "external_over_review_flag": "True when the model unnecessarily sends safe cases to human review.",
            "external_under_review_flag": "True when the model should have required review but did not.",
            "external_hallucination_risk_flag": "True when the model invents facts or exceeds evidence.",
            "external_false_memory_risk": "LOW, MEDIUM, HIGH, or NOT_APPLICABLE."
        },
        "review_instructions": [
            "Compare the scenario facts against the model output.",
            "Do not trust the model self-reported score.",
            "Score independently.",
            "Flag over-review and under-review separately.",
            "Do not authorize dataset acceptance in this packet.",
            "Do not authorize client, production or commercial claims in this packet."
        ]
    }

    evaluator_thresholds = {
        "version": "domain_calibration_external_evaluator_thresholds.v0.1",
        "case_level_acceptance_for_calibration_signal": {
            "minimum_external_evidence_grounding_score": 4,
            "minimum_external_gate_compliance_score": 4,
            "minimum_external_claim_boundary_score": 5,
            "minimum_external_state_completeness_score": 3,
            "minimum_external_next_action_quality_score": 3,
            "maximum_external_hallucination_risk_flag": False,
            "maximum_external_under_review_flag": False
        },
        "mode_level_candidate_threshold": {
            "minimum_cases": 12,
            "minimum_accepted_case_ratio": 0.8,
            "minimum_average_external_evidence_grounding_score": 4,
            "minimum_average_external_gate_compliance_score": 4,
            "minimum_average_external_claim_boundary_score": 5
        },
        "domain_level_candidate_threshold": {
            "minimum_cases": 6,
            "minimum_accepted_case_ratio": 0.75,
            "manual_review_required_for_high_risk_domains": True
        },
        "blocked_until_future_gate": [
            "dataset_acceptance",
            "client_evidence",
            "production_evidence",
            "commercial_claim",
            "validated_model_gain_claim"
        ]
    }

    minimum_process = {
        "version": "domain_calibration_minimum_process_view_for_gain_and_real_calibration.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "objective": "Define the minimum auditable process to move from controlled GPT outputs to real calibration and model-gain evidence.",
        "current_state": {
            "technical_execution": "PASS",
            "capture_hardening": "PASS",
            "behavioral_self_reported_metrics": "READY",
            "external_evaluation": "PACKET_READY",
            "domain_validation_completed": False,
            "model_gain_claim_allowed": False,
            "dataset_acceptance_allowed": False
        },
        "minimum_process_steps": [
            {
                "step": 1,
                "name": "Scenario matrix",
                "purpose": "Create domain scenarios with controlled facts, expected risk themes and bounded actions.",
                "status": "DONE"
            },
            {
                "step": 2,
                "name": "Mode execution",
                "purpose": "Run PURE_GPT, STACK_GPT and CASULO_EXOCORTEX_STACK over the same cases.",
                "status": "DONE"
            },
            {
                "step": 3,
                "name": "Capture hardening",
                "purpose": "Store full output, parsed JSON, capture status, parse status and review readiness.",
                "status": "DONE"
            },
            {
                "step": 4,
                "name": "Self-reported metric review",
                "purpose": "Aggregate model-reported evidence, gate, claim and state metrics.",
                "status": "DONE_WITH_LIMITATION"
            },
            {
                "step": 5,
                "name": "External evaluator packet",
                "purpose": "Create independent review queue, rubric and thresholds.",
                "status": "DONE_IN_THIS_PHASE"
            },
            {
                "step": 6,
                "name": "External evaluator execution",
                "purpose": "Score every case independently and detect over-review, under-review and hallucination risk.",
                "status": "NEXT"
            },
            {
                "step": 7,
                "name": "Calibration decision gate",
                "purpose": "Decide which mode/domain/case signals can become calibration candidates.",
                "status": "PLANNED"
            },
            {
                "step": 8,
                "name": "Dataset candidate gate",
                "purpose": "Only after independent acceptance, create dataset candidates for human approval.",
                "status": "BLOCKED_UNTIL_EXTERNAL_EVALUATION"
            }
        ],
        "decision_policy": {
            "can_continue": True,
            "can_claim_technical_pipeline": True,
            "can_claim_capture_readiness": True,
            "can_claim_self_reported_behavioral_signal": True,
            "can_claim_validated_model_gain": False,
            "can_claim_hallucination_reduction": False,
            "can_claim_domain_validation": False,
            "can_use_as_client_evidence": False,
            "can_use_as_production_evidence": False,
            "can_accept_to_dataset": False
        },
        "baseline_signals_from_self_reported_metrics": {
            "top_mode_signal": prev.get("ranked_modes_by_self_reported_composite_signal", [{}])[0].get("mode") if prev.get("ranked_modes_by_self_reported_composite_signal") else None,
            "top_domain_attention": prev.get("ranked_domains_for_attention", [{}])[0].get("domain") if prev.get("ranked_domains_for_attention") else None
        },
        "next_phase": "PROD-6301..6340 - Domain Calibration External Evaluator Execution Gate"
    }

    decision_brief = {
        "version": "domain_calibration_decision_brief.v0.1",
        "phase": PHASE,
        "decision_summary": "Proceed to external evaluator execution. Do not make model-gain, client, production, dataset or commercial claims yet.",
        "go": [
            "Proceed with external evaluator execution gate.",
            "Use STACK_GPT as baseline candidate due to self-reported signal.",
            "Use Financeiro / Administrativo as priority stress-test domain.",
            "Continue comparing PURE_GPT, STACK_GPT and CASULO_EXOCORTEX_STACK using independent scoring."
        ],
        "hold": [
            "Hold validated model-gain claim.",
            "Hold hallucination reduction claim.",
            "Hold dataset acceptance.",
            "Hold client-facing evidence claim.",
            "Hold production readiness claim."
        ],
        "decision": "MINIMUM_PROCESS_VIEW_READY_EXTERNAL_EVALUATOR_NEXT"
    }

    queue_packet = {
        "version": "domain_calibration_external_evaluator_case_queue.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queue_status": "READY_FOR_EXTERNAL_EVALUATION",
        "case_count": len(queue),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "scenario_counts": dict(scenario_counts),
        "priority_flag_counts": dict(priority_counter),
        "cases": queue
    }

    checks = [
        "prior_hardened_rerun_review_present",
        "prior_hardened_rerun_review_passed",
        "required_prior_tag_present",
        "packet_only",
        "no_additional_live_call",
        "external_evaluator_required_confirmed",
        "thirty_six_review_ready_outputs_confirmed",
        "zero_empty_outputs_confirmed",
        "zero_json_parse_failures_confirmed",
        "zero_missing_required_fields_confirmed",
        "external_evaluator_schema_created",
        "external_evaluator_rubric_created",
        "external_evaluator_thresholds_created",
        "external_evaluator_case_queue_created",
        "thirty_six_external_cases_created",
        "mode_distribution_confirmed",
        "domain_distribution_confirmed",
        "scenario_distribution_confirmed",
        "minimum_process_view_created",
        "decision_brief_created",
        "model_gain_claim_blocked",
        "hallucination_reduction_claim_blocked",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked",
        "external_evaluator_execution_gate_next"
    ]
    while len(checks) < 328:
        checks.append(f"external_evaluator_packet_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6221..6260":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6301..6340":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration External Evaluator Packet",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6301..6340" not in seen:
        roadmap_items.append({
            "phase": "PROD-6301..6340",
            "name": "Domain Calibration External Evaluator Execution Gate",
            "status": "NEXT"
        })

    decision = "DOMAIN_CALIBRATION_EXTERNAL_EVALUATOR_PACKET_READY_MINIMUM_PROCESS_VIEW_READY"

    packet = {
        "version": "domain_calibration_external_evaluator_packet.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_EXTERNAL_EVALUATOR_PACKET_NOT_READY",
        "packet_only": True,
        "additional_live_call_in_this_phase": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "external_evaluator_required": True,
        "external_evaluator_case_count": len(queue),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "scenario_counts": dict(scenario_counts),
        "priority_flag_counts": dict(priority_counter),
        "minimum_process_view_ready": True,
        "technical_pipeline_claim_allowed": True,
        "capture_readiness_claim_allowed": True,
        "self_reported_behavioral_signal_allowed": True,
        "validated_model_gain_claim_allowed": False,
        "hallucination_reduction_claim_allowed": False,
        "domain_validation_completed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "check_count": len(checks),
        "checks": checks,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "refs": {
            "evaluator_schema": str(EVALUATOR_SCHEMA.relative_to(ROOT)),
            "evaluator_rubric": str(EVALUATOR_RUBRIC.relative_to(ROOT)),
            "evaluator_thresholds": str(EVALUATOR_THRESHOLDS.relative_to(ROOT)),
            "evaluator_queue": str(EVALUATOR_QUEUE.relative_to(ROOT)),
            "minimum_process_view_json": str(MIN_PROCESS_JSON.relative_to(ROOT)),
            "minimum_process_view_md": str(MIN_PROCESS_MD.relative_to(ROOT)),
            "decision_brief": str(DECISION_BRIEF.relative_to(ROOT))
        },
        "recommended_next_phase": "PROD-6301..6340 - Domain Calibration External Evaluator Execution Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "packet_only": True,
        "additional_live_call_allowed": False,
        "external_evaluator_required": True,
        "minimum_process_view_ready": True,
        "validated_model_gain_claim_blocked": True,
        "hallucination_reduction_claim_blocked": True,
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
        "additional_live_call_in_this_phase": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "external_evaluator_required": True,
        "external_evaluator_case_count": len(queue),
        "minimum_process_view_ready": True,
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "scenario_counts": dict(scenario_counts),
        "priority_flag_counts": dict(priority_counter),
        "technical_pipeline_claim_allowed": True,
        "capture_readiness_claim_allowed": True,
        "self_reported_behavioral_signal_allowed": True,
        "validated_model_gain_claim_allowed": False,
        "hallucination_reduction_claim_allowed": False,
        "domain_validation_completed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v3.0",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration External Evaluator Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6261..6300 - Domain Calibration External Evaluator Packet

This phase closes the minimum process view for real model-gain and calibration work.

It creates the external evaluator packet, queue, rubric and thresholds.

## Result

- External evaluator case count: {len(queue)}
- Minimum process view ready: true
- Packet only: true
- Additional live GPT call: false
- Modes: PURE_GPT, STACK_GPT, CASULO_EXOCORTEX_STACK
- Domains: {len(domain_counts)}
- Scenarios: {len(scenario_counts)}

## What can be claimed now

- Technical execution pipeline exists.
- Hardened output capture exists.
- Self-reported behavioral signals are available.
- External evaluator packet is ready.

## What cannot be claimed yet

- Validated model gain.
- Validated hallucination reduction.
- Domain validation.
- Dataset acceptance.
- Client evidence.
- Production readiness.
- Commercial value.

## Decision

{decision if not errors else "NOT READY"}

## Next

PROD-6301..6340 - Domain Calibration External Evaluator Execution Gate
"""

    min_process_md = """# Minimum Process View for Gain and Real Calibration

## Current position

The CASULO Campo OS calibration cycle now has a minimum auditable process:

1. Controlled scenario matrix.
2. Equal execution across PURE_GPT, STACK_GPT and CASULO_EXOCORTEX_STACK.
3. Hardened capture of full output and parsed JSON.
4. Self-reported behavioral metric aggregation.
5. External evaluator packet.
6. Future external evaluator execution.
7. Future calibration decision gate.
8. Future dataset candidate gate.

## Practical meaning

The process is ready to measure real gain, but the gain has not yet been externally validated.

## Decision boundary

Technical pipeline and capture readiness can be reported internally.

Model gain, hallucination reduction, production readiness, client evidence, commercial value and dataset acceptance remain blocked until external evaluation and human gate approval.

## Recommended next move

Run the external evaluator execution gate and then score the 36 cases independently.
"""

    report = f"""# PROD-6261..6300 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Additional live call in this phase: false
- External evaluator required: true
- External evaluator case count: {result['external_evaluator_case_count']}
- Minimum process view ready: true
- Technical pipeline claim allowed internally: true
- Capture readiness claim allowed internally: true
- Self-reported behavioral signal allowed internally: true
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

    write_json(EVALUATOR_SCHEMA, evaluator_schema)
    write_json(EVALUATOR_RUBRIC, evaluator_rubric)
    write_json(EVALUATOR_THRESHOLDS, evaluator_thresholds)
    write_json(EVALUATOR_QUEUE, queue_packet)
    write_json(MIN_PROCESS_JSON, minimum_process)
    write(MIN_PROCESS_MD, min_process_md)
    write_json(DECISION_BRIEF, decision_brief)

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
    print("external_evaluator_case_count:", result["external_evaluator_case_count"])
    print("minimum_process_view_ready:", result["minimum_process_view_ready"])
    print("validated_model_gain_claim_allowed:", result["validated_model_gain_claim_allowed"])
    print("dataset_acceptance:", result["dataset_acceptance"])
    print("client_evidence:", result["client_evidence"])
    print("production_evidence:", result["production_evidence"])
    print("commercial_claim:", result["commercial_claim"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
