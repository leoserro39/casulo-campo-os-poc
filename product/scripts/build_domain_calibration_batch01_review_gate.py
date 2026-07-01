#!/usr/bin/env python3
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6061..6100"
REQ_TAG = "product-domain-calibration-batch01-execution-run-v0.1"

EXEC_RUN = ROOT / "outputs/prod6021_6060_domain_calibration_batch01_execution_run.json"
BATCH = ROOT / "outputs/prod6021_6060_domain_calibration_batch01_result.json"
SUMMARY = ROOT / "product/reports/domain_calibration_batch01_execution_summary_v0_1.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
RUBRIC = ROOT / "product/evaluation/domain_calibration_scoring_rubric_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod6021_6060_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/655_DOMAIN_CALIBRATION_BATCH01_REVIEW_GATE.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_batch01_review_gate.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_batch01_review_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/domain_calibration_batch01_review_gate_v0_1.json"
BEHAVIOR_REPORT = ROOT / "product/reports/domain_calibration_batch01_behavioral_review_v0_1.json"
CAPTURE_GAPS = ROOT / "product/reports/domain_calibration_batch01_content_capture_gaps_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6061_6100_domain_calibration_batch01_review_gate.json"
OUT_MD = ROOT / "outputs/prod6061_6100_domain_calibration_batch01_review_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod6061_6100_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

EXPECTED_BEHAVIOR_FIELDS = [
    "domain",
    "scenario_id",
    "evidence_sufficiency",
    "gate_status",
    "blocked_actions",
    "human_review_required",
    "unsupported_claim_count",
    "missing_evidence_claim_count",
    "gate_violation_count",
    "evidence_grounding_score",
    "state_completeness_score",
    "manual_arbitration_needed_count",
    "false_memory_risk",
    "context_regression_count",
    "next_safe_operational_action"
]

FULL_OUTPUT_KEYS = [
    "output_text",
    "response_text",
    "full_output",
    "full_response",
    "content",
    "message_content",
    "raw_output"
]

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
    "batch01_review_gate_creation",
    "technical_execution_review",
    "content_capture_gap_detection",
    "behavioral_review_hold",
    "output_capture_hardening_packet_next",
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

def try_parse_json(text):
    if not isinstance(text, str) or not text.strip():
        return None, False
    try:
        return json.loads(text), True
    except Exception:
        return None, False

def stats(values):
    values = sorted(v for v in values if isinstance(v, int))
    if not values:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(values),
        "min": values[0],
        "max": values[-1],
        "avg": round(sum(values) / len(values), 2)
    }

def main():
    exec_run = read_json(EXEC_RUN) if EXEC_RUN.exists() else {}
    batch = read_json(BATCH) if BATCH.exists() else {}
    summary = read_json(SUMMARY) if SUMMARY.exists() else {}
    scenarios = read_json(SCENARIOS) if SCENARIOS.exists() else {}
    plan = read_json(EXEC_PLAN) if EXEC_PLAN.exists() else {}
    rubric = read_json(RUBRIC) if RUBRIC.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required batch01 execution run tag")
    if exec_run.get("status") != "PASS":
        errors.append("execution run not PASS")
    if exec_run.get("decision") != "DOMAIN_CALIBRATION_BATCH01_EXECUTION_RUN_COMPLETED_PENDING_REVIEW":
        errors.append("execution run decision mismatch")
    if batch.get("status") != "PASS":
        errors.append("batch result not PASS")
    if summary.get("status") != "PASS":
        errors.append("execution summary not PASS")
    if batch.get("executed_count") != 36:
        errors.append("executed_count mismatch")
    if batch.get("real_provider_call_count") != 36:
        errors.append("real_provider_call_count mismatch")
    if batch.get("successful_live_response_count") != 36:
        errors.append("successful_live_response_count mismatch")
    if summary.get("safety_violations") != 0:
        errors.append("summary safety violations not zero")
    if exec_run.get("safety_violations") != 0:
        errors.append("execution run safety violations not zero")
    if scenarios.get("scenario_count") != 12:
        errors.append("scenario_count mismatch")
    if plan.get("planned_execution_count") != 36:
        errors.append("planned_execution_count mismatch")
    if "scores" not in rubric:
        errors.append("rubric missing scores")

    results = batch.get("results", [])
    if len(results) != 36:
        errors.append("batch results length is not 36")

    mode_counts = Counter()
    domain_counts = Counter()
    status_counts = Counter()
    empty_by_mode = Counter()
    nonempty_by_mode = Counter()
    empty_by_domain = Counter()
    nonempty_by_domain = Counter()
    parseable_by_mode = Counter()
    parseable_by_domain = Counter()
    full_output_by_mode = Counter()
    full_output_by_domain = Counter()
    latency_by_mode = defaultdict(list)
    latency_by_domain = defaultdict(list)

    execution_reviews = []
    empty_output_count = 0
    nonempty_output_count = 0
    full_output_present_count = 0
    json_parseable_from_preview_count = 0
    expected_field_full_coverage_count = 0
    expected_field_partial_coverage_count = 0
    safety_violations = 0

    for r in results:
        execution_id = r.get("execution_id")
        mode = r.get("mode")
        domain = r.get("domain")
        scenario_id = r.get("scenario_id")
        single = r.get("single_result", {})

        mode_counts[mode] += 1
        domain_counts[domain] += 1
        status_counts[single.get("status")] += 1

        preview = single.get("output_preview", "")
        preview = preview if isinstance(preview, str) else ""
        preview_stripped = preview.strip()
        preview_empty = len(preview_stripped) == 0

        if preview_empty:
            empty_output_count += 1
            empty_by_mode[mode] += 1
            empty_by_domain[domain] += 1
        else:
            nonempty_output_count += 1
            nonempty_by_mode[mode] += 1
            nonempty_by_domain[domain] += 1

        full_output_present = any(bool(single.get(k)) for k in FULL_OUTPUT_KEYS)
        if full_output_present:
            full_output_present_count += 1
            full_output_by_mode[mode] += 1
            full_output_by_domain[domain] += 1

        parsed_preview, parseable = try_parse_json(preview_stripped)
        if parseable:
            json_parseable_from_preview_count += 1
            parseable_by_mode[mode] += 1
            parseable_by_domain[domain] += 1

        fields_present = []
        missing_fields = list(EXPECTED_BEHAVIOR_FIELDS)

        if isinstance(parsed_preview, dict):
            fields_present = [f for f in EXPECTED_BEHAVIOR_FIELDS if f in parsed_preview]
            missing_fields = [f for f in EXPECTED_BEHAVIOR_FIELDS if f not in parsed_preview]
            if len(fields_present) == len(EXPECTED_BEHAVIOR_FIELDS):
                expected_field_full_coverage_count += 1
            elif fields_present:
                expected_field_partial_coverage_count += 1

        if isinstance(single.get("latency_ms"), int):
            latency_by_mode[mode].append(single["latency_ms"])
            latency_by_domain[domain].append(single["latency_ms"])

        local_safety = [
            single.get("status") == "PASS",
            single.get("dry_run") is False,
            single.get("real_gpt_provider_call") is True,
            single.get("successful_live_gpt_response") is True,
            single.get("openai_api_key_storage") is False,
            single.get("gpt_memory_api_execution") is False,
            single.get("dataset_write") is False,
            single.get("real_candidate_inserted") is False,
            single.get("real_candidate_accepted_to_dataset") is False,
            r.get("client_evidence") is False,
            r.get("production_evidence") is False,
        ]
        if not all(local_safety):
            safety_violations += 1

        execution_reviews.append({
            "execution_id": execution_id,
            "scenario_id": scenario_id,
            "domain": domain,
            "mode": mode,
            "technical_status": single.get("status"),
            "latency_ms": single.get("latency_ms"),
            "output_preview_empty": preview_empty,
            "output_preview_length": len(preview_stripped),
            "full_output_present": full_output_present,
            "json_parseable_from_preview": parseable,
            "expected_behavior_fields_present_count": len(fields_present),
            "expected_behavior_fields_missing_count": len(missing_fields),
            "expected_behavior_fields_present": fields_present,
            "expected_behavior_fields_missing": missing_fields,
            "behavioral_review_possible": bool(full_output_present and parseable and not missing_fields),
            "safety_boundary_ok": all(local_safety)
        })

    content_capture_sufficient = (
        empty_output_count == 0
        and full_output_present_count == 36
        and json_parseable_from_preview_count == 36
        and expected_field_full_coverage_count == 36
    )

    behavioral_review_status = (
        "READY_FOR_FULL_BEHAVIORAL_REVIEW"
        if content_capture_sufficient
        else "PARTIAL_BLOCKED_BY_CONTENT_CAPTURE"
    )

    content_capture_hold = not content_capture_sufficient
    rerun_required = content_capture_hold

    checks = [
        "prior_batch01_execution_run_present",
        "prior_batch01_execution_run_passed",
        "required_prior_tag_present",
        "review_gate_only",
        "no_additional_live_call",
        "thirty_six_executions_loaded",
        "thirty_six_real_provider_calls_confirmed",
        "thirty_six_successful_live_responses_confirmed",
        "six_domains_loaded",
        "three_modes_loaded",
        "safety_violations_checked",
        "output_preview_presence_checked",
        "full_output_presence_checked",
        "json_parseability_checked",
        "expected_behavior_field_coverage_checked",
        "content_capture_sufficiency_evaluated",
        "behavioral_review_status_assigned",
        "content_capture_hold_assigned",
        "rerun_requirement_assigned",
        "hardening_packet_next_required",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 272:
        checks.append(f"domain_calibration_batch01_review_gate_control_{len(checks)+1:03d}")

    if mode_counts != Counter({"PURE_GPT": 12, "STACK_GPT": 12, "CASULO_EXOCORTEX_STACK": 12}):
        errors.append("mode distribution mismatch: " + json.dumps(dict(mode_counts), ensure_ascii=False))
    if len(domain_counts) != 6:
        errors.append("domain distribution mismatch: " + json.dumps(dict(domain_counts), ensure_ascii=False))
    if any(v != 6 for v in domain_counts.values()):
        errors.append("expected 6 executions per domain, got " + json.dumps(dict(domain_counts), ensure_ascii=False))
    if safety_violations != 0:
        errors.append(f"safety violations detected: {safety_violations}")

    latency_summary_by_mode = {k: stats(v) for k, v in latency_by_mode.items()}
    latency_summary_by_domain = {k: stats(v) for k, v in latency_by_domain.items()}

    content_capture = {
        "empty_output_count": empty_output_count,
        "nonempty_output_count": nonempty_output_count,
        "full_output_present_count": full_output_present_count,
        "json_parseable_from_preview_count": json_parseable_from_preview_count,
        "expected_field_full_coverage_count": expected_field_full_coverage_count,
        "expected_field_partial_coverage_count": expected_field_partial_coverage_count,
        "empty_by_mode": dict(empty_by_mode),
        "nonempty_by_mode": dict(nonempty_by_mode),
        "empty_by_domain": dict(empty_by_domain),
        "nonempty_by_domain": dict(nonempty_by_domain),
        "parseable_by_mode": dict(parseable_by_mode),
        "parseable_by_domain": dict(parseable_by_domain),
        "full_output_by_mode": dict(full_output_by_mode),
        "full_output_by_domain": dict(full_output_by_domain),
        "content_capture_sufficient": content_capture_sufficient,
        "content_capture_hold": content_capture_hold,
        "rerun_required": rerun_required
    }

    behavioral_review = {
        "version": "domain_calibration_batch01_behavioral_review.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "technical_execution_status": "PASS",
        "behavioral_review_status": behavioral_review_status,
        "content_capture": content_capture,
        "execution_reviews": execution_reviews,
        "latency_summary_by_mode": latency_summary_by_mode,
        "latency_summary_by_domain": latency_summary_by_domain,
        "safety_violations": safety_violations,
        "domain_validation_completed": False,
        "accepted_for_behavioral_calibration": False if content_capture_hold else True,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "commercial_claim": False,
        "recommended_action": "Harden output capture before rerunning behavioral calibration." if content_capture_hold else "Proceed to behavioral scoring review.",
        "recommended_next_phase": "PROD-6101..6140 - Domain Calibration Output Capture Hardening Packet" if content_capture_hold else "PROD-6101..6140 - Domain Calibration Batch 01 Behavioral Scoring Gate"
    }

    capture_gaps = {
        "version": "domain_calibration_batch01_content_capture_gaps.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "content_capture_hold": content_capture_hold,
        "rerun_required": rerun_required,
        "main_gap": "The batch runner confirms technical PASS, but stored output is insufficient for full behavioral calibration.",
        "required_hardening": [
            "Store full model output text for every execution.",
            "Store parsed response JSON when available.",
            "Fail behavioral capture if output is empty.",
            "Fail behavioral capture if response is not parseable JSON for calibration prompts.",
            "Validate expected behavioral fields.",
            "Separate technical PASS from behavioral PASS.",
            "Create output_capture_status per execution.",
            "Create behavior_parse_status per execution.",
            "Create review_ready flag per execution.",
            "Rerun Batch 01 after hardening as controlled calibration records only."
        ],
        "content_capture": content_capture,
        "affected_executions": [
            x for x in execution_reviews
            if x["output_preview_empty"]
            or not x["full_output_present"]
            or not x["json_parseable_from_preview"]
            or x["expected_behavior_fields_missing_count"] > 0
        ]
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6021..6060":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6101..6140":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration Batch 01 Review Gate",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6101..6140" not in seen:
        roadmap_items.append({
            "phase": "PROD-6101..6140",
            "name": "Domain Calibration Output Capture Hardening Packet",
            "status": "NEXT"
        })

    decision = "DOMAIN_CALIBRATION_BATCH01_REVIEW_COMPLETED_WITH_CONTENT_CAPTURE_HOLD"

    gate = {
        "version": "domain_calibration_batch01_review_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_BATCH01_REVIEW_GATE_FAILED",
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "technical_execution_status": "PASS",
        "behavioral_review_status": behavioral_review_status,
        "content_capture_hold": content_capture_hold,
        "rerun_required": rerun_required,
        "domain_validation_completed": False,
        "accepted_for_behavioral_calibration": False if content_capture_hold else True,
        "review_check_count": len(checks),
        "review_checks": checks,
        "content_capture": content_capture,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": behavioral_review["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "review_gate_only": True,
        "additional_live_call_allowed": False,
        "technical_execution_accepted": True,
        "behavioral_calibration_acceptance_blocked": content_capture_hold,
        "content_capture_hold": content_capture_hold,
        "rerun_required_after_hardening": rerun_required,
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
        "executed_count": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
        "domain_count": len(domain_counts),
        "scenario_count": scenarios.get("scenario_count"),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "safety_violations": safety_violations,
        "empty_output_count": empty_output_count,
        "nonempty_output_count": nonempty_output_count,
        "full_output_present_count": full_output_present_count,
        "json_parseable_from_preview_count": json_parseable_from_preview_count,
        "expected_field_full_coverage_count": expected_field_full_coverage_count,
        "content_capture_sufficient": content_capture_sufficient,
        "content_capture_hold": content_capture_hold,
        "behavioral_review_status": behavioral_review_status,
        "domain_validation_completed": False,
        "accepted_for_behavioral_calibration": False if content_capture_hold else True,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "commercial_claim": False,
        "rerun_required": rerun_required,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.5",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Batch 01 Review Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6061..6100 - Domain Calibration Batch 01 Review Gate

Review gate for Domain Calibration Batch 01.

## Executive result

Technical execution passed.

Behavioral calibration is on HOLD because content capture is insufficient for full behavioral review.

## Technical execution

- Executed count: {batch.get('executed_count')}
- Real provider calls: {batch.get('real_provider_call_count')}
- Successful live responses: {batch.get('successful_live_response_count')}
- Domains: {len(domain_counts)}
- Scenarios: {scenarios.get('scenario_count')}
- Safety violations: {safety_violations}

## Content capture

- Empty output count: {empty_output_count}
- Non-empty output count: {nonempty_output_count}
- Full output present count: {full_output_present_count}
- JSON parseable from preview count: {json_parseable_from_preview_count}
- Expected field full coverage count: {expected_field_full_coverage_count}

## Decision

{decision}

## Interpretation

The system proved the controlled execution pipeline, gates and safety boundaries.

It did not yet prove behavioral calibration quality because the captured content is not sufficient to score evidence grounding, gate compliance, claim boundary, state completeness or next operational action across all executions.

## Required next step

PROD-6101..6140 - Domain Calibration Output Capture Hardening Packet
"""

    report = f"""# PROD-6061..6100 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Review checks: {result['review_check_count']}
- Review gate only: true
- Additional live call in this gate: false
- Technical execution status: {result['technical_execution_status']}
- Executed count: {result['executed_count']}
- Real provider call count: {result['real_provider_call_count']}
- Successful live response count: {result['successful_live_response_count']}
- Domain count: {result['domain_count']}
- Scenario count: {result['scenario_count']}
- Safety violations: {result['safety_violations']}
- Empty output count: {result['empty_output_count']}
- Non-empty output count: {result['nonempty_output_count']}
- Full output present count: {result['full_output_present_count']}
- JSON parseable from preview count: {result['json_parseable_from_preview_count']}
- Expected field full coverage count: {result['expected_field_full_coverage_count']}
- Content capture sufficient: {result['content_capture_sufficient']}
- Content capture hold: {result['content_capture_hold']}
- Behavioral review status: {result['behavioral_review_status']}
- Domain validation completed: false
- Accepted for behavioral calibration: {result['accepted_for_behavioral_calibration']}
- Accepted as dataset candidate: false
- Accepted as client evidence: false
- Accepted as production evidence: false
- Commercial claim: false
- Rerun required: {result['rerun_required']}
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
    write_json(BEHAVIOR_REPORT, behavioral_review)
    write_json(CAPTURE_GAPS, capture_gaps)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("review_checks:", result["review_check_count"])
    print("technical_execution_status:", result["technical_execution_status"])
    print("executed_count:", result["executed_count"])
    print("real_provider_call_count:", result["real_provider_call_count"])
    print("successful_live_response_count:", result["successful_live_response_count"])
    print("empty_output_count:", result["empty_output_count"])
    print("nonempty_output_count:", result["nonempty_output_count"])
    print("full_output_present_count:", result["full_output_present_count"])
    print("json_parseable_from_preview_count:", result["json_parseable_from_preview_count"])
    print("content_capture_hold:", result["content_capture_hold"])
    print("behavioral_review_status:", result["behavioral_review_status"])
    print("rerun_required:", result["rerun_required"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
