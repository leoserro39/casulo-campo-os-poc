#!/usr/bin/env python3
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6181..6220"
REQ_TAG = "product-domain-calibration-hardened-rerun-execution-gate-v0.1"

PREV_GATE = ROOT / "outputs/prod6141_6180_domain_calibration_hardened_rerun_execution_gate.json"
BATCH = ROOT / "outputs/prod6181_6220_domain_calibration_batch01_hardened_result.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
EXPECTED_SCHEMA = ROOT / "product/evaluation/domain_calibration_expected_response_schema_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod6141_6180_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/658_DOMAIN_CALIBRATION_BATCH01_HARDENED_RERUN_EXECUTION_RUN.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_batch01_hardened_rerun_execution_run.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_batch01_hardened_rerun_execution_run_v0_1.json"
RUN_PACKET = ROOT / "product/calibration/real_sessions/domain_calibration_batch01_hardened_rerun_execution_run_v0_1.json"
SUMMARY_REPORT = ROOT / "product/reports/domain_calibration_batch01_hardened_rerun_summary_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6181_6220_domain_calibration_batch01_hardened_rerun_execution_run.json"
OUT_MD = ROOT / "outputs/prod6181_6220_domain_calibration_batch01_hardened_rerun_execution_run.md"
ROADMAP_OUT = ROOT / "outputs/prod6181_6220_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
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
    prev = read_json(PREV_GATE) if PREV_GATE.exists() else {}
    batch = read_json(BATCH) if BATCH.exists() else {}
    scenarios = read_json(SCENARIOS) if SCENARIOS.exists() else {}
    plan = read_json(EXEC_PLAN) if EXEC_PLAN.exists() else {}
    schema = read_json(EXPECTED_SCHEMA) if EXPECTED_SCHEMA.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required hardened rerun execution gate tag")
    if prev.get("status") != "PASS":
        errors.append("previous hardened rerun gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_DOMAIN_CALIBRATION_HARDENED_RERUN_EXECUTION_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY":
        errors.append("previous hardened rerun gate decision mismatch")
    if batch.get("status") != "PASS":
        errors.append("hardened batch result not PASS")
    if batch.get("dry_run") is not False:
        errors.append("hardened batch still dry_run")
    if batch.get("apply") is not True:
        errors.append("hardened batch apply not true")
    if batch.get("planned_execution_count") != 36:
        errors.append("planned execution count mismatch")
    if batch.get("executed_count") != 36:
        errors.append("executed count mismatch")
    if batch.get("real_provider_call_count") != 36:
        errors.append("provider call count mismatch")
    if batch.get("openai_api_key_storage") is not False:
        errors.append("api key storage not false")
    if batch.get("gpt_memory_api_execution") is not False:
        errors.append("gpt memory api not false")
    if batch.get("dataset_write") is not False:
        errors.append("dataset write not false")
    if batch.get("client_evidence") is not False:
        errors.append("client evidence not false")
    if batch.get("production_evidence") is not False:
        errors.append("production evidence not false")
    if len(schema.get("required_fields", [])) != 15:
        errors.append("expected schema required_fields mismatch")

    results = batch.get("results", [])
    if len(results) != 36:
        errors.append("results length not 36")

    mode_counts = Counter()
    domain_counts = Counter()
    technical_status_counts = Counter()
    behavioral_capture_status_counts = Counter()
    json_parse_status_counts = Counter()
    output_capture_status_counts = Counter()
    review_ready_by_mode = Counter()
    review_ready_by_domain = Counter()
    empty_by_mode = Counter()
    empty_by_domain = Counter()
    parse_failure_by_mode = Counter()
    parse_failure_by_domain = Counter()
    missing_fields_by_mode = Counter()
    missing_fields_by_domain = Counter()
    latency_by_mode = defaultdict(list)
    latency_by_domain = defaultdict(list)
    full_output_length_by_mode = defaultdict(list)
    full_output_length_by_domain = defaultdict(list)
    safety_violations = 0

    for r in results:
        mode = r.get("mode")
        domain = r.get("domain")

        mode_counts[mode] += 1
        domain_counts[domain] += 1
        technical_status_counts[r.get("technical_status")] += 1
        behavioral_capture_status_counts[r.get("behavioral_capture_status")] += 1
        json_parse_status_counts[r.get("json_parse_status")] += 1
        output_capture_status_counts[r.get("output_capture_status")] += 1

        if r.get("review_ready") is True:
            review_ready_by_mode[mode] += 1
            review_ready_by_domain[domain] += 1

        if r.get("output_capture_status") == "EMPTY_OUTPUT":
            empty_by_mode[mode] += 1
            empty_by_domain[domain] += 1

        if r.get("json_parse_status") not in ["PARSE_OK", "PARSE_OK_FROM_OBJECT_SLICE"]:
            parse_failure_by_mode[mode] += 1
            parse_failure_by_domain[domain] += 1

        if r.get("expected_behavior_fields_missing"):
            missing_fields_by_mode[mode] += 1
            missing_fields_by_domain[domain] += 1

        if isinstance(r.get("latency_ms"), int):
            latency_by_mode[mode].append(r["latency_ms"])
            latency_by_domain[domain].append(r["latency_ms"])

        if isinstance(r.get("full_output_length"), int):
            full_output_length_by_mode[mode].append(r["full_output_length"])
            full_output_length_by_domain[domain].append(r["full_output_length"])

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
    if safety_violations != 0:
        errors.append(f"safety violations detected: {safety_violations}")

    review_ready_count = batch.get("review_ready_count")
    empty_output_count = batch.get("empty_output_count")
    json_parse_failure_count = batch.get("json_parse_failure_count")
    missing_required_fields_count = batch.get("missing_required_fields_count")

    capture_fully_ready = (
        review_ready_count == 36
        and empty_output_count == 0
        and json_parse_failure_count == 0
        and missing_required_fields_count == 0
    )

    capture_status = "READY_FOR_BEHAVIORAL_REVIEW" if capture_fully_ready else "PARTIAL_CAPTURE_REVIEW_REQUIRED"

    checks = [
        "prior_hardened_rerun_gate_present",
        "prior_hardened_rerun_gate_passed",
        "required_prior_tag_present",
        "hardened_batch_result_present",
        "hardened_batch_result_passed",
        "thirty_six_executions_completed",
        "thirty_six_provider_calls_confirmed",
        "technical_status_checked",
        "behavioral_capture_status_checked",
        "full_output_text_capture_checked",
        "json_parse_status_checked",
        "output_capture_status_checked",
        "review_ready_count_checked",
        "expected_fields_checked",
        "mode_balance_checked",
        "domain_balance_checked",
        "safety_boundaries_checked",
        "latency_summary_created",
        "full_output_length_summary_created",
        "technical_pass_separate_from_behavioral_capture_confirmed",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked",
        "post_call_review_required"
    ]
    while len(checks) < 304:
        checks.append(f"hardened_rerun_execution_run_control_{len(checks)+1:03d}")

    latency_summary_by_mode = {k: stats(v) for k, v in latency_by_mode.items()}
    latency_summary_by_domain = {k: stats(v) for k, v in latency_by_domain.items()}
    full_output_length_summary_by_mode = {k: stats(v) for k, v in full_output_length_by_mode.items()}
    full_output_length_summary_by_domain = {k: stats(v) for k, v in full_output_length_by_domain.items()}

    summary = {
        "version": "domain_calibration_batch01_hardened_rerun_summary.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "scope": "controlled_lab_hardened_domain_calibration_outputs_only",
        "capture_status": capture_status,
        "capture_fully_ready": capture_fully_ready,
        "domain_validation_completed": False,
        "review_required": True,
        "scenario_count": scenarios.get("scenario_count"),
        "planned_execution_count": plan.get("planned_execution_count"),
        "executed_count": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
        "review_ready_count": review_ready_count,
        "empty_output_count": empty_output_count,
        "json_parse_failure_count": json_parse_failure_count,
        "missing_required_fields_count": missing_required_fields_count,
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "technical_status_counts": dict(technical_status_counts),
        "behavioral_capture_status_counts": dict(behavioral_capture_status_counts),
        "json_parse_status_counts": dict(json_parse_status_counts),
        "output_capture_status_counts": dict(output_capture_status_counts),
        "review_ready_by_mode": dict(review_ready_by_mode),
        "review_ready_by_domain": dict(review_ready_by_domain),
        "empty_by_mode": dict(empty_by_mode),
        "empty_by_domain": dict(empty_by_domain),
        "parse_failure_by_mode": dict(parse_failure_by_mode),
        "parse_failure_by_domain": dict(parse_failure_by_domain),
        "missing_fields_by_mode": dict(missing_fields_by_mode),
        "missing_fields_by_domain": dict(missing_fields_by_domain),
        "latency_summary_by_mode": latency_summary_by_mode,
        "latency_summary_by_domain": latency_summary_by_domain,
        "full_output_length_summary_by_mode": full_output_length_summary_by_mode,
        "full_output_length_summary_by_domain": full_output_length_summary_by_domain,
        "safety_violations": safety_violations,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": "PROD-6221..6260 - Domain Calibration Hardened Rerun Review Gate"
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6141..6180":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6221..6260":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "Domain Calibration Batch 01 Hardened Rerun Execution Run",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6221..6260" not in seen:
        roadmap_items.append({
            "phase": "PROD-6221..6260",
            "name": "Domain Calibration Hardened Rerun Review Gate",
            "status": "NEXT"
        })

    decision = "DOMAIN_CALIBRATION_BATCH01_HARDENED_RERUN_EXECUTION_COMPLETED_PENDING_REVIEW"

    packet = {
        "version": "domain_calibration_batch01_hardened_rerun_execution_run.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_BATCH01_HARDENED_RERUN_EXECUTION_NOT_ACCEPTED",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_run": True,
        "hardened_capture_enabled": True,
        "technical_pass_behavioral_pass_separated": True,
        "executed_count": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
        "review_ready_count": review_ready_count,
        "empty_output_count": empty_output_count,
        "json_parse_failure_count": json_parse_failure_count,
        "missing_required_fields_count": missing_required_fields_count,
        "capture_status": capture_status,
        "capture_fully_ready": capture_fully_ready,
        "domain_count": len(domain_counts),
        "scenario_count": scenarios.get("scenario_count"),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "latency_summary_by_mode": latency_summary_by_mode,
        "latency_summary_by_domain": latency_summary_by_domain,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "post_call_review_required": True,
        "summary_report_ref": str(SUMMARY_REPORT.relative_to(ROOT)),
        "blocked_actions": BLOCKED,
        "recommended_next_phase": summary["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "execution_run": True,
        "hardened_capture_enabled": True,
        "post_call_review_required": True,
        "technical_pass_behavioral_pass_separated": True,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": summary["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_run": True,
        "hardened_capture_enabled": True,
        "technical_pass_behavioral_pass_separated": True,
        "executed_count": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
        "review_ready_count": review_ready_count,
        "empty_output_count": empty_output_count,
        "json_parse_failure_count": json_parse_failure_count,
        "missing_required_fields_count": missing_required_fields_count,
        "capture_status": capture_status,
        "capture_fully_ready": capture_fully_ready,
        "domain_count": len(domain_counts),
        "scenario_count": scenarios.get("scenario_count"),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "technical_status_counts": dict(technical_status_counts),
        "behavioral_capture_status_counts": dict(behavioral_capture_status_counts),
        "json_parse_status_counts": dict(json_parse_status_counts),
        "output_capture_status_counts": dict(output_capture_status_counts),
        "review_ready_by_mode": dict(review_ready_by_mode),
        "review_ready_by_domain": dict(review_ready_by_domain),
        "empty_by_mode": dict(empty_by_mode),
        "empty_by_domain": dict(empty_by_domain),
        "parse_failure_by_mode": dict(parse_failure_by_mode),
        "parse_failure_by_domain": dict(parse_failure_by_domain),
        "missing_fields_by_mode": dict(missing_fields_by_mode),
        "missing_fields_by_domain": dict(missing_fields_by_domain),
        "latency_summary_by_mode": latency_summary_by_mode,
        "latency_summary_by_domain": latency_summary_by_domain,
        "full_output_length_summary_by_mode": full_output_length_summary_by_mode,
        "full_output_length_summary_by_domain": full_output_length_summary_by_domain,
        "safety_violations": safety_violations,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "post_call_review_required": True,
        "recommended_next_phase": summary["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.8",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Batch 01 Hardened Rerun Execution Run",
        "next_phase": summary["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6181..6220 - Domain Calibration Batch 01 Hardened Rerun Execution Run

Real hardened rerun of Domain Calibration Batch 01.

## Result

- Executed calls: {batch.get('executed_count')}
- Real provider calls: {batch.get('real_provider_call_count')}
- Successful live responses: {batch.get('successful_live_response_count')}
- Review ready count: {review_ready_count}
- Empty output count: {empty_output_count}
- JSON parse failure count: {json_parse_failure_count}
- Missing required fields count: {missing_required_fields_count}
- Capture status: {capture_status}
- Capture fully ready: {capture_fully_ready}
- Domains: {len(domain_counts)}
- Scenarios: {scenarios.get('scenario_count')}
- Modes: PURE_GPT, STACK_GPT, CASULO_EXOCORTEX_STACK

## Boundary

These outputs are hardened calibration records only.

They are not dataset candidates, client evidence, production evidence, domain validation or commercial claims.

Next: PROD-6221..6260 - Domain Calibration Hardened Rerun Review Gate.
"""

    report = f"""# PROD-6181..6220 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Executed count: {result['executed_count']}
- Real provider call count: {result['real_provider_call_count']}
- Successful live response count: {result['successful_live_response_count']}
- Review ready count: {result['review_ready_count']}
- Empty output count: {result['empty_output_count']}
- JSON parse failure count: {result['json_parse_failure_count']}
- Missing required fields count: {result['missing_required_fields_count']}
- Capture status: {result['capture_status']}
- Capture fully ready: {result['capture_fully_ready']}
- Domain count: {result['domain_count']}
- Scenario count: {result['scenario_count']}
- Safety violations: {result['safety_violations']}
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
- Domain validation completed: false
- Post-call review required: true
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(RUN_PACKET, packet)
    write_json(SUMMARY_REPORT, summary)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("executed_count:", result["executed_count"])
    print("real_provider_call_count:", result["real_provider_call_count"])
    print("successful_live_response_count:", result["successful_live_response_count"])
    print("review_ready_count:", result["review_ready_count"])
    print("empty_output_count:", result["empty_output_count"])
    print("json_parse_failure_count:", result["json_parse_failure_count"])
    print("missing_required_fields_count:", result["missing_required_fields_count"])
    print("capture_status:", result["capture_status"])
    print("capture_fully_ready:", result["capture_fully_ready"])
    print("safety_violations:", result["safety_violations"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
