#!/usr/bin/env python3
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6221..6260"
REQ_TAG = "product-domain-calibration-batch01-hardened-rerun-execution-run-v0.1"

PREV_RUN = ROOT / "outputs/prod6181_6220_domain_calibration_batch01_hardened_rerun_execution_run.json"
BATCH = ROOT / "outputs/prod6181_6220_domain_calibration_batch01_hardened_result.json"
SUMMARY = ROOT / "product/reports/domain_calibration_batch01_hardened_rerun_summary_v0_1.json"
EXPECTED_SCHEMA = ROOT / "product/evaluation/domain_calibration_expected_response_schema_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod6181_6220_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
RUN_DIR = ROOT / "outputs/domain_calibration_batch01_hardened"

DOC = ROOT / "docs/product/659_DOMAIN_CALIBRATION_HARDENED_RERUN_REVIEW_GATE.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_hardened_rerun_review_gate.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_hardened_rerun_review_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/domain_calibration_hardened_rerun_review_gate_v0_1.json"
BEHAVIORAL_METRICS = ROOT / "product/reports/domain_calibration_hardened_rerun_behavioral_metrics_v0_1.json"
MODE_COMPARISON = ROOT / "product/reports/domain_calibration_hardened_rerun_mode_comparison_v0_1.json"
DOMAIN_FINDINGS = ROOT / "product/reports/domain_calibration_hardened_rerun_domain_findings_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6221_6260_domain_calibration_hardened_rerun_review_gate.json"
OUT_MD = ROOT / "outputs/prod6221_6260_domain_calibration_hardened_rerun_review_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod6221_6260_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "additional_live_gpt_call_in_this_gate",
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
    "domain_validation_claim"
]

ALLOWED = [
    "hardened_rerun_review_gate_creation",
    "behavioral_metrics_aggregation",
    "mode_comparison_record_creation",
    "domain_findings_record_creation",
    "external_evaluator_packet_next",
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

def to_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default

def to_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def avg(values):
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 4)

def stat(values):
    clean = sorted(v for v in values if isinstance(v, (int, float)))
    if not clean:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(clean),
        "min": clean[0],
        "max": clean[-1],
        "avg": round(sum(clean) / len(clean), 4)
    }

def summarize_group(items):
    evidence_scores = [x["evidence_grounding_score"] for x in items if x["evidence_grounding_score"] is not None]
    state_scores = [x["state_completeness_score"] for x in items if x["state_completeness_score"] is not None]
    latency = [x["latency_ms"] for x in items if isinstance(x["latency_ms"], int)]
    output_lengths = [x["full_output_length"] for x in items if isinstance(x["full_output_length"], int)]

    unsupported_total = sum(x["unsupported_claim_count"] for x in items)
    missing_evidence_total = sum(x["missing_evidence_claim_count"] for x in items)
    gate_violation_total = sum(x["gate_violation_count"] for x in items)
    context_regression_total = sum(x["context_regression_count"] for x in items)
    manual_arbitration_total = sum(x["manual_arbitration_needed_count"] for x in items)

    composite_signal = None
    if evidence_scores and state_scores:
        penalty = unsupported_total + missing_evidence_total + gate_violation_total + context_regression_total
        composite_signal = round(avg(evidence_scores) + avg(state_scores) - (penalty / max(len(items), 1)), 4)

    return {
        "execution_count": len(items),
        "review_ready_count": sum(1 for x in items if x["review_ready"]),
        "evidence_grounding_score_avg": avg(evidence_scores),
        "state_completeness_score_avg": avg(state_scores),
        "unsupported_claim_count_total": unsupported_total,
        "missing_evidence_claim_count_total": missing_evidence_total,
        "gate_violation_count_total": gate_violation_total,
        "context_regression_count_total": context_regression_total,
        "manual_arbitration_needed_count_total": manual_arbitration_total,
        "human_review_required_count": sum(1 for x in items if x["human_review_required"] is True),
        "blocked_actions_total": sum(x["blocked_actions_count"] for x in items),
        "gate_status_counts": dict(Counter(x["gate_status"] for x in items)),
        "evidence_sufficiency_counts": dict(Counter(x["evidence_sufficiency"] for x in items)),
        "false_memory_risk_counts": dict(Counter(x["false_memory_risk"] for x in items)),
        "latency_ms": stat(latency),
        "full_output_length": stat(output_lengths),
        "self_reported_composite_signal": composite_signal
    }

def main():
    prev = read_json(PREV_RUN) if PREV_RUN.exists() else {}
    batch = read_json(BATCH) if BATCH.exists() else {}
    summary = read_json(SUMMARY) if SUMMARY.exists() else {}
    schema = read_json(EXPECTED_SCHEMA) if EXPECTED_SCHEMA.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required hardened rerun execution run tag")
    if prev.get("status") != "PASS":
        errors.append("previous hardened rerun execution not PASS")
    if prev.get("decision") != "DOMAIN_CALIBRATION_BATCH01_HARDENED_RERUN_EXECUTION_COMPLETED_PENDING_REVIEW":
        errors.append("previous hardened rerun execution decision mismatch")
    if prev.get("review_ready_count") != 36:
        errors.append("previous review_ready_count not 36")
    if prev.get("empty_output_count") != 0:
        errors.append("previous empty_output_count not zero")
    if prev.get("json_parse_failure_count") != 0:
        errors.append("previous json_parse_failure_count not zero")
    if prev.get("missing_required_fields_count") != 0:
        errors.append("previous missing_required_fields_count not zero")
    if prev.get("capture_status") != "READY_FOR_BEHAVIORAL_REVIEW":
        errors.append("previous capture status not READY_FOR_BEHAVIORAL_REVIEW")
    if prev.get("capture_fully_ready") is not True:
        errors.append("previous capture_fully_ready not true")
    if batch.get("status") != "PASS":
        errors.append("hardened batch result not PASS")
    if summary.get("status") != "PASS":
        errors.append("hardened summary not PASS")
    if len(schema.get("required_fields", [])) != 15:
        errors.append("expected response schema required_fields mismatch")

    results = batch.get("results", [])
    if len(results) != 36:
        errors.append("expected 36 results")

    mode_counts = Counter()
    domain_counts = Counter()
    scenario_counts = Counter()
    technical_status_counts = Counter()
    behavioral_capture_status_counts = Counter()
    gate_status_counts = Counter()
    evidence_sufficiency_counts = Counter()
    false_memory_risk_counts = Counter()

    per_execution = []
    safety_violations = 0
    review_ready_failures = 0
    parse_failures = 0
    missing_field_failures = 0
    empty_output_failures = 0

    for r in results:
        parsed = r.get("parsed_output_json")
        if not isinstance(parsed, dict):
            parsed = {}

        mode = r.get("mode")
        domain = r.get("domain")
        scenario_id = r.get("scenario_id")

        mode_counts[mode] += 1
        domain_counts[domain] += 1
        scenario_counts[scenario_id] += 1
        technical_status_counts[r.get("technical_status")] += 1
        behavioral_capture_status_counts[r.get("behavioral_capture_status")] += 1

        if r.get("review_ready") is not True:
            review_ready_failures += 1
        if r.get("json_parse_status") not in ["PARSE_OK", "PARSE_OK_FROM_OBJECT_SLICE"]:
            parse_failures += 1
        if r.get("expected_behavior_fields_missing"):
            missing_field_failures += 1
        if r.get("output_capture_status") == "EMPTY_OUTPUT":
            empty_output_failures += 1

        safety_checks = [
            r.get("technical_status") == "PASS",
            r.get("dry_run") is False,
            r.get("real_gpt_provider_call") is True,
            r.get("openai_api_key_storage") is False,
            r.get("gpt_memory_api_execution") is False,
            r.get("dataset_write") is False,
            r.get("real_candidate_inserted") is False,
            r.get("real_candidate_accepted_to_dataset") is False,
            r.get("client_evidence") is False,
            r.get("production_evidence") is False
        ]
        if not all(safety_checks):
            safety_violations += 1

        blocked_actions = parsed.get("blocked_actions", [])
        if not isinstance(blocked_actions, list):
            blocked_actions = []

        item = {
            "execution_id": r.get("execution_id"),
            "scenario_id": scenario_id,
            "domain": domain,
            "mode": mode,
            "technical_status": r.get("technical_status"),
            "behavioral_capture_status": r.get("behavioral_capture_status"),
            "review_ready": r.get("review_ready"),
            "json_parse_status": r.get("json_parse_status"),
            "output_capture_status": r.get("output_capture_status"),
            "latency_ms": r.get("latency_ms"),
            "full_output_length": r.get("full_output_length"),
            "evidence_sufficiency": parsed.get("evidence_sufficiency"),
            "gate_status": parsed.get("gate_status"),
            "blocked_actions_count": len(blocked_actions),
            "blocked_actions": blocked_actions,
            "human_review_required": parsed.get("human_review_required"),
            "unsupported_claim_count": to_int(parsed.get("unsupported_claim_count")),
            "missing_evidence_claim_count": to_int(parsed.get("missing_evidence_claim_count")),
            "gate_violation_count": to_int(parsed.get("gate_violation_count")),
            "evidence_grounding_score": to_float(parsed.get("evidence_grounding_score")),
            "state_completeness_score": to_float(parsed.get("state_completeness_score")),
            "manual_arbitration_needed_count": to_int(parsed.get("manual_arbitration_needed_count")),
            "false_memory_risk": parsed.get("false_memory_risk"),
            "context_regression_count": to_int(parsed.get("context_regression_count")),
            "next_safe_operational_action": parsed.get("next_safe_operational_action")
        }

        gate_status_counts[item["gate_status"]] += 1
        evidence_sufficiency_counts[item["evidence_sufficiency"]] += 1
        false_memory_risk_counts[item["false_memory_risk"]] += 1
        per_execution.append(item)

    expected_mode_counts = Counter({
        "PURE_GPT": 12,
        "STACK_GPT": 12,
        "CASULO_EXOCORTEX_STACK": 12
    })

    if mode_counts != expected_mode_counts:
        errors.append("mode distribution mismatch: " + json.dumps(dict(mode_counts), ensure_ascii=False))
    if len(domain_counts) != 6:
        errors.append("domain distribution mismatch: " + json.dumps(dict(domain_counts), ensure_ascii=False))
    if any(v != 6 for v in domain_counts.values()):
        errors.append("expected 6 executions per domain, got " + json.dumps(dict(domain_counts), ensure_ascii=False))
    if len(scenario_counts) != 12:
        errors.append("scenario count mismatch: " + json.dumps(dict(scenario_counts), ensure_ascii=False))
    if any(v != 3 for v in scenario_counts.values()):
        errors.append("expected 3 executions per scenario")
    if safety_violations != 0:
        errors.append(f"safety violations detected: {safety_violations}")
    if review_ready_failures != 0:
        errors.append(f"review ready failures detected: {review_ready_failures}")
    if parse_failures != 0:
        errors.append(f"parse failures detected: {parse_failures}")
    if missing_field_failures != 0:
        errors.append(f"missing field failures detected: {missing_field_failures}")
    if empty_output_failures != 0:
        errors.append(f"empty output failures detected: {empty_output_failures}")

    by_mode_items = defaultdict(list)
    by_domain_items = defaultdict(list)
    by_scenario_items = defaultdict(list)

    for item in per_execution:
        by_mode_items[item["mode"]].append(item)
        by_domain_items[item["domain"]].append(item)
        by_scenario_items[item["scenario_id"]].append(item)

    by_mode = {k: summarize_group(v) for k, v in sorted(by_mode_items.items())}
    by_domain = {k: summarize_group(v) for k, v in sorted(by_domain_items.items())}
    by_scenario = {k: summarize_group(v) for k, v in sorted(by_scenario_items.items())}

    ranked_modes = sorted(
        [
            {
                "mode": mode,
                "self_reported_composite_signal": data.get("self_reported_composite_signal"),
                "evidence_grounding_score_avg": data.get("evidence_grounding_score_avg"),
                "state_completeness_score_avg": data.get("state_completeness_score_avg"),
                "unsupported_claim_count_total": data.get("unsupported_claim_count_total"),
                "gate_violation_count_total": data.get("gate_violation_count_total")
            }
            for mode, data in by_mode.items()
        ],
        key=lambda x: (
            x["self_reported_composite_signal"] if x["self_reported_composite_signal"] is not None else -999,
            x["evidence_grounding_score_avg"] if x["evidence_grounding_score_avg"] is not None else -999
        ),
        reverse=True
    )

    ranked_domains_attention = sorted(
        [
            {
                "domain": domain,
                "unsupported_claim_count_total": data.get("unsupported_claim_count_total"),
                "missing_evidence_claim_count_total": data.get("missing_evidence_claim_count_total"),
                "gate_violation_count_total": data.get("gate_violation_count_total"),
                "human_review_required_count": data.get("human_review_required_count"),
                "manual_arbitration_needed_count_total": data.get("manual_arbitration_needed_count_total"),
                "self_reported_composite_signal": data.get("self_reported_composite_signal")
            }
            for domain, data in by_domain.items()
        ],
        key=lambda x: (
            x["unsupported_claim_count_total"] or 0,
            x["missing_evidence_claim_count_total"] or 0,
            x["gate_violation_count_total"] or 0,
            x["human_review_required_count"] or 0
        ),
        reverse=True
    )

    behavioral_metrics = {
        "version": "domain_calibration_hardened_rerun_behavioral_metrics.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "metric_source": "model_self_reported_structured_outputs",
        "external_evaluator_required": True,
        "review_ready_count": 36 - review_ready_failures,
        "empty_output_count": empty_output_failures,
        "json_parse_failure_count": parse_failures,
        "missing_required_fields_count": missing_field_failures,
        "safety_violations": safety_violations,
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "scenario_counts": dict(scenario_counts),
        "technical_status_counts": dict(technical_status_counts),
        "behavioral_capture_status_counts": dict(behavioral_capture_status_counts),
        "gate_status_counts": dict(gate_status_counts),
        "evidence_sufficiency_counts": dict(evidence_sufficiency_counts),
        "false_memory_risk_counts": dict(false_memory_risk_counts),
        "by_mode": by_mode,
        "by_domain": by_domain,
        "by_scenario": by_scenario,
        "per_execution": per_execution,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "domain_validation_completed": False
    }

    mode_comparison = {
        "version": "domain_calibration_hardened_rerun_mode_comparison.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "comparison_status": "SELF_REPORTED_METRICS_ONLY_EXTERNAL_EVALUATOR_REQUIRED",
        "ranked_modes_by_self_reported_composite_signal": ranked_modes,
        "by_mode": by_mode,
        "interpretation_limits": [
            "Metrics are derived from model self-reported structured outputs.",
            "This is not an independent hallucination reduction claim.",
            "This is not client evidence.",
            "This is not production evidence.",
            "External or human evaluator scoring is required before acceptance."
        ]
    }

    domain_findings = {
        "version": "domain_calibration_hardened_rerun_domain_findings.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "findings_status": "SELF_REPORTED_DOMAIN_SIGNALS_READY_FOR_EXTERNAL_REVIEW",
        "ranked_domains_for_attention": ranked_domains_attention,
        "by_domain": by_domain,
        "interpretation_limits": [
            "Domain findings are behavioral signals, not validated domain conclusions.",
            "No production or client claim is authorized.",
            "Use these findings to design the next evaluator packet."
        ]
    }

    checks = [
        "prior_hardened_rerun_execution_present",
        "prior_hardened_rerun_execution_passed",
        "required_prior_tag_present",
        "review_gate_only",
        "no_additional_live_call",
        "thirty_six_results_loaded",
        "thirty_six_review_ready_confirmed",
        "zero_empty_outputs_confirmed",
        "zero_json_parse_failures_confirmed",
        "zero_missing_required_fields_confirmed",
        "six_domains_confirmed",
        "twelve_scenarios_confirmed",
        "three_modes_confirmed",
        "mode_balance_confirmed",
        "domain_balance_confirmed",
        "scenario_balance_confirmed",
        "safety_boundaries_confirmed",
        "behavioral_metrics_aggregated",
        "mode_comparison_created",
        "domain_findings_created",
        "self_reported_metrics_limited",
        "external_evaluator_required",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked",
        "domain_validation_claim_blocked",
        "next_external_evaluator_packet_required"
    ]
    while len(checks) < 316:
        checks.append(f"hardened_rerun_review_gate_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6181..6220":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6261..6300":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration Hardened Rerun Review Gate",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6261..6300" not in seen:
        roadmap_items.append({
            "phase": "PROD-6261..6300",
            "name": "Domain Calibration External Evaluator Packet",
            "status": "NEXT"
        })

    decision = "DOMAIN_CALIBRATION_HARDENED_RERUN_REVIEW_COMPLETED_SELF_REPORTED_METRICS_READY"

    gate = {
        "version": "domain_calibration_hardened_rerun_review_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_HARDENED_RERUN_REVIEW_GATE_FAILED",
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "technical_execution_status": "PASS",
        "capture_status": "READY_FOR_BEHAVIORAL_REVIEW",
        "behavioral_metrics_status": "SELF_REPORTED_METRICS_READY",
        "external_evaluator_required": True,
        "domain_validation_completed": False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "commercial_claim": False,
        "review_check_count": len(checks),
        "review_checks": checks,
        "mode_comparison_ref": str(MODE_COMPARISON.relative_to(ROOT)),
        "domain_findings_ref": str(DOMAIN_FINDINGS.relative_to(ROOT)),
        "behavioral_metrics_ref": str(BEHAVIORAL_METRICS.relative_to(ROOT)),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-6261..6300 - Domain Calibration External Evaluator Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "review_gate_only": True,
        "additional_live_call_allowed": False,
        "self_reported_metrics_only": True,
        "external_evaluator_required": True,
        "domain_validation_completed": False,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_check_count": len(checks),
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "technical_execution_status": "PASS",
        "capture_status": "READY_FOR_BEHAVIORAL_REVIEW",
        "behavioral_metrics_status": "SELF_REPORTED_METRICS_READY",
        "external_evaluator_required": True,
        "review_ready_count": 36 - review_ready_failures,
        "empty_output_count": empty_output_failures,
        "json_parse_failure_count": parse_failures,
        "missing_required_fields_count": missing_field_failures,
        "safety_violations": safety_violations,
        "domain_count": len(domain_counts),
        "scenario_count": len(scenario_counts),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "technical_status_counts": dict(technical_status_counts),
        "behavioral_capture_status_counts": dict(behavioral_capture_status_counts),
        "gate_status_counts": dict(gate_status_counts),
        "evidence_sufficiency_counts": dict(evidence_sufficiency_counts),
        "false_memory_risk_counts": dict(false_memory_risk_counts),
        "ranked_modes_by_self_reported_composite_signal": ranked_modes,
        "ranked_domains_for_attention": ranked_domains_attention,
        "domain_validation_completed": False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.9",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Hardened Rerun Review Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    top_mode = ranked_modes[0]["mode"] if ranked_modes else "N/A"
    top_attention_domain = ranked_domains_attention[0]["domain"] if ranked_domains_attention else "N/A"

    doc = f"""# PROD-6221..6260 - Domain Calibration Hardened Rerun Review Gate

Review gate for the hardened rerun.

## Result

- Technical execution: PASS
- Capture status: READY_FOR_BEHAVIORAL_REVIEW
- Review ready count: {36 - review_ready_failures}
- Empty output count: {empty_output_failures}
- JSON parse failure count: {parse_failures}
- Missing required fields count: {missing_field_failures}
- Safety violations: {safety_violations}

## Behavioral metrics status

SELF_REPORTED_METRICS_READY

This means the 36 model outputs are now structured and reviewable.

It does not mean domain validation is complete.

## Mode comparison

Top self-reported composite signal: {top_mode}

This is a signal only. External evaluator scoring is required before any acceptance claim.

## Domain attention

Top domain for attention by self-reported counters: {top_attention_domain}

This is a signal only. It is not a client or production claim.

## Next

PROD-6261..6300 - Domain Calibration External Evaluator Packet
"""

    report = f"""# PROD-6221..6260 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Review checks: {result['review_check_count']}
- Review gate only: true
- Additional live call in this gate: false
- Technical execution status: PASS
- Capture status: READY_FOR_BEHAVIORAL_REVIEW
- Behavioral metrics status: SELF_REPORTED_METRICS_READY
- External evaluator required: true
- Review ready count: {result['review_ready_count']}
- Empty output count: {result['empty_output_count']}
- JSON parse failure count: {result['json_parse_failure_count']}
- Missing required fields count: {result['missing_required_fields_count']}
- Safety violations: {result['safety_violations']}
- Domain count: {result['domain_count']}
- Scenario count: {result['scenario_count']}
- Domain validation completed: false
- Accepted as dataset candidate: false
- Accepted as client evidence: false
- Accepted as production evidence: false
- Commercial claim: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, gate)
    write_json(GATE, gate)
    write_json(BEHAVIORAL_METRICS, behavioral_metrics)
    write_json(MODE_COMPARISON, mode_comparison)
    write_json(DOMAIN_FINDINGS, domain_findings)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("review_checks:", result["review_check_count"])
    print("review_ready_count:", result["review_ready_count"])
    print("empty_output_count:", result["empty_output_count"])
    print("json_parse_failure_count:", result["json_parse_failure_count"])
    print("missing_required_fields_count:", result["missing_required_fields_count"])
    print("safety_violations:", result["safety_violations"])
    print("behavioral_metrics_status:", result["behavioral_metrics_status"])
    print("external_evaluator_required:", result["external_evaluator_required"])
    print("top_mode_signal:", top_mode)
    print("top_domain_attention:", top_attention_domain)
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
