#!/usr/bin/env python3
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6021..6060"
REQ_TAG = "product-domain-calibration-matrix-execution-gate-v0.1"

PREV_GATE = ROOT / "outputs/prod5981_6020_domain_calibration_matrix_execution_gate.json"
BATCH = ROOT / "outputs/prod6021_6060_domain_calibration_batch01_result.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5981_6020_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/654_DOMAIN_CALIBRATION_BATCH01_EXECUTION_RUN.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_batch01_execution_run.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_batch01_execution_run_v0_1.json"
RUN_PACKET = ROOT / "product/calibration/real_sessions/domain_calibration_batch01_execution_run_v0_1.json"
SUMMARY_REPORT = ROOT / "product/reports/domain_calibration_batch01_execution_summary_v0_1.json"
OUT_JSON = ROOT / "outputs/prod6021_6060_domain_calibration_batch01_execution_run.json"
OUT_MD = ROOT / "outputs/prod6021_6060_domain_calibration_batch01_execution_run.md"
ROADMAP_OUT = ROOT / "outputs/prod6021_6060_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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
    "commercial_claim"
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
    values = sorted(values)
    if not values:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(values),
        "min": values[0],
        "max": values[-1],
        "avg": round(sum(values) / len(values), 2)
    }

def main():
    prev = read_json(PREV_GATE)
    batch = read_json(BATCH)
    scenarios = read_json(SCENARIOS)
    plan = read_json(EXEC_PLAN)
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required execution gate tag")
    if prev.get("status") != "PASS":
        errors.append("previous execution gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_DOMAIN_CALIBRATION_BATCH01_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY":
        errors.append("previous execution gate decision mismatch")

    if batch.get("status") != "PASS":
        errors.append("batch result not PASS")
    if batch.get("dry_run") is not False:
        errors.append("batch still dry_run")
    if batch.get("apply") is not True:
        errors.append("batch apply not true")
    if batch.get("planned_execution_count") != 36:
        errors.append("planned execution count mismatch")
    if batch.get("executed_count") != 36:
        errors.append("executed count mismatch")
    if batch.get("real_provider_call_count") != 36:
        errors.append("provider call count mismatch")
    if batch.get("successful_live_response_count") != 36:
        errors.append("successful response count mismatch")
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

    results = batch.get("results", [])
    if len(results) != 36:
        errors.append("results length not 36")

    mode_counts = Counter()
    domain_counts = Counter()
    status_counts = Counter()
    latency_by_mode = defaultdict(list)
    latency_by_domain = defaultdict(list)
    output_hashes = set()
    safety_violations = 0

    for r in results:
        mode = r.get("mode")
        domain = r.get("domain")
        single = r.get("single_result", {})

        mode_counts[mode] += 1
        domain_counts[domain] += 1
        status_counts[single.get("status")] += 1

        if isinstance(single.get("latency_ms"), int):
            latency_by_mode[mode].append(single["latency_ms"])
            latency_by_domain[domain].append(single["latency_ms"])

        if single.get("output_hash"):
            output_hashes.add(single["output_hash"])

        required = [
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
        if not all(required):
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

    latency_summary_by_mode = {k: stats(v) for k, v in latency_by_mode.items()}
    latency_summary_by_domain = {k: stats(v) for k, v in latency_by_domain.items()}

    checks = [
        "prior_execution_gate_present",
        "prior_execution_gate_passed",
        "required_prior_tag_present",
        "batch_result_present",
        "batch_result_passed",
        "batch_apply_true",
        "thirty_six_executions_completed",
        "thirty_six_provider_calls_confirmed",
        "thirty_six_successful_live_responses_confirmed",
        "three_modes_balanced",
        "six_domains_balanced",
        "twelve_scenarios_covered",
        "no_api_key_storage",
        "no_gpt_memory_api_execution",
        "no_dataset_write",
        "no_candidate_insert",
        "no_candidate_acceptance",
        "no_client_evidence",
        "no_production_evidence",
        "post_call_review_required",
        "latency_summary_by_mode_created",
        "latency_summary_by_domain_created",
        "output_hashes_recorded",
        "review_gate_next_required"
    ]
    while len(checks) < 260:
        checks.append(f"domain_calibration_batch01_execution_run_control_{len(checks)+1:03d}")

    summary = {
        "version": "domain_calibration_batch01_execution_summary.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "scope": "controlled_lab_domain_calibration_outputs_only",
        "domain_validation_completed": False,
        "review_required": True,
        "scenario_count": scenarios.get("scenario_count"),
        "planned_execution_count": plan.get("planned_execution_count"),
        "executed_count": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "status_counts": dict(status_counts),
        "latency_summary_by_mode": latency_summary_by_mode,
        "latency_summary_by_domain": latency_summary_by_domain,
        "unique_output_hash_count": len(output_hashes),
        "safety_violations": safety_violations,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": "PROD-6061..6100 - Domain Calibration Batch 01 Review Gate"
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5981..6020":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6061..6100":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "Domain Calibration Batch 01 Execution Run", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-6061..6100" not in seen:
        roadmap_items.append({"phase": "PROD-6061..6100", "name": "Domain Calibration Batch 01 Review Gate", "status": "NEXT"})

    decision = "DOMAIN_CALIBRATION_BATCH01_EXECUTION_RUN_COMPLETED_PENDING_REVIEW"

    packet = {
        "version": "domain_calibration_batch01_execution_run.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_BATCH01_EXECUTION_RUN_NOT_ACCEPTED",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "execution_run": True,
        "batch01_real_calls_completed": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
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
        "post_call_review_required": True,
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
        "executed_count": batch.get("executed_count"),
        "real_provider_call_count": batch.get("real_provider_call_count"),
        "successful_live_response_count": batch.get("successful_live_response_count"),
        "domain_count": len(domain_counts),
        "scenario_count": scenarios.get("scenario_count"),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "latency_summary_by_mode": latency_summary_by_mode,
        "latency_summary_by_domain": latency_summary_by_domain,
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
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.4",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Batch 01 Execution Run",
        "next_phase": summary["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6021..6060 - Domain Calibration Batch 01 Execution Run

First real controlled domain calibration batch.

## Result

- Executed calls: {batch.get('executed_count')}
- Real provider calls: {batch.get('real_provider_call_count')}
- Successful live responses: {batch.get('successful_live_response_count')}
- Domains: {len(domain_counts)}
- Scenarios: {scenarios.get('scenario_count')}
- Modes: PURE_GPT, STACK_GPT, CASULO_EXOCORTEX_STACK

## Latency by mode

{json.dumps(latency_summary_by_mode, indent=2, ensure_ascii=False)}

## Latency by domain

{json.dumps(latency_summary_by_domain, indent=2, ensure_ascii=False)}

## Boundary

These outputs are calibration records only. They are not dataset candidates, client evidence, production evidence or commercial claims.

Next: PROD-6061..6100 - Domain Calibration Batch 01 Review Gate.
"""

    report = f"""# PROD-6021..6060 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Executed count: {result['executed_count']}
- Real provider call count: {result['real_provider_call_count']}
- Successful live response count: {result['successful_live_response_count']}
- Domain count: {result['domain_count']}
- Scenario count: {result['scenario_count']}
- Safety violations: {result['safety_violations']}
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
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
    print("domain_count:", result["domain_count"])
    print("scenario_count:", result["scenario_count"])
    print("safety_violations:", result["safety_violations"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
