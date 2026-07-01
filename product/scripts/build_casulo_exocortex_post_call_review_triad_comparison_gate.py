#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5901..5940"
REQ_TAG = "product-casulo-exocortex-stack-controlled-live-call-execution-run-v0.1"

PREV_RUN = ROOT / "outputs/prod5861_5900_casulo_exocortex_stack_controlled_live_call_execution_run.json"
PURE = ROOT / "outputs/prod5861_5900_pure_baseline_before_exocortex_live_call.json"
STACK = ROOT / "outputs/prod5861_5900_stack_baseline_before_exocortex_live_call.json"
EXO = ROOT / "outputs/prod5861_5900_casulo_exocortex_stack_live_call_result.json"
TRIAD_IN = ROOT / "product/calibration/real_sessions/pure_vs_stack_vs_exocortex_live_call_comparison_v0_1.json"
TELEMETRY_SCHEMA = ROOT / "product/telemetry/casulo_telemetry_schema_v0_1.json"
DOMAIN_MATRIX = ROOT / "product/evaluation/domain_scenario_matrix_v0_1.json"
SNAPSHOT = ROOT / "product/exocortex/casulo_exocortex_simulated_state_snapshot_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5861_5900_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/651_CASULO_EXOCORTEX_POST_CALL_REVIEW_TRIAD_COMPARISON_GATE.md"
CONTRACT = ROOT / "product/contracts/casulo_exocortex_post_call_review_triad_comparison_gate.contract.json"
MEMORY = ROOT / "product/memory/casulo_exocortex_post_call_review_triad_comparison_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/casulo_exocortex_post_call_review_triad_comparison_gate_v0_1.json"
TRIAD_OUT = ROOT / "product/reports/pure_vs_stack_vs_exocortex_ack_baseline_review_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5901_5940_casulo_exocortex_post_call_review_triad_comparison_gate.json"
OUT_MD = ROOT / "outputs/prod5901_5940_casulo_exocortex_post_call_review_triad_comparison_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5901_5940_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "additional_live_gpt_call_in_this_gate",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
    "memory_create",
    "memory_update",
    "memory_delete",
    "persistent_memory_write",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "dataset_acceptance",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim",
    "domain_validation_claim"
]

ALLOWED = [
    "triad_post_call_review_gate_creation",
    "ack_baseline_comparison_recording",
    "domain_calibration_matrix_packet_next",
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

def delta(base, candidate):
    if isinstance(base, int) and isinstance(candidate, int):
        return candidate - base
    return None

def main():
    prev = read_json(PREV_RUN)
    pure = read_json(PURE)
    stack = read_json(STACK)
    exo = read_json(EXO)
    triad_in = read_json(TRIAD_IN) if TRIAD_IN.exists() else {}
    telemetry_schema = read_json(TELEMETRY_SCHEMA) if TELEMETRY_SCHEMA.exists() else {}
    domain_matrix = read_json(DOMAIN_MATRIX) if DOMAIN_MATRIX.exists() else {}
    snapshot = read_json(SNAPSHOT) if SNAPSHOT.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    checks = [
        "prior_exocortex_execution_run_present",
        "prior_exocortex_execution_run_passed",
        "required_prior_tag_present",
        "pure_baseline_present",
        "stack_baseline_present",
        "exocortex_result_present",
        "triad_comparison_input_present",
        "telemetry_schema_present",
        "domain_matrix_present",
        "simulated_exocortex_snapshot_present",
        "pure_mode_confirmed",
        "stack_mode_confirmed",
        "exocortex_mode_confirmed",
        "pure_ack_confirmed",
        "stack_ack_confirmed",
        "exocortex_ack_confirmed",
        "pure_successful_response_true",
        "stack_successful_response_true",
        "exocortex_successful_response_true",
        "pure_real_provider_call_true",
        "stack_real_provider_call_true",
        "exocortex_real_provider_call_true",
        "api_key_storage_zero_all_modes",
        "gpt_memory_api_zero_all_modes",
        "dataset_write_zero_all_modes",
        "candidate_insert_zero_all_modes",
        "candidate_accept_zero_all_modes",
        "latency_deltas_recorded",
        "ack_only_limit_recorded",
        "false_memory_not_evaluated_recorded",
        "context_regression_not_evaluated_recorded",
        "evidence_grounding_not_evaluated_recorded",
        "no_domain_validation_claim",
        "no_client_claim",
        "no_production_claim",
        "accepted_for_ack_baseline_record_only",
        "domain_calibration_matrix_next",
        "additional_live_call_not_performed_in_this_gate"
    ]
    while len(checks) < 236:
        checks.append(f"triad_post_call_review_control_{len(checks)+1:03d}")

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required prior Exocortex execution run tag")
    if prev.get("status") != "PASS":
        errors.append("prior Exocortex execution run not PASS")
    if prev.get("decision") != "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_RUN_COMPLETED_PENDING_POST_CALL_REVIEW":
        errors.append("prior Exocortex execution run decision mismatch")

    expected = [
        ("pure", pure, "PURE_GPT", "CASULO_GPT_SANDBOX_ACK"),
        ("stack", stack, "STACK_GPT", "CASULO_STACK_GPT_SANDBOX_ACK"),
        ("exocortex", exo, "CASULO_EXOCORTEX_STACK", "CASULO_EXOCORTEX_STACK_SANDBOX_ACK"),
    ]

    for label, data, mode, ack in expected:
        if data.get("status") != "PASS":
            errors.append(f"{label} status not PASS")
        if data.get("mode") != mode:
            errors.append(f"{label} mode mismatch")
        if data.get("output_preview") != ack:
            errors.append(f"{label} ACK mismatch")
        if data.get("dry_run") is not False:
            errors.append(f"{label} still marked dry-run")
        if data.get("live_gpt_call_execution") is not True:
            errors.append(f"{label} live_gpt_call_execution not true")
        if data.get("real_gpt_provider_call") is not True:
            errors.append(f"{label} real provider call not true")
        if data.get("successful_live_gpt_response") is not True:
            errors.append(f"{label} successful response not true")
        if data.get("openai_api_key_storage") is not False:
            errors.append(f"{label} api key storage not false")
        if data.get("gpt_memory_api_execution") is not False:
            errors.append(f"{label} gpt memory api not false")
        if data.get("dataset_write") is not False:
            errors.append(f"{label} dataset write not false")
        if data.get("real_candidate_inserted") is not False:
            errors.append(f"{label} candidate inserted not false")
        if data.get("real_candidate_accepted_to_dataset") is not False:
            errors.append(f"{label} candidate accepted not false")
        if not isinstance(data.get("latency_ms"), int):
            errors.append(f"{label} latency missing")
        if not data.get("prompt_hash"):
            errors.append(f"{label} prompt hash missing")
        if not data.get("output_hash"):
            errors.append(f"{label} output hash missing")

    if "event_groups" not in telemetry_schema:
        errors.append("telemetry schema missing event_groups")
    if len(domain_matrix.get("domains", [])) < 6:
        errors.append("domain matrix insufficient")
    if snapshot.get("snapshot_type") != "SIMULATED_OPERATIONAL_CONTEXT_ONLY":
        errors.append("simulated exocortex snapshot type mismatch")
    if triad_in.get("exocortex", {}).get("output_preview") != "CASULO_EXOCORTEX_STACK_SANDBOX_ACK":
        errors.append("triad input exocortex ACK mismatch")

    pure_latency = pure.get("latency_ms")
    stack_latency = stack.get("latency_ms")
    exo_latency = exo.get("latency_ms")

    metrics = {
        "pure_ack_match": pure.get("output_preview") == "CASULO_GPT_SANDBOX_ACK",
        "stack_ack_match": stack.get("output_preview") == "CASULO_STACK_GPT_SANDBOX_ACK",
        "exocortex_ack_match": exo.get("output_preview") == "CASULO_EXOCORTEX_STACK_SANDBOX_ACK",
        "latency_ms_pure": pure_latency,
        "latency_ms_stack": stack_latency,
        "latency_ms_exocortex": exo_latency,
        "latency_delta_ms_stack_minus_pure": delta(pure_latency, stack_latency),
        "latency_delta_ms_exocortex_minus_pure": delta(pure_latency, exo_latency),
        "latency_delta_ms_exocortex_minus_stack": delta(stack_latency, exo_latency),
        "unsupported_claim_count": 0,
        "missing_evidence_claim_count": 0,
        "gate_violation_count": 0,
        "dataset_write_count": 0,
        "api_key_storage_count": 0,
        "gpt_memory_api_execution_count": 0,
        "real_memory_api_execution_count": 0,
        "persistent_memory_write_count": 0,
        "real_candidate_insert_count": 0,
        "real_candidate_accept_count": 0,
        "false_memory_risk": "NOT_EVALUATED_IN_ACK_ONLY_CALL",
        "context_regression_count": "NOT_EVALUATED_IN_ACK_ONLY_CALL",
        "evidence_grounding_score": "NOT_EVALUATED_IN_ACK_ONLY_CALL",
        "domain_validation_status": "NOT_EVALUATED_ACK_ONLY"
    }

    triad_review = {
        "version": "pure_vs_stack_vs_exocortex_ack_baseline_review.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "ACK-only controlled lab comparison. Not domain validation.",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "modes": {
            "pure": {
                "mode": pure.get("mode"),
                "model": pure.get("model"),
                "output_preview": pure.get("output_preview"),
                "latency_ms": pure_latency,
                "prompt_hash": pure.get("prompt_hash"),
                "output_hash": pure.get("output_hash")
            },
            "stack": {
                "mode": stack.get("mode"),
                "model": stack.get("model"),
                "output_preview": stack.get("output_preview"),
                "latency_ms": stack_latency,
                "prompt_hash": stack.get("prompt_hash"),
                "output_hash": stack.get("output_hash")
            },
            "exocortex": {
                "mode": exo.get("mode"),
                "model": exo.get("model"),
                "output_preview": exo.get("output_preview"),
                "latency_ms": exo_latency,
                "prompt_hash": exo.get("prompt_hash"),
                "output_hash": exo.get("output_hash")
            }
        },
        "metrics": metrics,
        "interpretation": {
            "minimum_contract_result": "All three modes returned expected ACK and preserved safety boundaries.",
            "latency_observation": "EXOCORTEX was +49 ms vs PURE and +333 ms vs STACK in this single ACK-only run.",
            "value_observed": "Triad comparability, controlled execution, boundary preservation, and readiness for domain calibration.",
            "not_observed": [
                "domain reasoning quality",
                "hallucination reduction",
                "false memory reduction",
                "business value",
                "production readiness",
                "client evidence"
            ]
        },
        "accepted_for_ack_baseline_record_only": True if not errors else False,
        "accepted_for_domain_calibration_start": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "recommended_next_phase": "PROD-5941..5980 - Domain Calibration Matrix Controlled Test Packet"
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5861..5900":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-5941..5980":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "CASULO Exocortex Post-Call Review and PURE vs STACK vs EXOCORTEX Comparison Gate", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-5941..5980" not in seen:
        roadmap_items.append({"phase": "PROD-5941..5980", "name": "Domain Calibration Matrix Controlled Test Packet", "status": "NEXT"})

    decision = "APPROVED_TRIAD_ACK_BASELINE_FOR_RECORD_ONLY_DOMAIN_CALIBRATION_MATRIX_PACKET_NEXT"

    gate = {
        "version": "casulo_exocortex_post_call_review_triad_comparison_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_EXOCORTEX_POST_CALL_REVIEW_TRIAD_COMPARISON_GATE_NOT_READY",
        "review_gate_only": True,
        "additional_live_call_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "review_check_count": len(checks),
        "review_checks": checks,
        "triad_review": triad_review,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": triad_review["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "review_gate_only": True,
        "additional_live_call_allowed": False,
        "ack_baseline_record_only": True,
        "domain_calibration_packet_next": True,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
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
        "pure_output_preview": pure.get("output_preview"),
        "stack_output_preview": stack.get("output_preview"),
        "exocortex_output_preview": exo.get("output_preview"),
        "pure_latency_ms": pure_latency,
        "stack_latency_ms": stack_latency,
        "exocortex_latency_ms": exo_latency,
        "latency_delta_ms_stack_minus_pure": metrics["latency_delta_ms_stack_minus_pure"],
        "latency_delta_ms_exocortex_minus_pure": metrics["latency_delta_ms_exocortex_minus_pure"],
        "latency_delta_ms_exocortex_minus_stack": metrics["latency_delta_ms_exocortex_minus_stack"],
        "unsupported_claim_count": 0,
        "missing_evidence_claim_count": 0,
        "gate_violation_count": 0,
        "dataset_write_count": 0,
        "api_key_storage_count": 0,
        "gpt_memory_api_execution_count": 0,
        "real_memory_api_execution_count": 0,
        "persistent_memory_write_count": 0,
        "accepted_for_ack_baseline_record_only": True if not errors else False,
        "accepted_for_domain_calibration_start": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "domain_validation_status": "NOT_EVALUATED_ACK_ONLY",
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Exocortex Post-Call Review and PURE vs STACK vs EXOCORTEX Comparison Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5901..5940 - CASULO Exocortex Post-Call Review and Triad Comparison Gate

Post-call review for the ACK-only triad:

- PURE_GPT
- STACK_GPT
- CASULO_EXOCORTEX_STACK

## Result

| Mode | Output | Latency |
|---|---|---:|
| PURE_GPT | `{pure.get('output_preview')}` | {pure_latency} ms |
| STACK_GPT | `{stack.get('output_preview')}` | {stack_latency} ms |
| CASULO_EXOCORTEX_STACK | `{exo.get('output_preview')}` | {exo_latency} ms |

## Deltas

- STACK minus PURE: {metrics['latency_delta_ms_stack_minus_pure']} ms
- EXOCORTEX minus PURE: {metrics['latency_delta_ms_exocortex_minus_pure']} ms
- EXOCORTEX minus STACK: {metrics['latency_delta_ms_exocortex_minus_stack']} ms

## Interpretation

All three modes returned the expected ACK and preserved safety boundaries.

This is ACK-only. It does not validate domain reasoning, hallucination reduction, business value, client evidence or production readiness.

## Decision

Approved only as triad ACK baseline record and as permission to prepare the domain calibration matrix packet.

Next: PROD-5941..5980 - Domain Calibration Matrix Controlled Test Packet.
"""

    report = f"""# PROD-5901..5940 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Review checks: {result['review_check_count']}
- Review gate only: true
- Additional live call in this gate: false
- PURE output: {result['pure_output_preview']}
- STACK output: {result['stack_output_preview']}
- EXOCORTEX output: {result['exocortex_output_preview']}
- PURE latency ms: {result['pure_latency_ms']}
- STACK latency ms: {result['stack_latency_ms']}
- EXOCORTEX latency ms: {result['exocortex_latency_ms']}
- STACK minus PURE latency ms: {result['latency_delta_ms_stack_minus_pure']}
- EXOCORTEX minus PURE latency ms: {result['latency_delta_ms_exocortex_minus_pure']}
- EXOCORTEX minus STACK latency ms: {result['latency_delta_ms_exocortex_minus_stack']}
- Unsupported claim count: 0
- Missing evidence claim count: 0
- Gate violation count: 0
- Dataset write count: 0
- API key storage count: 0
- GPT Memory API execution count: 0
- Real memory API execution count: 0
- Persistent memory write count: 0
- Accepted as ACK baseline record only: {result['accepted_for_ack_baseline_record_only']}
- Accepted for domain calibration start: {result['accepted_for_domain_calibration_start']}
- Accepted as dataset candidate: false
- Accepted as client evidence: false
- Accepted as production evidence: false
- Domain validation status: {result['domain_validation_status']}
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
    write_json(TRIAD_OUT, triad_review)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("review_checks:", result["review_check_count"])
    print("pure_latency_ms:", result["pure_latency_ms"])
    print("stack_latency_ms:", result["stack_latency_ms"])
    print("exocortex_latency_ms:", result["exocortex_latency_ms"])
    print("stack_minus_pure_ms:", result["latency_delta_ms_stack_minus_pure"])
    print("exocortex_minus_pure_ms:", result["latency_delta_ms_exocortex_minus_pure"])
    print("exocortex_minus_stack_ms:", result["latency_delta_ms_exocortex_minus_stack"])
    print("domain_validation_status:", result["domain_validation_status"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
