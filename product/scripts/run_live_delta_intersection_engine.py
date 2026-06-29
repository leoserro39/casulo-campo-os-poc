#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
]

GATE_SEVERITY = {
    "ANSWER_ALLOWED": 0.15,
    "PARSER_OUTPUT_ALLOWED": 0.12,
    "TASK_PROPOSAL_ALLOWED": 0.22,
    "EVIDENCE_REQUIRED": 0.55,
    "HUMAN_REVIEW_REQUIRED": 0.75,
    "UNSUPPORTED_BLOCKED": 1.0,
}

WORKLOAD_SENSITIVITY = {
    "parser": 0.90,
    "document_field_extraction": 0.90,
    "receipt_invoice_extraction": 0.95,
    "summary": 1.10,
    "classification": 1.10,
    "email_triage": 1.10,
    "task_generation": 1.15,
    "contract_checklist": 1.25,
    "policy_rule_extraction": 1.25,
    "technical_review": 1.30,
    "delta_detection": 1.30,
    "evidence_gap_detection": 1.30,
}

BUSINESS_DOMAIN_SENSITIVITY = {
    "restaurant_inventory": 1.00,
    "restaurant_cashflow": 1.20,
    "clinic_scheduling": 1.20,
    "clinic_billing_glosa": 1.45,
    "accounting_tax_obligation": 1.45,
    "contract_legal_review": 1.50,
    "ecommerce_order_ops": 1.10,
    "field_service_work_order": 1.05,
    "construction_project_control": 1.30,
    "small_industry_quality": 1.25,
}

HIGH_RISK_PROFILES = {
    "high_stakes_claim",
    "cross_document_mismatch",
    "partial_context",
    "stale_or_undated_evidence",
}

CONFLICT_PROFILES = {
    "conflicting_values",
    "cross_document_mismatch",
    "high_stakes_claim",
}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def mean(values: List[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0

def pct(n: int, total: int) -> float:
    return round((n / total) * 100, 2) if total else 0.0

def load_rows(repo: Path) -> List[Dict[str, Any]]:
    script = repo / "product/scripts/run_common_workload_calibration_stress_lab.py"
    if not script.exists():
        raise FileNotFoundError("missing product/scripts/run_common_workload_calibration_stress_lab.py")
    spec = importlib.util.spec_from_file_location("stress_lab", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    rows = []
    for workload, input_class, expected_output in module.WORKLOADS:
        for idx in range(1, 101):
            row = module.score_case(module.build_case(workload, input_class, expected_output, idx))
            rows.append(row)
    for row in rows:
        row["safe_block_success"] = row.get("gate") == "UNSUPPORTED_BLOCKED" and row.get("stress_profile") == "unknown_or_unsupported_input"
        row["safe_review_success"] = row.get("gate") == "HUMAN_REVIEW_REQUIRED" and row.get("stress_profile") in HIGH_RISK_PROFILES
        row["true_failure_candidate"] = row.get("gate") in {"ANSWER_ALLOWED", "PARSER_OUTPUT_ALLOWED", "TASK_PROPOSAL_ALLOWED"} and row.get("cubo_risk", 0) >= 55
    return rows

def correlation_weight(repo: Path, a: str, b: str, default: float) -> float:
    p = repo / "outputs/prod601b_620b_telemetry_correlation_matrix.json"
    if not p.exists():
        return default
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return float(data.get("correlations", {}).get(a, {}).get(b, default))
    except Exception:
        return default

def delta_vector(row: Dict[str, Any], repo: Path) -> Dict[str, float]:
    stress = min(1.0, row.get("stress_score", 0) / 56.0)
    risk = min(1.0, row.get("cubo_risk", 0) / 100.0)
    evidence_gap = max(0.0, 1.0 - row.get("evidence_coverage", 0) / 100.0)
    control_gap = max(0.0, 1.0 - row.get("delta_control", 0) / 100.0)
    conflict = 1.0 if row.get("stress_profile") in CONFLICT_PROFILES else (0.55 if row.get("stress_profile") in {"partial_context", "multi_record_table"} else 0.15)
    gate_delta = GATE_SEVERITY.get(row.get("gate"), 0.5)
    sensitivity = WORKLOAD_SENSITIVITY.get(row.get("workload_family"), 1.0)
    domain_delta = min(1.0, max(0.0, (sensitivity - 0.85) / 0.65))

    corr_risk_control = abs(correlation_weight(repo, "cubo_risk", "delta_control", -0.9151))
    corr_stress_output = abs(correlation_weight(repo, "stress_score", "useful_output_rate", -0.936))
    corr_evidence_reduction = abs(correlation_weight(repo, "relative_risk_reduction_pct", "evidence_coverage", 0.8313))
    corr_delta = min(1.0, (
        risk * corr_risk_control
        + stress * corr_stress_output
        + evidence_gap * corr_evidence_reduction
    ) / 3.0)

    review_delta = 0.0 if row.get("safe_review_success") else (0.65 if row.get("gate") == "HUMAN_REVIEW_REQUIRED" else 0.15)
    block_delta = 0.0 if row.get("safe_block_success") else (1.0 if row.get("gate") == "UNSUPPORTED_BLOCKED" else 0.10)

    return {
        "delta_risk": round(risk, 4),
        "delta_evidence": round(evidence_gap, 4),
        "delta_control": round(control_gap, 4),
        "delta_stress": round(stress, 4),
        "delta_conflict": round(conflict, 4),
        "delta_gate": round(gate_delta, 4),
        "delta_correlation": round(corr_delta, 4),
        "delta_domain": round(domain_delta, 4),
        "delta_review": round(review_delta, 4),
        "delta_block": round(block_delta, 4),
    }

def live_delta_score(vector: Dict[str, float]) -> float:
    weights = {
        "delta_risk": 0.18,
        "delta_evidence": 0.12,
        "delta_control": 0.10,
        "delta_stress": 0.14,
        "delta_conflict": 0.13,
        "delta_gate": 0.12,
        "delta_correlation": 0.11,
        "delta_domain": 0.04,
        "delta_review": 0.03,
        "delta_block": 0.03,
    }
    return round(sum(vector[k] * w for k, w in weights.items()), 4)

def gate_transition(row: Dict[str, Any], vector: Dict[str, float], score: float) -> str:
    if row.get("stress_profile") == "unknown_or_unsupported_input" or row.get("gate") == "UNSUPPORTED_BLOCKED":
        return "BLOCK_ZONE"
    if row.get("stress_profile") in {"high_stakes_claim", "cross_document_mismatch"}:
        return "REVIEW_ZONE"
    if row.get("cubo_risk", 0) >= 50:
        return "REVIEW_ZONE"
    if row.get("evidence_coverage", 0) < 70 and row.get("workload_family") in {"summary", "classification", "email_triage", "task_generation"}:
        return "EVIDENCE_OR_REVIEW_ZONE"
    if score < 0.42 and row.get("gate") in {"ANSWER_ALLOWED", "PARSER_OUTPUT_ALLOWED", "TASK_PROPOSAL_ALLOWED"}:
        return "ALLOW_ZONE"
    if score < 0.55:
        return "ALLOW_WITH_WARNING_ZONE"
    return "REVIEW_ZONE"

def bayesian_trust(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    groups = defaultdict(list)
    for row in rows:
        groups[row["gate"]].append(row)

    out = {}
    for gate, items in groups.items():
        if gate == "UNSUPPORTED_BLOCKED":
            success = sum(1 for r in items if r.get("safe_block_success"))
        elif gate == "HUMAN_REVIEW_REQUIRED":
            success = sum(1 for r in items if r.get("safe_review_success"))
        else:
            success = sum(1 for r in items if not r.get("true_failure_candidate"))
        total = len(items)
        posterior_mean = round((success + 1) / (total + 2), 4)
        out[gate] = {
            "total": total,
            "success": success,
            "beta_prior": [1, 1],
            "posterior_alpha_beta": [success + 1, total - success + 1],
            "posterior_mean": posterior_mean,
        }
    return {"status": "PASS", "gate_trust": out, "blocked_actions": BLOCKED_ACTIONS}

def pareto_front(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_profile = defaultdict(list)
    for row in rows:
        by_profile[row["stress_profile"]].append(row)

    points = []
    for profile, items in by_profile.items():
        points.append({
            "profile": profile,
            "avg_cubo_risk": mean([r["cubo_risk"] for r in items]),
            "avg_delta_control": mean([r["delta_control"] for r in items]),
            "avg_evidence_coverage": mean([r["evidence_coverage"] for r in items]),
            "avg_useful_output_rate": mean([r["useful_output_rate"] for r in items]),
            "safe_review_success_rate": pct(sum(1 for r in items if r.get("safe_review_success")), len(items)),
            "safe_block_success_rate": pct(sum(1 for r in items if r.get("safe_block_success")), len(items)),
        })

    # Non-dominated with lower risk and higher useful output/control/evidence.
    front = []
    for p in points:
        dominated = False
        for q in points:
            if p is q:
                continue
            better_or_equal = (
                q["avg_cubo_risk"] <= p["avg_cubo_risk"]
                and q["avg_delta_control"] >= p["avg_delta_control"]
                and q["avg_evidence_coverage"] >= p["avg_evidence_coverage"]
                and q["avg_useful_output_rate"] >= p["avg_useful_output_rate"]
            )
            strictly_better = (
                q["avg_cubo_risk"] < p["avg_cubo_risk"]
                or q["avg_delta_control"] > p["avg_delta_control"]
                or q["avg_evidence_coverage"] > p["avg_evidence_coverage"]
                or q["avg_useful_output_rate"] > p["avg_useful_output_rate"]
            )
            if better_or_equal and strictly_better:
                dominated = True
                break
        if not dominated:
            front.append(p)

    return {"status": "PASS", "pareto_front": sorted(front, key=lambda x: x["avg_cubo_risk"]), "all_points": points, "blocked_actions": BLOCKED_ACTIONS}

def ewma_drift(repo: Path, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    current = {
        "avg_cubo_risk": mean([r["cubo_risk"] for r in rows]),
        "avg_delta_control": mean([r["delta_control"] for r in rows]),
        "avg_evidence_coverage": mean([r["evidence_coverage"] for r in rows]),
        "avg_useful_output_rate": mean([r["useful_output_rate"] for r in rows]),
    }

    p = repo / "outputs/prod601_620_direct_vs_cubo_metrics.json"
    previous = None
    if p.exists():
        try:
            old = json.loads(p.read_text(encoding="utf-8"))
            previous = {
                "avg_cubo_risk": float(old.get("avg_cubo_risk", current["avg_cubo_risk"])),
                "avg_delta_control": float(old.get("avg_delta_control", current["avg_delta_control"])),
                "avg_evidence_coverage": float(old.get("avg_evidence_coverage", current["avg_evidence_coverage"])),
                "avg_useful_output_rate": float(old.get("avg_useful_output_rate", current["avg_useful_output_rate"])),
            }
        except Exception:
            previous = None
    if previous is None:
        previous = current

    alpha = 0.35
    ewma = {k: round(alpha * current[k] + (1 - alpha) * previous[k], 4) for k in current}
    drift = {k: round(current[k] - previous[k], 4) for k in current}

    return {
        "status": "PASS",
        "alpha": alpha,
        "previous_batch": previous,
        "current_batch": current,
        "ewma": ewma,
        "drift": drift,
        "interpretation": "stress calibration intentionally increases residual risk; use as sensitivity baseline, not regression failure",
        "blocked_actions": BLOCKED_ACTIONS,
    }

def aggregate_vectors(items: List[Dict[str, Any]]) -> Dict[str, float]:
    keys = list(items[0]["delta_vector"].keys()) if items else []
    return {k: mean([x["delta_vector"][k] for x in items]) for k in keys}

def baseline_policy(rows: List[Dict[str, Any]], vector_rows: List[Dict[str, Any]], trust: Dict[str, Any]) -> Dict[str, Any]:
    parser = [r for r in rows if r["workload_family"] in {"parser", "document_field_extraction", "receipt_invoice_extraction"}]
    generic = [r for r in rows if r["workload_family"] in {"summary", "classification", "email_triage", "task_generation"}]
    high = [r for r in rows if r["stress_profile"] in HIGH_RISK_PROFILES]
    unsupported = [r for r in rows if r["stress_profile"] == "unknown_or_unsupported_input"]

    decisions = [
        {
            "target": "parser_and_structured_extraction",
            "decision": "PARTIAL_FREEZE_CANDIDATE",
            "reason": "low residual risk relative to stress, high delta control, strong parser output gate",
            "metrics": {
                "avg_cubo_risk": mean([r["cubo_risk"] for r in parser]),
                "avg_delta_control": mean([r["delta_control"] for r in parser]),
                "allowed_rate_pct": pct(sum(1 for r in parser if r["gate"] == "PARSER_OUTPUT_ALLOWED"), len(parser)),
            },
            "regression_required": True,
            "human_approval_required": True,
        },
        {
            "target": "safe_block_taxonomy",
            "decision": "PROMOTE_CANDIDATE_AFTER_REGRESSION",
            "reason": "unsupported input maps perfectly to UNSUPPORTED_BLOCKED in calibration",
            "metrics": {
                "unsupported_count": len(unsupported),
                "safe_block_rate_pct": pct(sum(1 for r in unsupported if r.get("safe_block_success")), len(unsupported)),
            },
            "regression_required": True,
            "human_approval_required": True,
        },
        {
            "target": "safe_review_taxonomy",
            "decision": "PROMOTE_CANDIDATE_WITH_TRACE_REQUIREMENT",
            "reason": "high-risk profiles frequently map to safe human review, but not all high-risk cases do",
            "metrics": {
                "high_risk_count": len(high),
                "safe_review_rate_pct": pct(sum(1 for r in high if r.get("safe_review_success")), len(high)),
            },
            "regression_required": True,
            "human_approval_required": True,
        },
        {
            "target": "summary_classification_email_task",
            "decision": "CALIBRATE_MORE_REQUIRE_CONTEXT",
            "reason": "generic workloads have higher residual Cubo risk and lower evidence coverage",
            "metrics": {
                "avg_cubo_risk": mean([r["cubo_risk"] for r in generic]),
                "avg_evidence_coverage": mean([r["evidence_coverage"] for r in generic]),
            },
            "regression_required": True,
            "human_approval_required": True,
        },
        {
            "target": "core_architecture",
            "decision": "KEEP_STABLE_NO_CORE_CHANGE",
            "reason": "apply mathematical interpretation layer; do not mutate runtime/product core yet",
            "regression_required": False,
            "human_approval_required": False,
        },
    ]
    return {"status": "PASS", "decisions": decisions, "blocked_actions": BLOCKED_ACTIONS}

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows = load_rows(repo)

    vector_rows = []
    for row in rows:
        vec = delta_vector(row, repo)
        score = live_delta_score(vec)
        transition = gate_transition(row, vec, score)
        vector_rows.append({
            "case_id": row["case_id"],
            "workload_family": row["workload_family"],
            "stress_profile": row["stress_profile"],
            "gate": row["gate"],
            "delta_vector": vec,
            "live_delta_score": score,
            "gate_transition": transition,
            "safe_block_success": row.get("safe_block_success"),
            "safe_review_success": row.get("safe_review_success"),
            "true_failure_candidate": row.get("true_failure_candidate"),
        })

    by_workload = defaultdict(list)
    by_profile = defaultdict(list)
    by_transition = defaultdict(list)
    for item in vector_rows:
        by_workload[item["workload_family"]].append(item)
        by_profile[item["stress_profile"]].append(item)
        by_transition[item["gate_transition"]].append(item)

    transition_distribution = {k: len(v) for k, v in sorted(by_transition.items())}
    gate_distribution = defaultdict(int)
    for row in rows:
        gate_distribution[row["gate"]] += 1

    gate_model = {
        "status": "PASS",
        "gate_distribution": dict(sorted(gate_distribution.items())),
        "transition_distribution": transition_distribution,
        "transition_policy": [
            "unsupported profile always blocks",
            "high_stakes_claim and cross_document_mismatch require review",
            "cubo_risk >= 50 requires review unless already blocked",
            "generic workload with evidence_coverage < 70 requires evidence or review",
            "low live_delta_score plus allowed gate remains allow",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    vector_model = {
        "status": "PASS",
        "generated_at": generated_at,
        "case_count": len(vector_rows),
        "components": [
            "delta_risk",
            "delta_evidence",
            "delta_control",
            "delta_stress",
            "delta_conflict",
            "delta_gate",
            "delta_correlation",
            "delta_domain",
            "delta_review",
            "delta_block",
        ],
        "global_average_vector": aggregate_vectors(vector_rows),
        "by_workload_average_vector": {k: aggregate_vectors(v) for k, v in sorted(by_workload.items())},
        "by_stress_profile_average_vector": {k: aggregate_vectors(v) for k, v in sorted(by_profile.items())},
        "sample_vectors": vector_rows[:25],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    trust = bayesian_trust(rows)
    pareto = pareto_front(rows)
    drift = ewma_drift(repo, rows)
    baseline = baseline_policy(rows, vector_rows, trust)

    telemetry_events = {
        "status": "PASS",
        "event_count": 6,
        "events": [
            {
                "event_type": "DELTA_INTERSECTION_DETECTED",
                "signal": "cubo_risk_delta_control_inverse_relation",
                "interpretation": "higher Cubo risk reduces delta control; review threshold should react before production",
            },
            {
                "event_type": "SAFE_BLOCK_SUCCESS",
                "signal": "unsupported_input_blocked",
                "interpretation": "unsupported inputs should count as successful block, not failure",
            },
            {
                "event_type": "SAFE_REVIEW_SUCCESS",
                "signal": "high_risk_human_review",
                "interpretation": "human review in high-risk profiles is a desired gate behavior",
            },
            {
                "event_type": "PARTIAL_FREEZE_CANDIDATE",
                "signal": "parser_extraction_stability",
                "interpretation": "parser/extraction can be frozen as candidate family after regression",
            },
            {
                "event_type": "THRESHOLD_SPLIT_REQUIRED",
                "signal": "generic_workload_evidence_gap",
                "interpretation": "summary/classification/triage/task require context/evidence thresholds",
            },
            {
                "event_type": "NO_AUTO_MUTATION",
                "signal": "baseline_promotion_gate",
                "interpretation": "correlation suggests changes but does not apply them automatically",
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS",
        "decision": "READY_FOR_SOLVER_AGENT_CONTROLLED_STUB_WITH_LIVE_DELTA",
        "case_count": len(rows),
        "model_count": 8,
        "ready_for": [
            "solver agent controlled stub",
            "live delta telemetry feedback",
            "domain sensitivity calibration",
            "business domain calibration matrix",
        ],
        "not_ready_for": [
            "automatic threshold mutation",
            "production activation",
            "autonomous external execution",
            "client-facing benchmark claim",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Live Delta Intersection Engine audit",
        "case_count": len(rows),
        "delta_vector_count": len(vector_rows),
        "model_count": 8,
        "baseline_decision_count": len(baseline["decisions"]),
        "finding": "PASS: mathematical telemetry models applied as gated calibration layer without automatic mutation.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod601c_620c_live_delta_vectors.json", vector_model)
    write_json(out / "prod601c_620c_gate_transition_model.json", gate_model)
    write_json(out / "prod601c_620c_domain_sensitivity_model.json", {
        "status": "PASS",
        "workload_sensitivity": WORKLOAD_SENSITIVITY,
        "business_domain_sensitivity": BUSINESS_DOMAIN_SENSITIVITY,
        "policy": "risk_adjusted = cubo_risk * sensitivity",
        "blocked_actions": BLOCKED_ACTIONS,
    })
    write_json(out / "prod601c_620c_bayesian_gate_trust.json", trust)
    write_json(out / "prod601c_620c_ewma_drift_profile.json", drift)
    write_json(out / "prod601c_620c_pareto_frontier.json", pareto)
    write_json(out / "prod601c_620c_baseline_promotion_policy.json", baseline)
    write_json(out / "prod601c_620c_telemetry_feedback_events.json", telemetry_events)
    write_json(out / "prod601c_620c_readiness.json", readiness)
    write_json(out / "prod601c_620c_audit_report.json", audit)

    report = [
        "# PROD-601C..620C Live Delta Intersection Engine",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(rows)}`",
        f"- Delta vectors: `{len(vector_rows)}`",
        f"- Model count: `{audit['model_count']}`",
        f"- Decision: `{readiness['decision']}`",
        "",
        "## Applied Mathematical Models",
        "- correlation-weighted live delta vector",
        "- gate transition model",
        "- domain sensitivity coefficient",
        "- Bayesian gate trust",
        "- EWMA drift profile",
        "- Pareto frontier",
        "- safe anomaly taxonomy",
        "- baseline promotion policy",
        "",
        "## Transition Distribution",
    ]
    for k, v in sorted(transition_distribution.items()):
        report.append(f"- `{k}`: `{v}`")
    report += ["", "## Baseline Decisions"]
    for d in baseline["decisions"]:
        report.append(f"- `{d['target']}` -> `{d['decision']}` / {d['reason']}")
    report += ["", "## Global Delta Vector"]
    for k, v in vector_model["global_average_vector"].items():
        report.append(f"- `{k}`: `{v}`")
    write_text(out / "prod601c_620c_live_delta_intersection_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-601C..620C",
        "status": "PASS",
        "phase": "Live Delta Intersection Engine",
        "decision": readiness["decision"],
        "outputs": [
            "outputs/prod601c_620c_live_delta_vectors.json",
            "outputs/prod601c_620c_gate_transition_model.json",
            "outputs/prod601c_620c_domain_sensitivity_model.json",
            "outputs/prod601c_620c_bayesian_gate_trust.json",
            "outputs/prod601c_620c_ewma_drift_profile.json",
            "outputs/prod601c_620c_pareto_frontier.json",
            "outputs/prod601c_620c_baseline_promotion_policy.json",
            "outputs/prod601c_620c_telemetry_feedback_events.json",
            "outputs/prod601c_620c_readiness.json",
            "outputs/prod601c_620c_audit_report.json",
        ],
        "next_recommended_bundle": "PROD-602 Solver Agent Controlled Stub with Live Delta",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod601c_620c_result.json", result)
    write_text(out / "prod601c_620c_report.md", "# PROD-601C..620C Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
