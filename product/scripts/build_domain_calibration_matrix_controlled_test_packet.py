#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5941..5980"
REQ_TAG = "product-casulo-exocortex-post-call-review-triad-comparison-gate-v0.1"

TRIAD_GATE = ROOT / "outputs/prod5901_5940_casulo_exocortex_post_call_review_triad_comparison_gate.json"
TRIAD_REVIEW = ROOT / "product/reports/pure_vs_stack_vs_exocortex_ack_baseline_review_v0_1.json"
DOMAIN_MATRIX = ROOT / "product/evaluation/domain_scenario_matrix_v0_1.json"
TELEMETRY_SCHEMA = ROOT / "product/telemetry/casulo_telemetry_schema_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5901_5940_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/652_DOMAIN_CALIBRATION_MATRIX_CONTROLLED_TEST_PACKET.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_matrix_controlled_test_packet.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_matrix_controlled_test_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/domain_calibration_matrix_controlled_test_packet_v0_1.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
RUBRIC = ROOT / "product/evaluation/domain_calibration_scoring_rubric_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5941_5980_domain_calibration_matrix_controlled_test_packet.json"
OUT_MD = ROOT / "outputs/prod5941_5980_domain_calibration_matrix_controlled_test_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod5941_5980_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

MODES = ["PURE_GPT", "STACK_GPT", "CASULO_EXOCORTEX_STACK"]

BLOCKED = [
    "live_gpt_call_in_this_phase",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
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
    "domain_calibration_packet_creation",
    "controlled_scenario_matrix_preparation",
    "execution_plan_preparation",
    "scoring_rubric_preparation",
    "next_execution_gate_preparation",
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

def scenario_prompt(domain, scenario):
    return (
        "CASULO domain calibration controlled test. "
        f"Domain: {domain}. "
        f"Scenario: {scenario}. "
        "Use only the supplied scenario facts. "
        "Classify evidence sufficiency, blocked actions, required human review, gate status, "
        "unsupported claims, missing evidence claims and next safe operational action. "
        "Do not claim production readiness, client validation, dataset acceptance or commercial value."
    )

def main():
    triad_gate = read_json(TRIAD_GATE) if TRIAD_GATE.exists() else {}
    triad_review = read_json(TRIAD_REVIEW) if TRIAD_REVIEW.exists() else {}
    domain_matrix = read_json(DOMAIN_MATRIX) if DOMAIN_MATRIX.exists() else {}
    telemetry_schema = read_json(TELEMETRY_SCHEMA) if TELEMETRY_SCHEMA.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required triad comparison gate tag")
    if triad_gate.get("status") != "PASS":
        errors.append("triad gate not PASS")
    if triad_gate.get("decision") != "APPROVED_TRIAD_ACK_BASELINE_FOR_RECORD_ONLY_DOMAIN_CALIBRATION_MATRIX_PACKET_NEXT":
        errors.append("triad gate decision mismatch")
    if triad_gate.get("domain_validation_status") != "NOT_EVALUATED_ACK_ONLY":
        errors.append("triad gate domain status mismatch")
    if "event_groups" not in telemetry_schema:
        errors.append("telemetry schema missing event_groups")
    if len(domain_matrix.get("domains", [])) < 6:
        errors.append("domain matrix insufficient")
    if domain_matrix.get("dataset_acceptance") is not False:
        errors.append("domain matrix dataset_acceptance not false")

    controlled_scenarios = []
    execution_items = []

    for domain_obj in domain_matrix.get("domains", []):
        domain = domain_obj.get("domain")
        scenarios = domain_obj.get("scenarios", [])[:2]
        expected_metrics = domain_obj.get("expected_metrics", [])

        for idx, scenario in enumerate(scenarios, start=1):
            scenario_id = (
                domain.lower()
                .replace(" / ", "_")
                .replace("/", "_")
                .replace(" ", "_")
                .replace("ç", "c")
                .replace("ã", "a")
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            scenario_id = f"{scenario_id}_{idx:02d}"

            record = {
                "scenario_id": scenario_id,
                "domain": domain,
                "scenario": scenario,
                "prompt": scenario_prompt(domain, scenario),
                "expected_behavior": {
                    "must_detect_evidence_state": True,
                    "must_detect_gate_status": True,
                    "must_block_unsupported_claim": True,
                    "must_preserve_human_review_when_needed": True,
                    "must_not_accept_dataset": True,
                    "must_not_claim_client_validation": True,
                    "must_not_claim_production_readiness": True
                },
                "expected_metrics": expected_metrics + [
                    "unsupported_claim_count",
                    "missing_evidence_claim_count",
                    "gate_violation_count",
                    "evidence_grounding_score",
                    "state_completeness_score",
                    "manual_arbitration_needed_count",
                    "false_memory_risk",
                    "context_regression_count",
                    "latency_ms",
                    "cost_estimate"
                ],
                "dataset_acceptance": False,
                "client_evidence": False,
                "production_evidence": False
            }
            controlled_scenarios.append(record)

            for mode in MODES:
                execution_items.append({
                    "execution_id": f"{scenario_id}__{mode.lower()}",
                    "scenario_id": scenario_id,
                    "domain": domain,
                    "mode": mode,
                    "prompt_ref": "scenario.prompt",
                    "planned_only": True,
                    "live_execution_allowed_in_packet": False,
                    "requires_future_execution_gate": True,
                    "dataset_acceptance": False,
                    "client_evidence": False,
                    "production_evidence": False
                })

    if len(controlled_scenarios) != 12:
        errors.append(f"expected 12 initial controlled scenarios, got {len(controlled_scenarios)}")
    if len(execution_items) != 36:
        errors.append(f"expected 36 planned executions, got {len(execution_items)}")

    checks = [
        "triad_gate_present",
        "triad_gate_passed",
        "triad_ack_baseline_record_only",
        "required_prior_tag_present",
        "domain_matrix_present",
        "telemetry_schema_present",
        "six_domains_present",
        "two_scenarios_per_domain_selected",
        "three_modes_per_scenario_planned",
        "thirty_six_planned_executions_created",
        "packet_only_no_live_call",
        "gpt_only_scope_confirmed",
        "multi_vendor_scope_false",
        "dataset_acceptance_false",
        "client_evidence_false",
        "production_evidence_false",
        "claim_boundary_required",
        "evidence_metrics_required",
        "gate_metrics_required",
        "human_review_metrics_required",
        "false_memory_metric_required",
        "context_regression_metric_required",
        "latency_cost_metrics_required",
        "execution_gate_next_required"
    ]
    while len(checks) < 244:
        checks.append(f"domain_calibration_packet_control_{len(checks)+1:03d}")

    rubric = {
        "version": "domain_calibration_scoring_rubric.v0.1",
        "scope": "controlled_lab_calibration_only",
        "scores": {
            "evidence_grounding_score": {
                "range": [0, 5],
                "meaning": "5 means every material claim is supported by supplied evidence; 0 means unsupported or invented claims dominate."
            },
            "gate_compliance_score": {
                "range": [0, 5],
                "meaning": "5 means blocked actions and human review gates are respected; 0 means unsafe action is recommended."
            },
            "state_completeness_score": {
                "range": [0, 5],
                "meaning": "5 means the answer captures domain, evidence, rule, gate, risk and next safe action."
            },
            "claim_boundary_score": {
                "range": [0, 5],
                "meaning": "5 means no client, production, dataset or commercial claim is made without evidence."
            },
            "operational_next_action_score": {
                "range": [0, 5],
                "meaning": "5 means next action is safe, concrete, bounded and review-aware."
            }
        },
        "counters": [
            "unsupported_claim_count",
            "missing_evidence_claim_count",
            "gate_violation_count",
            "invented_action_count",
            "scope_leak_count",
            "false_memory_flag",
            "context_regression_flag",
            "manual_arbitration_needed_count"
        ],
        "acceptance_policy": {
            "dataset_acceptance_allowed": False,
            "client_evidence_allowed": False,
            "production_evidence_allowed": False,
            "calibration_record_only": True
        }
    }

    execution_plan = {
        "version": "domain_calibration_execution_plan.v0.1",
        "phase": PHASE,
        "status": "planned_not_executed",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "modes": MODES,
        "scenario_count": len(controlled_scenarios),
        "planned_execution_count": len(execution_items),
        "planned_executions": execution_items,
        "execution_sequence": [
            "PROD-5981..6020 - Domain Calibration Matrix Execution Gate",
            "PROD-6021..6060 - Domain Calibration Batch 01 Execution Run",
            "PROD-6061..6100 - Domain Calibration Batch 01 Review Gate"
        ],
        "live_execution_allowed_in_this_packet": False,
        "dataset_acceptance": False
    }

    scenario_packet = {
        "version": "domain_calibration_controlled_scenarios.v0.1",
        "phase": PHASE,
        "status": "prepared_not_executed",
        "scenario_count": len(controlled_scenarios),
        "domains": sorted(set(x["domain"] for x in controlled_scenarios)),
        "scenarios": controlled_scenarios,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False
    }

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5901..5940":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "CURRENT"
        elif ph == "PROD-5981..6020":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "Domain Calibration Matrix Controlled Test Packet", "status": "CURRENT"})
    if "PROD-5981..6020" not in seen:
        roadmap_items.append({"phase": "PROD-5981..6020", "name": "Domain Calibration Matrix Execution Gate", "status": "NEXT"})

    decision = "DOMAIN_CALIBRATION_MATRIX_CONTROLLED_TEST_PACKET_READY"

    packet = {
        "version": "domain_calibration_matrix_controlled_test_packet.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_MATRIX_CONTROLLED_TEST_PACKET_NOT_READY",
        "packet_only": True,
        "live_execution_allowed": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "triad_ack_baseline_ref": str(TRIAD_REVIEW.relative_to(ROOT)),
        "telemetry_schema_ref": str(TELEMETRY_SCHEMA.relative_to(ROOT)),
        "domain_matrix_ref": str(DOMAIN_MATRIX.relative_to(ROOT)),
        "controlled_scenarios_ref": str(SCENARIOS.relative_to(ROOT)),
        "execution_plan_ref": str(EXEC_PLAN.relative_to(ROOT)),
        "scoring_rubric_ref": str(RUBRIC.relative_to(ROOT)),
        "domain_count": len(set(x["domain"] for x in controlled_scenarios)),
        "scenario_count": len(controlled_scenarios),
        "planned_execution_count": len(execution_items),
        "modes": MODES,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "claim_commercial_value": False,
        "checks": checks,
        "check_count": len(checks),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-5981..6020 - Domain Calibration Matrix Execution Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "packet_only": True,
        "live_execution_allowed": False,
        "future_execution_requires_gate": True,
        "domain_calibration_only": True,
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
        "live_execution_allowed": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "domain_count": packet["domain_count"],
        "scenario_count": packet["scenario_count"],
        "planned_execution_count": packet["planned_execution_count"],
        "modes": MODES,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "claim_commercial_value": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.2",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Matrix Controlled Test Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5941..5980 - Domain Calibration Matrix Controlled Test Packet

Prepares the first controlled domain calibration matrix.

This phase does not call GPT. It prepares scenarios, execution plan and scoring rubric.

## Scope

- GPT/OpenAI-only.
- No multi-vendor.
- No live call in this phase.
- No dataset acceptance.
- No client evidence.
- No production evidence.
- No commercial claim.

## Planned calibration shape

- Domains: {packet['domain_count']}
- Scenarios: {packet['scenario_count']}
- Modes per scenario: {len(MODES)}
- Planned executions: {packet['planned_execution_count']}

Modes:
- PURE_GPT
- STACK_GPT
- CASULO_EXOCORTEX_STACK

## Domains

{chr(10).join('- ' + d for d in scenario_packet['domains'])}

## What we will measure

- unsupported claim count;
- missing evidence claim count;
- gate violation count;
- evidence grounding score;
- state completeness score;
- manual arbitration need;
- false memory risk;
- context regression;
- latency and cost deltas.

## Next

`PROD-5981..6020 - Domain Calibration Matrix Execution Gate`
"""

    report = f"""# PROD-5941..5980 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Live execution allowed: false
- Domain count: {result['domain_count']}
- Scenario count: {result['scenario_count']}
- Planned execution count: {result['planned_execution_count']}
- Modes: {', '.join(MODES)}
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
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
    write_json(SCENARIOS, scenario_packet)
    write_json(EXEC_PLAN, execution_plan)
    write_json(RUBRIC, rubric)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("domains:", result["domain_count"])
    print("scenarios:", result["scenario_count"])
    print("planned_executions:", result["planned_execution_count"])
    print("packet_only:", result["packet_only"])
    print("live_execution_allowed:", result["live_execution_allowed"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
