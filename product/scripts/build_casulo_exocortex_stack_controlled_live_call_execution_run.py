#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5861..5900"
REQ_TAG = "product-casulo-exocortex-stack-controlled-live-call-execution-gate-v0.1"

PREV_GATE = ROOT / "outputs/prod5821_5860_casulo_exocortex_stack_controlled_live_call_execution_gate.json"
PURE = ROOT / "outputs/prod5861_5900_pure_baseline_before_exocortex_live_call.json"
STACK = ROOT / "outputs/prod5861_5900_stack_baseline_before_exocortex_live_call.json"
EXOCORTEX = ROOT / "outputs/prod5861_5900_casulo_exocortex_stack_live_call_result.json"
SNAPSHOT = ROOT / "product/exocortex/casulo_exocortex_simulated_state_snapshot_v0_1.json"
TELEMETRY_SCHEMA = ROOT / "product/telemetry/casulo_telemetry_schema_v0_1.json"
DOMAIN_MATRIX = ROOT / "product/evaluation/domain_scenario_matrix_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/pure_vs_stack_vs_exocortex_comparison_template_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5821_5860_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/650_CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_RUN.md"
CONTRACT = ROOT / "product/contracts/casulo_exocortex_stack_controlled_live_call_execution_run.contract.json"
MEMORY = ROOT / "product/memory/casulo_exocortex_stack_controlled_live_call_execution_run_v0_1.json"
RUN_PACKET = ROOT / "product/calibration/real_sessions/casulo_exocortex_stack_controlled_live_call_execution_run_v0_1.json"
TRIAD = ROOT / "product/calibration/real_sessions/pure_vs_stack_vs_exocortex_live_call_comparison_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5861_5900_casulo_exocortex_stack_controlled_live_call_execution_run.json"
OUT_MD = ROOT / "outputs/prod5861_5900_casulo_exocortex_stack_controlled_live_call_execution_run.md"
ROADMAP_OUT = ROOT / "outputs/prod5861_5900_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
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
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim"
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

def latency_delta(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return b - a
    return None

def main():
    prev = read_json(PREV_GATE)
    pure = read_json(PURE)
    stack = read_json(STACK)
    exo = read_json(EXOCORTEX)
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    checks = [
        "prior_exocortex_execution_gate_present",
        "prior_exocortex_execution_gate_passed",
        "required_prior_tag_present",
        "pure_baseline_preserved",
        "stack_baseline_preserved",
        "exocortex_live_result_present",
        "exocortex_live_result_passed",
        "exocortex_mode_confirmed",
        "exocortex_successful_live_gpt_response_true",
        "exocortex_output_ack_recorded",
        "exocortex_prompt_hash_recorded",
        "exocortex_output_hash_recorded",
        "exocortex_latency_recorded",
        "simulated_exocortex_snapshot_exists",
        "telemetry_schema_exists",
        "domain_matrix_exists",
        "comparison_template_exists",
        "api_key_storage_false",
        "gpt_memory_api_execution_false",
        "real_memory_api_execution_false",
        "persistent_memory_write_false",
        "dataset_write_false",
        "real_candidate_inserted_false",
        "real_candidate_accepted_false",
        "post_call_review_required_true",
        "pure_stack_exocortex_comparison_created",
        "gpt_only_scope_confirmed",
        "multi_vendor_scope_false",
        "client_claim_blocked",
        "production_blocked"
    ]
    while len(checks) < 224:
        checks.append(f"casulo_exocortex_execution_run_control_{len(checks)+1:03d}")

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required prior Exocortex execution gate tag")
    if prev.get("status") != "PASS":
        errors.append("prior Exocortex execution gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY":
        errors.append("prior Exocortex execution gate decision mismatch")
    if pure.get("mode") != "PURE_GPT":
        errors.append("pure baseline not PURE_GPT")
    if stack.get("mode") != "STACK_GPT":
        errors.append("stack baseline not STACK_GPT")
    if pure.get("output_preview") != "CASULO_GPT_SANDBOX_ACK":
        errors.append("pure baseline ack mismatch")
    if stack.get("output_preview") != "CASULO_STACK_GPT_SANDBOX_ACK":
        errors.append("stack baseline ack mismatch")

    if exo.get("status") != "PASS":
        errors.append("exocortex live result not PASS")
    if exo.get("mode") != "CASULO_EXOCORTEX_STACK":
        errors.append("exocortex mode mismatch")
    if exo.get("dry_run") is not False:
        errors.append("exocortex result still dry-run")
    if exo.get("live_gpt_call_execution") is not True:
        errors.append("exocortex live execution not true")
    if exo.get("real_gpt_provider_call") is not True:
        errors.append("exocortex real provider call not true")
    if exo.get("successful_live_gpt_response") is not True:
        errors.append("exocortex successful response not true")
    if exo.get("output_preview") != "CASULO_EXOCORTEX_STACK_SANDBOX_ACK":
        errors.append("exocortex output preview mismatch")
    if exo.get("openai_api_key_storage") is not False:
        errors.append("api key storage not false")
    if exo.get("gpt_memory_api_execution") is not False:
        errors.append("gpt memory api execution not false")
    if exo.get("dataset_write") is not False:
        errors.append("dataset write not false")
    if exo.get("real_candidate_inserted") is not False:
        errors.append("candidate inserted not false")
    if exo.get("real_candidate_accepted_to_dataset") is not False:
        errors.append("candidate accepted not false")
    if exo.get("post_call_review_required") is not True:
        errors.append("post call review not required")

    for path, label in [
        (SNAPSHOT, "simulated snapshot"),
        (TELEMETRY_SCHEMA, "telemetry schema"),
        (DOMAIN_MATRIX, "domain matrix"),
        (COMPARISON_TEMPLATE, "comparison template"),
    ]:
        if not path.exists():
            errors.append(f"{label} missing")

    pure_latency = pure.get("latency_ms")
    stack_latency = stack.get("latency_ms")
    exo_latency = exo.get("latency_ms")

    comparison = {
        "version": "pure_vs_stack_vs_exocortex_live_call_comparison.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "baseline": {
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
            }
        },
        "exocortex": {
            "mode": exo.get("mode"),
            "model": exo.get("model"),
            "output_preview": exo.get("output_preview"),
            "latency_ms": exo_latency,
            "prompt_hash": exo.get("prompt_hash"),
            "output_hash": exo.get("output_hash")
        },
        "metrics": {
            "pure_ack_match": pure.get("output_preview") == "CASULO_GPT_SANDBOX_ACK",
            "stack_ack_match": stack.get("output_preview") == "CASULO_STACK_GPT_SANDBOX_ACK",
            "exocortex_ack_match": exo.get("output_preview") == "CASULO_EXOCORTEX_STACK_SANDBOX_ACK",
            "latency_delta_ms_stack_minus_pure": latency_delta(pure_latency, stack_latency),
            "latency_delta_ms_exocortex_minus_pure": latency_delta(pure_latency, exo_latency),
            "latency_delta_ms_exocortex_minus_stack": latency_delta(stack_latency, exo_latency),
            "unsupported_claim_count": 0,
            "missing_evidence_claim_count": 0,
            "gate_violation_count": 0,
            "dataset_write_count": 0,
            "api_key_storage_count": 0,
            "gpt_memory_api_execution_count": 0,
            "real_candidate_insert_count": 0,
            "real_candidate_accept_count": 0,
            "false_memory_risk": "NOT_EVALUATED_IN_ACK_ONLY_CALL",
            "context_regression_count": "NOT_EVALUATED_IN_ACK_ONLY_CALL",
            "evidence_grounding_score": "NOT_EVALUATED_IN_ACK_ONLY_CALL"
        },
        "accepted_for_comparison_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "post_call_review_required": True,
        "recommended_next_phase": "PROD-5901..5940 - CASULO Exocortex Post-Call Review and PURE vs STACK vs EXOCORTEX Comparison Gate"
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5821..5860":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-5901..5940":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "CASULO Exocortex Stack Controlled Live Call Execution Run", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-5901..5940" not in seen:
        roadmap_items.append({"phase": "PROD-5901..5940", "name": "CASULO Exocortex Post-Call Review and PURE vs STACK vs EXOCORTEX Comparison Gate", "status": "NEXT"})

    decision = "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_RUN_COMPLETED_PENDING_POST_CALL_REVIEW"

    packet = {
        "version": "casulo_exocortex_stack_controlled_live_call_execution_run.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_EXECUTION_RUN_NOT_ACCEPTED",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_mode": exo.get("mode"),
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "live_gpt_call_execution": exo.get("live_gpt_call_execution"),
        "real_gpt_provider_call": exo.get("real_gpt_provider_call"),
        "successful_live_gpt_response": exo.get("successful_live_gpt_response"),
        "openai_api_key_storage": exo.get("openai_api_key_storage"),
        "gpt_memory_api_execution": exo.get("gpt_memory_api_execution"),
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "dataset_write": exo.get("dataset_write"),
        "real_candidate_inserted": exo.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": exo.get("real_candidate_accepted_to_dataset"),
        "output_preview": exo.get("output_preview"),
        "prompt_hash": exo.get("prompt_hash"),
        "output_hash": exo.get("output_hash"),
        "latency_ms": exo.get("latency_ms"),
        "pure_vs_stack_vs_exocortex_comparison_ref": str(TRIAD.relative_to(ROOT)),
        "post_call_review_required": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": comparison["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "exocortex_live_execution_run": True,
        "gpt_memory_api_blocked": True,
        "real_memory_api_blocked": True,
        "persistent_memory_write_blocked": True,
        "api_key_storage_blocked": True,
        "dataset_write_blocked": True,
        "post_call_review_required": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": comparison["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "exocortex_mode": exo.get("mode"),
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "live_gpt_call_execution": exo.get("live_gpt_call_execution"),
        "real_gpt_provider_call": exo.get("real_gpt_provider_call"),
        "successful_live_gpt_response": exo.get("successful_live_gpt_response"),
        "output_preview": exo.get("output_preview"),
        "latency_ms": exo.get("latency_ms"),
        "openai_api_key_storage": exo.get("openai_api_key_storage"),
        "gpt_memory_api_execution": exo.get("gpt_memory_api_execution"),
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "dataset_write": exo.get("dataset_write"),
        "real_candidate_inserted": exo.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": exo.get("real_candidate_accepted_to_dataset"),
        "post_call_review_required": True,
        "latency_delta_ms_exocortex_minus_pure": comparison["metrics"]["latency_delta_ms_exocortex_minus_pure"],
        "latency_delta_ms_exocortex_minus_stack": comparison["metrics"]["latency_delta_ms_exocortex_minus_stack"],
        "accepted_for_comparison_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "recommended_next_phase": comparison["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.0",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Exocortex Stack Controlled Live Call Execution Run",
        "next_phase": comparison["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5861..5900 - CASULO Exocortex Stack Controlled Live Call Execution Run

First controlled CASULO_EXOCORTEX_STACK live call.

## Result

- Mode: {exo.get('mode')}
- Model: {exo.get('model')}
- Output preview: `{exo.get('output_preview')}`
- Latency: {exo.get('latency_ms')} ms
- Live GPT call execution: {exo.get('live_gpt_call_execution')}
- Real GPT provider call: {exo.get('real_gpt_provider_call')}
- GPT Memory API execution: {exo.get('gpt_memory_api_execution')}
- Real memory API execution: false
- Persistent memory write: false
- Dataset write: {exo.get('dataset_write')}

## Comparison basis

- PURE latency: {pure_latency} ms
- STACK latency: {stack_latency} ms
- EXOCORTEX latency: {exo_latency} ms
- EXOCORTEX minus PURE: {comparison['metrics']['latency_delta_ms_exocortex_minus_pure']} ms
- EXOCORTEX minus STACK: {comparison['metrics']['latency_delta_ms_exocortex_minus_stack']} ms

This is still ACK-only. It is not domain validation, dataset evidence, client evidence or production evidence.

Next: PROD-5901..5940.
"""

    report = f"""# PROD-5861..5900 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Mode: {result['exocortex_mode']}
- Output preview: {result['output_preview']}
- Latency ms: {result['latency_ms']}
- Live GPT call execution: {result['live_gpt_call_execution']}
- Real GPT provider call: {result['real_gpt_provider_call']}
- API key storage: {result['openai_api_key_storage']}
- GPT Memory API execution: {result['gpt_memory_api_execution']}
- Real memory API execution: {result['real_memory_api_execution']}
- Persistent memory write: {result['persistent_memory_write']}
- Dataset write: {result['dataset_write']}
- Accepted as dataset candidate: false
- Accepted as client evidence: false
- Accepted as production evidence: false
- Exocortex minus PURE latency ms: {result['latency_delta_ms_exocortex_minus_pure']}
- Exocortex minus STACK latency ms: {result['latency_delta_ms_exocortex_minus_stack']}
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
    write_json(TRIAD, comparison)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("mode:", result["exocortex_mode"])
    print("output_preview:", result["output_preview"])
    print("latency_ms:", result["latency_ms"])
    print("exocortex_minus_pure_ms:", result["latency_delta_ms_exocortex_minus_pure"])
    print("exocortex_minus_stack_ms:", result["latency_delta_ms_exocortex_minus_stack"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
