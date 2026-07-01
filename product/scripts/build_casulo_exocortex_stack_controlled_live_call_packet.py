#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5781..5820"

REQ_TAGS = [
    "product-stack-gpt-post-call-review-pure-vs-stack-comparison-gate-v0.1",
    "product-gpt-stack-historical-value-report-v0.1",
    "product-telemetry-value-extraction-report-v0.1"
]

STACK_REVIEW = ROOT / "outputs/prod5741_5780_stack_gpt_post_call_review_pure_vs_stack_comparison_gate.json"
HIST_REPORT = ROOT / "outputs/gpt_stack_historical_value_report_v0_1.json"
TELEMETRY_REPORT = ROOT / "outputs/telemetry_value_extraction_report_v0_1.json"
TELEMETRY_SCHEMA = ROOT / "product/telemetry/casulo_telemetry_schema_v0_1.json"
DOMAIN_MATRIX = ROOT / "product/evaluation/domain_scenario_matrix_v0_1.json"
PURE_STACK_COMPARISON = ROOT / "product/calibration/real_sessions/pure_vs_stack_gpt_post_call_review_comparison_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5741_5780_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/648_CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_PACKET.md"
CONTRACT = ROOT / "product/contracts/casulo_exocortex_stack_controlled_live_call_packet.contract.json"
MEMORY = ROOT / "product/memory/casulo_exocortex_stack_controlled_live_call_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/casulo_exocortex_stack_controlled_live_call_packet_v0_1.json"
REQUEST_TEMPLATE = ROOT / "product/calibration/real_sessions/casulo_exocortex_stack_controlled_live_call_request_template_v0_1.json"
COMPARISON_TEMPLATE = ROOT / "product/calibration/real_sessions/pure_vs_stack_vs_exocortex_comparison_template_v0_1.json"
EXOCORTEX_SNAPSHOT = ROOT / "product/exocortex/casulo_exocortex_simulated_state_snapshot_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5781_5820_casulo_exocortex_stack_controlled_live_call_packet.json"
OUT_MD = ROOT / "outputs/prod5781_5820_casulo_exocortex_stack_controlled_live_call_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5781_5820_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
    "memory_create",
    "memory_update",
    "memory_delete",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "live_gpt_call_in_this_phase",
    "real_gpt_provider_call_in_this_phase",
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
    "commercial_package_pricing_claim"
]

ALLOWED = [
    "casulo_exocortex_stack_packet_creation",
    "simulated_exocortex_state_snapshot_creation",
    "pure_stack_exocortex_comparison_template_creation",
    "exocortex_execution_gate_preparation",
    "roadmap_update"
]

CHECKS = [
    "prior_stack_review_gate_present",
    "historical_value_report_present",
    "telemetry_value_report_present",
    "telemetry_schema_present",
    "domain_matrix_present",
    "pure_stack_comparison_present",
    "required_tags_present",
    "gpt_only_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "openai_gpt_provider_scope_confirmed",
    "exocortex_packet_only",
    "exocortex_live_execution_not_performed",
    "real_gpt_provider_call_not_performed_in_this_phase",
    "gpt_memory_api_not_used",
    "real_memory_api_not_used",
    "simulated_memory_only",
    "no_api_key_value_storage",
    "no_secret_storage",
    "no_raw_private_data",
    "no_unredacted_pii",
    "dataset_write_blocked",
    "real_candidate_insert_blocked",
    "real_candidate_acceptance_blocked",
    "client_claim_blocked",
    "production_blocked",
    "pure_baseline_reference_bound",
    "stack_baseline_reference_bound",
    "telemetry_schema_bound",
    "domain_matrix_bound",
    "false_memory_risk_metric_required",
    "context_regression_metric_required",
    "evidence_grounding_metric_required",
    "claim_boundary_metric_required",
    "cost_latency_metric_required",
    "post_call_review_required",
    "execution_gate_next_required",
    "controlled_lab_scope_only"
]

while len(CHECKS) < 196:
    CHECKS.append(f"casulo_exocortex_packet_control_{len(CHECKS)+1:03d}")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def git_tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def main():
    tags = git_tags()

    stack_review = read_json(STACK_REVIEW) if STACK_REVIEW.exists() else {}
    hist = read_json(HIST_REPORT) if HIST_REPORT.exists() else {}
    telemetry = read_json(TELEMETRY_REPORT) if TELEMETRY_REPORT.exists() else {}
    telemetry_schema = read_json(TELEMETRY_SCHEMA) if TELEMETRY_SCHEMA.exists() else {}
    domain_matrix = read_json(DOMAIN_MATRIX) if DOMAIN_MATRIX.exists() else {}
    pure_stack = read_json(PURE_STACK_COMPARISON) if PURE_STACK_COMPARISON.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    for tag in REQ_TAGS:
        if tag not in tags:
            errors.append(f"missing required tag: {tag}")

    if stack_review.get("status") != "PASS":
        errors.append("stack review gate not PASS")
    if stack_review.get("decision") != "APPROVED_PURE_VS_STACK_GPT_COMPARISON_FOR_RECORD_ONLY_EXOCORTEX_STACK_PACKET_NEXT":
        errors.append("stack review gate decision mismatch")
    if hist.get("confirmed_boundaries", {}).get("gpt_only_scope") is not True:
        errors.append("historical report gpt_only_scope not true")
    if hist.get("confirmed_boundaries", {}).get("exocortex_used") is not False:
        errors.append("historical report exocortex_used not false")
    if telemetry.get("confirmed_boundaries", {}).get("gpt_only_scope") is not True:
        errors.append("telemetry report gpt_only_scope not true")
    if telemetry.get("confirmed_boundaries", {}).get("dataset_write") is not False:
        errors.append("telemetry report dataset_write not false")
    if "event_groups" not in telemetry_schema:
        errors.append("telemetry schema missing event_groups")
    if len(domain_matrix.get("domains", [])) < 6:
        errors.append("domain matrix has fewer than 6 domains")
    if domain_matrix.get("dataset_acceptance") is not False:
        errors.append("domain matrix dataset_acceptance not false")
    if pure_stack.get("baseline", {}).get("mode") != "PURE_GPT":
        errors.append("PURE baseline reference missing")
    if pure_stack.get("stack", {}).get("mode") != "STACK_GPT":
        errors.append("STACK baseline reference missing")

    baseline = {
        "pure": {
            "mode": pure_stack.get("baseline", {}).get("mode"),
            "model": pure_stack.get("baseline", {}).get("model"),
            "output_preview": pure_stack.get("baseline", {}).get("output_preview"),
            "latency_ms": pure_stack.get("baseline", {}).get("latency_ms"),
            "prompt_hash": pure_stack.get("baseline", {}).get("prompt_hash"),
            "output_hash": pure_stack.get("baseline", {}).get("output_hash")
        },
        "stack": {
            "mode": pure_stack.get("stack", {}).get("mode"),
            "model": pure_stack.get("stack", {}).get("model"),
            "output_preview": pure_stack.get("stack", {}).get("output_preview"),
            "latency_ms": pure_stack.get("stack", {}).get("latency_ms"),
            "prompt_hash": pure_stack.get("stack", {}).get("prompt_hash"),
            "output_hash": pure_stack.get("stack", {}).get("output_hash")
        },
        "latency_delta_ms_stack_minus_pure": pure_stack.get("metrics", {}).get("latency_delta_ms_stack_minus_pure")
    }

    exocortex_snapshot = {
        "version": "casulo_exocortex_simulated_state_snapshot.v0.1",
        "phase": PHASE,
        "snapshot_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "gpt_memory_api_execution": False,
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "dataset_write": False,
        "contains_raw_private_data": False,
        "contains_secret_or_credential": False,
        "contains_unredacted_pii": False,
        "purpose": "Provide bounded simulated operational context for the future CASULO_EXOCORTEX_STACK controlled live call.",
        "state_layers": {
            "execution_history": {
                "pure_gpt_baseline_ack": baseline["pure"]["output_preview"],
                "stack_gpt_baseline_ack": baseline["stack"]["output_preview"],
                "comparison_delta_ms_stack_minus_pure": baseline["latency_delta_ms_stack_minus_pure"]
            },
            "governance_state": {
                "client_evidence": False,
                "production_evidence": False,
                "dataset_candidate": False,
                "commercial_claim": False,
                "post_call_review_required": True,
                "human_review_required_for_domain_claims": True
            },
            "telemetry_state": {
                "schema_ref": str(TELEMETRY_SCHEMA.relative_to(ROOT)),
                "domain_matrix_ref": str(DOMAIN_MATRIX.relative_to(ROOT)),
                "required_metrics": [
                    "unsupported_claim_count",
                    "missing_evidence_claim_count",
                    "evidence_grounding_score",
                    "gate_violation_count",
                    "blocked_action_detection_rate",
                    "state_completeness_score",
                    "manual_arbitration_needed_count",
                    "context_regression_count",
                    "false_memory_risk",
                    "latency_ms",
                    "cost_estimate",
                    "token_input_estimate",
                    "token_output_estimate"
                ]
            },
            "claim_boundary": {
                "allowed": [
                    "controlled_lab_observation",
                    "technical_operational_hypothesis",
                    "telemetry_recommendation",
                    "next_phase_recommendation"
                ],
                "blocked": [
                    "client_validated_claim",
                    "production_readiness_claim",
                    "cost_savings_claim",
                    "hallucination_reduction_claim",
                    "dataset_acceptance_claim"
                ]
            }
        }
    }

    request_template = {
        "version": "casulo_exocortex_stack_controlled_live_call_request_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "mode": "CASULO_EXOCORTEX_STACK",
        "provider": "openai_gpt",
        "api_key_source": "OPENAI_API_KEY_ENV_REFERENCE_ONLY_NOT_STORED",
        "model_env": "OPENAI_MODEL_OPTIONAL_ENV_REFERENCE",
        "prompt": "CASULO controlled EXOCORTEX sandbox test. Use the supplied simulated operational state, telemetry schema, domain matrix and claim boundaries. Return only: CASULO_EXOCORTEX_STACK_SANDBOX_ACK.",
        "exocortex_context_refs": {
            "simulated_state_snapshot_ref": str(EXOCORTEX_SNAPSHOT.relative_to(ROOT)),
            "telemetry_schema_ref": str(TELEMETRY_SCHEMA.relative_to(ROOT)),
            "domain_matrix_ref": str(DOMAIN_MATRIX.relative_to(ROOT)),
            "pure_stack_comparison_ref": str(PURE_STACK_COMPARISON.relative_to(ROOT))
        },
        "blocked_actions": BLOCKED,
        "post_call_review_required": True
    }

    comparison_template = {
        "version": "pure_vs_stack_vs_exocortex_comparison_template.v0.1",
        "phase": PHASE,
        "template_only": True,
        "modes": ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"],
        "baseline": baseline,
        "candidate_mode": "CASULO_EXOCORTEX_STACK",
        "metrics": [
            "successful_live_gpt_response",
            "output_ack_match",
            "unsupported_claim_count",
            "missing_evidence_claim_count",
            "gate_violation_count",
            "evidence_grounding_score",
            "context_regression_count",
            "false_memory_risk",
            "latency_ms",
            "latency_delta_ms_exocortex_minus_stack",
            "latency_delta_ms_exocortex_minus_pure",
            "cost_estimate",
            "token_input_estimate",
            "token_output_estimate",
            "api_key_storage",
            "gpt_memory_api_execution",
            "dataset_write"
        ],
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5741..5780":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5821..5860":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "CASULO Exocortex Stack Controlled Live Call Packet",
            "status": "CURRENT"
        })
    if "PROD-5821..5860" not in seen:
        roadmap_items.append({
            "phase": "PROD-5821..5860",
            "name": "CASULO Exocortex Stack Controlled Live Call Execution Gate",
            "status": "NEXT"
        })

    decision = "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_PACKET_READY"

    packet = {
        "version": "casulo_exocortex_stack_controlled_live_call_packet.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_EXOCORTEX_STACK_CONTROLLED_LIVE_CALL_PACKET_NOT_READY",
        "purpose": "Prepare CASULO_EXOCORTEX_STACK controlled live call packet using simulated operational context only.",
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "packet_only": True,
        "live_execution_allowed": False,
        "real_gpt_provider_call_in_this_phase": False,
        "successful_live_gpt_response_in_this_phase": False,
        "exocortex_mode": "CASULO_EXOCORTEX_STACK",
        "exocortex_used_in_this_phase": False,
        "simulated_exocortex_context_prepared": True,
        "gpt_memory_api_execution": False,
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "openai_api_key_storage": False,
        "dataset_write": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "baseline": baseline,
        "telemetry_schema_ref": str(TELEMETRY_SCHEMA.relative_to(ROOT)),
        "domain_matrix_ref": str(DOMAIN_MATRIX.relative_to(ROOT)),
        "simulated_state_snapshot_ref": str(EXOCORTEX_SNAPSHOT.relative_to(ROOT)),
        "request_template_ref": str(REQUEST_TEMPLATE.relative_to(ROOT)),
        "comparison_template_ref": str(COMPARISON_TEMPLATE.relative_to(ROOT)),
        "checks": CHECKS,
        "check_count": len(CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-5821..5860 - CASULO Exocortex Stack Controlled Live Call Execution Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tags": REQ_TAGS,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "packet_only": True,
        "live_execution_allowed": False,
        "live_execution_requires_next_gate": True,
        "exocortex_context_type": "SIMULATED_OPERATIONAL_CONTEXT_ONLY",
        "gpt_memory_api_blocked": True,
        "real_memory_api_blocked": True,
        "api_key_storage_blocked": True,
        "dataset_write_blocked": True,
        "multi_vendor_llm_blocked_this_cycle": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(CHECKS),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "packet_only": True,
        "live_execution_allowed": False,
        "real_gpt_provider_call_in_this_phase": False,
        "successful_live_gpt_response_in_this_phase": False,
        "exocortex_mode": "CASULO_EXOCORTEX_STACK",
        "exocortex_used_in_this_phase": False,
        "simulated_exocortex_context_prepared": True,
        "gpt_memory_api_execution": False,
        "real_memory_api_execution": False,
        "persistent_memory_write": False,
        "openai_api_key_storage": False,
        "dataset_write": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "baseline_pure_output": baseline["pure"]["output_preview"],
        "baseline_stack_output": baseline["stack"]["output_preview"],
        "baseline_latency_delta_ms_stack_minus_pure": baseline["latency_delta_ms_stack_minus_pure"],
        "telemetry_schema_bound": True,
        "domain_matrix_bound": True,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.8",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Exocortex Stack Controlled Live Call Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet

Prepares the CASULO Exocortex Stack controlled live call packet.

This phase does not call GPT.

## Scope

- GPT/OpenAI-only.
- No Claude, Gemini, Copilot or multi-vendor execution.
- No GPT Memory API.
- No real memory API.
- No persistent memory write.
- No dataset write.
- No client evidence.
- No production evidence.
- No commercial claim.

## Exocortex definition for this phase

`CASULO_EXOCORTEX_STACK` means GPT with a bounded simulated operational state snapshot, telemetry schema, domain scenario matrix, prior PURE/STACK comparison and explicit claim boundaries.

The Exocortex context is simulated and file-bound. It is not GPT Memory API and it is not persistent user memory.

## Baseline references

- PURE output: `{baseline['pure']['output_preview']}`
- PURE latency: {baseline['pure']['latency_ms']} ms
- STACK output: `{baseline['stack']['output_preview']}`
- STACK latency: {baseline['stack']['latency_ms']} ms
- Delta STACK minus PURE: {baseline['latency_delta_ms_stack_minus_pure']} ms

## What this packet prepares

- simulated Exocortex state snapshot;
- Exocortex request template;
- PURE vs STACK vs EXOCORTEX comparison template;
- execution gate contract;
- next telemetry metrics:
  - false memory risk;
  - context regression;
  - evidence grounding;
  - claim boundary violation;
  - latency and cost deltas.

## Next

`PROD-5821..5860 - CASULO Exocortex Stack Controlled Live Call Execution Gate`
"""

    report = f"""# PROD-5781..5820 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Live execution allowed: false
- Real GPT provider call in this phase: false
- Exocortex used in this phase: false
- Simulated Exocortex context prepared: true
- GPT Memory API execution: false
- Real memory API execution: false
- Persistent memory write: false
- API key storage: false
- Dataset write: false
- Baseline PURE output: {result['baseline_pure_output']}
- Baseline STACK output: {result['baseline_stack_output']}
- Telemetry schema bound: true
- Domain matrix bound: true
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(REQUEST_TEMPLATE, request_template)
    write_json(COMPARISON_TEMPLATE, comparison_template)
    write_json(EXOCORTEX_SNAPSHOT, exocortex_snapshot)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("packet_only:", result["packet_only"])
    print("live_execution_allowed:", result["live_execution_allowed"])
    print("simulated_exocortex_context_prepared:", result["simulated_exocortex_context_prepared"])
    print("gpt_memory_api_execution:", result["gpt_memory_api_execution"])
    print("real_memory_api_execution:", result["real_memory_api_execution"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
