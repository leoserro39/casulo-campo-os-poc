#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"

SOURCES = {
    "baseline_stack_hallucination": OUT / "prod1621_1660_baseline_stack_hallucination_evidence_pack.json",
    "provenance_rubric": OUT / "prod1661_1700_gpt_response_provenance_human_review_rubric.json",
    "business_taxonomy": OUT / "prod1701_1740_business_solution_telemetry_taxonomy.json",
    "business_ensemble": OUT / "prod1741_1780_business_solution_ensemble_scoring_model.json",
    "graph_ranking": OUT / "prod1781_1820_graph_based_opportunity_ranking.json",
    "human_calibration_dataset": OUT / "prod1821_1860_business_value_human_calibration_dataset.json"
}

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation_without_boundary",
    "gpt_call",
    "codex_execution",
    "public_api_publication",
    "custom_gpt_connection_without_human_approval",
    "final_threshold_calibration",
    "final_weight_calibration"
]

READINESS_DOMAINS = [
    "response_provenance_readiness",
    "real_gpt_capture_readiness",
    "human_review_completion_readiness",
    "business_value_calibration_readiness",
    "ensemble_weight_readiness",
    "graph_ranking_readiness",
    "client_claim_safety_readiness",
    "production_safety_readiness",
    "automation_codex_safety_readiness",
    "commercial_recommendation_safety_readiness"
]

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def status_bool(data):
    return data.get("status") == "PASS"

def readiness_item(status, reason, blockers=None, next_actions=None):
    return {
        "status": status,
        "reason": reason,
        "blockers": blockers or [],
        "next_actions": next_actions or []
    }

def main():
    loaded = {}
    errors = []

    for key, path in SOURCES.items():
        if not path.exists():
            errors.append(f"Missing source: {key} -> {path}")
        else:
            loaded[key] = load(path)

    baseline = loaded.get("baseline_stack_hallucination", {})
    provenance = loaded.get("provenance_rubric", {})
    taxonomy = loaded.get("business_taxonomy", {})
    ensemble = loaded.get("business_ensemble", {})
    graph = loaded.get("graph_ranking", {})
    human_dataset = loaded.get("human_calibration_dataset", {})

    human_ds = human_dataset.get("dataset", {})
    provenance_obj = provenance.get("provenance", {})
    ensemble_obj = ensemble.get("ensemble", {})
    graph_obj = graph.get("graph", {})

    prior_all_pass = all(status_bool(v) for v in loaded.values()) if loaded else False

    real_gpt_capture_ready = False
    human_review_completed = human_ds.get("calibration_eligible_count", 0) > 0
    final_weights_ready = ensemble_obj.get("calibration_status") != "NOT_CALIBRATED_PROVISIONAL_WEIGHTS_ONLY"
    graph_ready = status_bool(graph) and graph_obj.get("node_count", 0) >= 30 and graph_obj.get("edge_count", 0) >= 50

    readiness = {
        "response_provenance_readiness": readiness_item(
            "PARTIAL_READY",
            "Response provenance classes exist and prior evidence is explicitly labeled as simulated fixture.",
            blockers=["real_gpt_capture_missing"],
            next_actions=["capture_real_gpt_responses_or_manual_pasted_gpt_responses"]
        ),
        "real_gpt_capture_readiness": readiness_item(
            "BLOCKED",
            "No real GPT response capture is approved or present for calibration.",
            blockers=["gpt_call_blocked", "manual_real_capture_not_reviewed"],
            next_actions=["use_manual_capture_template_or_controlled_action_capture_after_human_approval"]
        ),
        "human_review_completion_readiness": readiness_item(
            "BLOCKED",
            "Business value calibration dataset exists, but all cases are still pending human review.",
            blockers=["human_review_not_completed", "calibration_eligible_count_zero"],
            next_actions=["complete_business_value_human_reviews", "complete_response_boundary_human_reviews"]
        ),
        "business_value_calibration_readiness": readiness_item(
            "PARTIAL_READY",
            "Business taxonomy, ensemble, graph ranking and human calibration dataset exist.",
            blockers=["human_review_pending", "real_client_or_anonymized_data_missing"],
            next_actions=["review_7_business_value_cases", "add_real_or_anonymized_business_cases"]
        ),
        "ensemble_weight_readiness": readiness_item(
            "BLOCKED",
            "Ensemble weights are provisional and must not be treated as final.",
            blockers=["final_weight_calibration_blocked", "sensitivity_analysis_missing"],
            next_actions=["run_weight_sensitivity_analysis", "compare_human_review_scores_against_model_scores"]
        ),
        "graph_ranking_readiness": readiness_item(
            "PARTIAL_READY" if graph_ready else "BLOCKED",
            "Graph ranking exists as in-memory analytical projection, not production graph write.",
            blockers=["production_graph_write_blocked", "ranking_based_on_synthetic_taxonomy"],
            next_actions=["compare_graph_ranking_with_human_review_priority"]
        ),
        "client_claim_safety_readiness": readiness_item(
            "BLOCKED",
            "Client-facing claims remain blocked until real evidence, review and claim boundary approval exist.",
            blockers=["client_facing_claim_blocked", "no_final_claim_review"],
            next_actions=["define_client_safe_language", "review_claims_after_calibration"]
        ),
        "production_safety_readiness": readiness_item(
            "BLOCKED",
            "Production activation remains blocked.",
            blockers=["production_activation_blocked", "real_world_side_effect_blocked"],
            next_actions=["define_production_go_no_go_pack_later"]
        ),
        "automation_codex_safety_readiness": readiness_item(
            "BLOCKED",
            "Codex execution, automatic merge and autonomous implementation remain blocked.",
            blockers=["codex_execution_blocked", "automatic_merge_blocked", "implementation_execution_blocked"],
            next_actions=["keep_actions_as_backlog_or_review_packets_only"]
        ),
        "commercial_recommendation_safety_readiness": readiness_item(
            "PARTIAL_READY",
            "Commercial recommendation patterns exist, but remain synthetic and require human review before claims.",
            blockers=["human_review_pending", "no_real_sales_discovery_data"],
            next_actions=["review_package_fit", "review_pilot_priority", "validate_value_hypotheses"]
        )
    }

    ready_counts = {
        "ready": len([v for v in readiness.values() if v["status"] == "READY"]),
        "partial_ready": len([v for v in readiness.values() if v["status"] == "PARTIAL_READY"]),
        "blocked": len([v for v in readiness.values() if v["status"] == "BLOCKED"])
    }

    go_no_go = {
        "threshold_calibration_go": False,
        "threshold_calibration_status": "NO_GO",
        "reason": "Final threshold calibration remains blocked by missing real GPT capture, pending human review and provisional weights.",
        "minimum_go_requirements": [
            "all_sources_pass",
            "real_gpt_or_manual_pasted_response_capture_reviewed",
            "business_value_human_review_completed",
            "reviewer_agreement_or_single_reviewer_exception_recorded",
            "weight_sensitivity_analysis_completed",
            "client_claim_boundary_review_completed",
            "production_boundary_review_completed",
            "final_go_no_go_review_approved"
        ]
    }

    checks = {
        "all_sources_exist": len(loaded) == len(SOURCES),
        "all_sources_pass": prior_all_pass,
        "baseline_stack_hallucination_pass": status_bool(baseline),
        "provenance_rubric_pass": status_bool(provenance),
        "business_taxonomy_pass": status_bool(taxonomy),
        "business_ensemble_pass": status_bool(ensemble),
        "graph_ranking_pass": status_bool(graph),
        "human_calibration_dataset_pass": status_bool(human_dataset),
        "human_review_case_count": human_ds.get("case_count") == 7,
        "human_review_dimension_count": human_ds.get("review_dimension_count") == 10,
        "calibration_eligible_count_zero": human_ds.get("calibration_eligible_count") == 0,
        "real_gpt_capture_required": provenance_obj.get("real_gpt_capture_required_before_threshold_calibration") is True,
        "prior_evidence_not_real_gpt_capture": provenance_obj.get("current_prior_evidence_is_real_gpt_capture") is False,
        "ensemble_weights_not_final": ensemble_obj.get("calibration_status") == "NOT_CALIBRATED_PROVISIONAL_WEIGHTS_ONLY",
        "graph_ranking_not_final_calibration": graph_obj.get("calibration_status") == "NOT_CALIBRATED_GRAPH_RANKING_ONLY",
        "readiness_domain_count": len(readiness) == 10,
        "threshold_calibration_go": go_no_go["threshold_calibration_go"] is True,
        "threshold_calibration_no_go_expected": go_no_go["threshold_calibration_go"] is False
    }

    if not checks["all_sources_exist"]:
        errors.append("Not all required sources exist")
    if not checks["all_sources_pass"]:
        errors.append("Not all required sources are PASS")
    if not checks["calibration_eligible_count_zero"]:
        errors.append("Expected zero calibration eligible cases before human review")
    if not checks["real_gpt_capture_required"]:
        errors.append("Real GPT capture must be required before threshold calibration")
    if not checks["prior_evidence_not_real_gpt_capture"]:
        errors.append("Prior simulated evidence must not be treated as real GPT capture")
    if not checks["ensemble_weights_not_final"]:
        errors.append("Ensemble weights must remain provisional in this phase")
    if not checks["threshold_calibration_no_go_expected"]:
        errors.append("Threshold calibration must remain NO-GO in this phase")

    status = "PASS" if not errors else "FAIL"
    decision = "CALIBRATION_GOVERNANCE_READY_THRESHOLDS_NOT_APPROVED" if status == "PASS" else "CALIBRATION_GOVERNANCE_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1861..1900",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness": {
            "domains": readiness,
            "counts": ready_counts,
            "go_no_go": go_no_go,
            "calibration_status": "NOT_CALIBRATED_THRESHOLDS_NOT_APPROVED"
        },
        "source_summary": {
            "baseline_stack_hallucination": baseline.get("decision"),
            "provenance_rubric": provenance.get("decision"),
            "business_taxonomy": taxonomy.get("decision"),
            "business_ensemble": ensemble.get("decision"),
            "graph_ranking": graph.get("decision"),
            "human_calibration_dataset": human_dataset.get("decision")
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1861_1900_calibration_governance_threshold_readiness_pack.json"
    md_path = OUT / "prod1861_1900_calibration_governance_threshold_readiness_pack.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1861..1900 Calibration Governance and Threshold Readiness Pack",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Calibration status: `{result['readiness']['calibration_status']}`",
        f"- Threshold calibration go: `{go_no_go['threshold_calibration_go']}`",
        f"- Threshold calibration status: `{go_no_go['threshold_calibration_status']}`",
        f"- Ready domains: `{ready_counts['ready']}`",
        f"- Partial-ready domains: `{ready_counts['partial_ready']}`",
        f"- Blocked domains: `{ready_counts['blocked']}`",
        "",
        "## Go / No-Go",
        f"- Reason: {go_no_go['reason']}",
        "",
        "## Minimum Go Requirements"
    ]

    for req in go_no_go["minimum_go_requirements"]:
        md.append(f"- {req}")

    md += ["", "## Readiness Domains"]
    for name, item in readiness.items():
        md += [
            f"### {name}",
            f"- Status: `{item['status']}`",
            f"- Reason: {item['reason']}",
            f"- Blockers: `{', '.join(item['blockers'])}`",
            f"- Next actions: `{', '.join(item['next_actions'])}`",
            ""
        ]

    md += ["## Source Summary"]
    for key, value in result["source_summary"].items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Checks"]
    for key, value in checks.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Errors"]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Boundary",
        "- Calibration governance only.",
        "- Thresholds are not approved.",
        "- Final weights are not approved.",
        "- No GPT connection.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No production connection.",
        "- No client-facing claim.",
        "",
        "## Blocked Actions"
    ]
    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
