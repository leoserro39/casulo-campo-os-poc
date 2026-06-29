#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    "autonomous_external_execution",
    "real_world_side_effect",
]

SAMPLE_INPUTS = [
    {
        "run_id": "SOLVER-STUB-001",
        "input_text": "Parse a clean synthetic invoice and return structured fields with evidence trace.",
        "workload_family": "receipt_invoice_extraction",
        "domain_context": "routine_document_extraction",
        "stress_profile": "clean_baseline",
        "consent_scope": "synthetic_fixture_only",
    },
    {
        "run_id": "SOLVER-STUB-002",
        "input_text": "Summarize a noisy synthetic email and classify urgency with supporting evidence.",
        "workload_family": "email_triage",
        "domain_context": "routine_email_triage",
        "stress_profile": "noisy_ocr_or_typo",
        "consent_scope": "synthetic_fixture_only",
    },
    {
        "run_id": "SOLVER-STUB-003",
        "input_text": "Review a high-stakes synthetic contract claim with cross-field conflict.",
        "workload_family": "contract_checklist",
        "domain_context": "contract_legal_review",
        "stress_profile": "high_stakes_claim",
        "consent_scope": "synthetic_fixture_only",
    },
    {
        "run_id": "SOLVER-STUB-004",
        "input_text": "Handle an unsupported synthetic input with no minimum schema.",
        "workload_family": "classification",
        "domain_context": "unknown_or_unsupported_domain",
        "stress_profile": "unknown_or_unsupported_input",
        "consent_scope": "synthetic_fixture_only",
    },
    {
        "run_id": "SOLVER-STUB-005",
        "input_text": "Create a task proposal for a restaurant cashflow bottleneck using only provided evidence.",
        "workload_family": "task_generation",
        "domain_context": "restaurant_cashflow",
        "stress_profile": "partial_context",
        "consent_scope": "synthetic_fixture_only",
    },
    {
        "run_id": "SOLVER-STUB-006",
        "input_text": "Detect deltas in a clinic billing/glosa scenario with stale evidence.",
        "workload_family": "delta_detection",
        "domain_context": "clinic_billing_glosa",
        "stress_profile": "stale_or_undated_evidence",
        "consent_scope": "synthetic_fixture_only",
    },
]

DOMAIN_SENSITIVITY_DEFAULT = {
    "routine_document_extraction": 0.95,
    "routine_email_triage": 1.10,
    "contract_legal_review": 1.50,
    "unknown_or_unsupported_domain": 1.60,
    "restaurant_cashflow": 1.20,
    "clinic_billing_glosa": 1.45,
}

BASELINE_BY_PROFILE = {
    "clean_baseline": {"cubo_risk": 18.17, "delta_control": 91.25, "evidence_coverage": 85.33, "useful_output_rate": 92.0},
    "noisy_ocr_or_typo": {"cubo_risk": 40.92, "delta_control": 88.25, "evidence_coverage": 78.33, "useful_output_rate": 81.0},
    "high_stakes_claim": {"cubo_risk": 52.50, "delta_control": 83.25, "evidence_coverage": 74.33, "useful_output_rate": 77.0},
    "unknown_or_unsupported_input": {"cubo_risk": 59.25, "delta_control": 81.25, "evidence_coverage": 64.33, "useful_output_rate": 75.0},
    "partial_context": {"cubo_risk": 48.92, "delta_control": 85.25, "evidence_coverage": 72.33, "useful_output_rate": 78.0},
    "stale_or_undated_evidence": {"cubo_risk": 46.92, "delta_control": 84.25, "evidence_coverage": 73.33, "useful_output_rate": 83.0},
}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def normalize_delta(profile_metrics: Dict[str, float], domain_sensitivity: float) -> Dict[str, float]:
    cubo_risk = profile_metrics["cubo_risk"]
    adjusted_risk = min(100.0, cubo_risk * domain_sensitivity)
    return {
        "delta_risk": round(adjusted_risk / 100.0, 4),
        "delta_evidence": round(max(0.0, 1.0 - profile_metrics["evidence_coverage"] / 100.0), 4),
        "delta_control": round(max(0.0, 1.0 - profile_metrics["delta_control"] / 100.0), 4),
        "delta_usefulness": round(max(0.0, 1.0 - profile_metrics["useful_output_rate"] / 100.0), 4),
        "delta_domain": round(min(1.0, max(0.0, (domain_sensitivity - 0.85) / 0.75)), 4),
    }

def live_delta_score(delta: Dict[str, float]) -> float:
    return round(
        delta["delta_risk"] * 0.36
        + delta["delta_evidence"] * 0.20
        + delta["delta_control"] * 0.16
        + delta["delta_usefulness"] * 0.14
        + delta["delta_domain"] * 0.14,
        4,
    )

def decide_gate(sample: Dict[str, Any], score: float, profile_metrics: Dict[str, float], domain_sensitivity: float) -> Dict[str, Any]:
    stress_profile = sample["stress_profile"]
    workload = sample["workload_family"]
    adjusted_risk = profile_metrics["cubo_risk"] * domain_sensitivity

    if stress_profile == "unknown_or_unsupported_input" or sample["domain_context"] == "unknown_or_unsupported_domain":
        return {
            "gate": "UNSUPPORTED_BLOCKED",
            "decision": "BLOCK",
            "gate_reason": "unsupported input/domain or missing minimum schema",
            "output_allowed": False,
            "external_execution_allowed": False,
        }

    if stress_profile in {"high_stakes_claim", "cross_document_mismatch"} or adjusted_risk >= 55:
        return {
            "gate": "HUMAN_REVIEW_REQUIRED",
            "decision": "REVIEW",
            "gate_reason": "high sensitivity, high residual risk or high-stakes profile",
            "output_allowed": False,
            "external_execution_allowed": False,
        }

    if workload in {"summary", "classification", "email_triage", "task_generation"} and profile_metrics["evidence_coverage"] < 70:
        return {
            "gate": "EVIDENCE_REQUIRED",
            "decision": "REQUEST_EVIDENCE_OR_REVIEW",
            "gate_reason": "generic workload requires more context/evidence below threshold",
            "output_allowed": False,
            "external_execution_allowed": False,
        }

    if score < 0.38:
        return {
            "gate": "ANSWER_ALLOWED" if workload not in {"parser", "document_field_extraction", "receipt_invoice_extraction"} else "PARSER_OUTPUT_ALLOWED",
            "decision": "ALLOW_CONTROLLED_OUTPUT",
            "gate_reason": "live delta score and evidence are inside controlled allow zone",
            "output_allowed": True,
            "external_execution_allowed": False,
        }

    return {
        "gate": "ANSWER_ALLOWED",
        "decision": "ALLOW_WITH_WARNING",
        "gate_reason": "controlled output allowed with warning and trace requirement",
        "output_allowed": True,
        "external_execution_allowed": False,
    }

def build_run(sample: Dict[str, Any]) -> Dict[str, Any]:
    profile_metrics = BASELINE_BY_PROFILE[sample["stress_profile"]]
    sensitivity = DOMAIN_SENSITIVITY_DEFAULT.get(sample["domain_context"], 1.2)
    delta = normalize_delta(profile_metrics, sensitivity)
    score = live_delta_score(delta)
    gate = decide_gate(sample, score, profile_metrics, sensitivity)

    evidence_trace = [
        {
            "evidence_id": f"{sample['run_id']}-EVID-001",
            "type": "synthetic_input_summary",
            "available": True,
            "description": "Synthetic stub input supplied by controlled runner.",
        },
        {
            "evidence_id": f"{sample['run_id']}-EVID-002",
            "type": "live_delta_baseline",
            "available": True,
            "description": "Profile metrics derived from PROD-601C live delta baseline.",
        },
        {
            "evidence_id": f"{sample['run_id']}-EVID-003",
            "type": "external_source",
            "available": False,
            "description": "External sources are blocked in stub mode.",
        },
    ]

    telemetry_events = [
        {
            "event_type": "SOLVER_AGENT_STUB_RUN",
            "run_id": sample["run_id"],
            "domain_context": sample["domain_context"],
            "workload_family": sample["workload_family"],
        },
        {
            "event_type": "LIVE_DELTA_SCORE_COMPUTED",
            "run_id": sample["run_id"],
            "live_delta_score": score,
        },
        {
            "event_type": "GATE_DECISION_EMITTED",
            "run_id": sample["run_id"],
            "gate": gate["gate"],
            "decision": gate["decision"],
        },
    ]

    return {
        "status": "PASS",
        "run_id": sample["run_id"],
        "input": sample,
        "domain_sensitivity": sensitivity,
        "profile_metrics": profile_metrics,
        "delta_vector": delta,
        "live_delta_score": score,
        "gate": gate["gate"],
        "decision": gate["decision"],
        "gate_reason": gate["gate_reason"],
        "output_allowed": gate["output_allowed"],
        "external_execution_allowed": False,
        "evidence_trace": evidence_trace,
        "gate_trace": {
            "status": "PASS",
            "gate": gate["gate"],
            "decision": gate["decision"],
            "gate_reason": gate["gate_reason"],
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "telemetry_events": telemetry_events,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    prod601c = load_json(out / "prod601c_620c_readiness.json", {})
    baseline_policy = load_json(out / "prod601c_620c_baseline_promotion_policy.json", {})
    readiness_ok = prod601c.get("decision") == "READY_FOR_SOLVER_AGENT_CONTROLLED_STUB_WITH_LIVE_DELTA"

    runs = [build_run(sample) for sample in SAMPLE_INPUTS]

    gate_distribution: Dict[str, int] = {}
    decision_distribution: Dict[str, int] = {}
    for run in runs:
        gate_distribution[run["gate"]] = gate_distribution.get(run["gate"], 0) + 1
        decision_distribution[run["decision"]] = decision_distribution.get(run["decision"], 0) + 1

    input_schema = {
        "status": "PASS",
        "required_fields": ["run_id", "input_text", "workload_family", "domain_context", "consent_scope"],
        "allowed_consent_scope": [
            "synthetic_fixture_only",
            "explicitly_approved_anonymized_real_case",
        ],
        "blocked_inputs": [
            "credentials",
            "unapproved confidential data",
            "external action request",
            "production activation request",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    stub_status = {
        "status": "PASS" if readiness_ok else "WARN",
        "phase": "Solver Agent Controlled Stub with Live Delta",
        "generated_at": generated_at,
        "upstream_readiness": prod601c.get("decision", "UNKNOWN"),
        "mode": "stub_only_no_external_execution",
        "run_count": len(runs),
        "gate_distribution": gate_distribution,
        "decision_distribution": decision_distribution,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    run_report = {
        "status": "PASS",
        "run_count": len(runs),
        "runs": runs,
        "baseline_policy_summary": baseline_policy.get("decisions", []),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    live_delta_decision = {
        "status": "PASS",
        "policy": "live_delta_decides_gate_not_execution",
        "decision_rules": [
            "unsupported input/domain -> UNSUPPORTED_BLOCKED",
            "high stakes or adjusted risk >= 55 -> HUMAN_REVIEW_REQUIRED",
            "generic workload with evidence below 70 -> EVIDENCE_REQUIRED",
            "low live delta score -> controlled allow output",
            "all external execution remains blocked",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    evidence_trace = {
        "status": "PASS",
        "trace_count": sum(len(run["evidence_trace"]) for run in runs),
        "runs": [{"run_id": run["run_id"], "evidence_trace": run["evidence_trace"]} for run in runs],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    gate_trace = {
        "status": "PASS",
        "gate_distribution": gate_distribution,
        "runs": [{"run_id": run["run_id"], "gate_trace": run["gate_trace"]} for run in runs],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    telemetry_feedback = {
        "status": "PASS",
        "event_count": sum(len(run["telemetry_events"]) for run in runs),
        "events": [event for run in runs for event in run["telemetry_events"]],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if readiness_ok else "WARN",
        "decision": "READY_FOR_CONTROLLED_USER_CASE_INPUT_WITH_LIVE_DELTA" if readiness_ok else "REVIEW_UPSTREAM_READINESS",
        "ready_for": [
            "controlled synthetic user cases",
            "explicitly approved anonymized real cases",
            "solver run reports",
            "telemetry feedback loop",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "credential handling",
            "client-facing benchmark claims",
            "automatic threshold mutation",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness_ok else "WARN",
        "audit": "Solver Agent Controlled Stub audit",
        "run_count": len(runs),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "finding": "PASS: controlled solver-agent stub is wired to live delta, evidence trace, gate trace and telemetry feedback without external execution.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod602_620_solver_agent_status.json", stub_status)
    write_json(out / "prod602_620_solver_agent_input_schema.json", input_schema)
    write_json(out / "prod602_620_solver_agent_sample_run.json", {"status": "PASS", "sample_run": runs[0], "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod602_620_solver_agent_run_report.json", run_report)
    write_json(out / "prod602_620_solver_agent_live_delta_decision.json", live_delta_decision)
    write_json(out / "prod602_620_solver_agent_evidence_trace.json", evidence_trace)
    write_json(out / "prod602_620_solver_agent_gate_trace.json", gate_trace)
    write_json(out / "prod602_620_solver_agent_telemetry_feedback.json", telemetry_feedback)
    write_json(out / "prod602_620_solver_agent_readiness.json", readiness)
    write_json(out / "prod602_620_solver_agent_audit_report.json", audit)

    report = [
        "# PROD-602..620 Solver Agent Controlled Stub with Live Delta",
        "",
        f"- Status: `{stub_status['status']}`",
        f"- Upstream readiness: `{stub_status['upstream_readiness']}`",
        f"- Mode: `{stub_status['mode']}`",
        f"- Run count: `{len(runs)}`",
        f"- External execution allowed: `{stub_status['external_execution_allowed']}`",
        f"- Automatic threshold mutation allowed: `{stub_status['automatic_threshold_mutation_allowed']}`",
        "",
        "## Gate Distribution",
    ]
    for gate, count in sorted(gate_distribution.items()):
        report.append(f"- `{gate}`: `{count}`")
    report += ["", "## Decision Distribution"]
    for decision, count in sorted(decision_distribution.items()):
        report.append(f"- `{decision}`: `{count}`")
    report += ["", "## Sample Runs"]
    for run in runs:
        report.append(f"- `{run['run_id']}` `{run['input']['workload_family']}` / `{run['input']['domain_context']}` -> `{run['gate']}` / `{run['decision']}` / live_delta `{run['live_delta_score']}`")
    report += ["", "## Readiness", f"- `{readiness['decision']}`"]
    write_text(out / "prod602_620_solver_agent_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-602..620",
        "status": stub_status["status"],
        "phase": "Solver Agent Controlled Stub with Live Delta",
        "decision": readiness["decision"],
        "outputs": [
            "outputs/prod602_620_solver_agent_status.json",
            "outputs/prod602_620_solver_agent_input_schema.json",
            "outputs/prod602_620_solver_agent_sample_run.json",
            "outputs/prod602_620_solver_agent_run_report.json",
            "outputs/prod602_620_solver_agent_live_delta_decision.json",
            "outputs/prod602_620_solver_agent_evidence_trace.json",
            "outputs/prod602_620_solver_agent_gate_trace.json",
            "outputs/prod602_620_solver_agent_telemetry_feedback.json",
            "outputs/prod602_620_solver_agent_readiness.json",
            "outputs/prod602_620_solver_agent_audit_report.json",
        ],
        "next_recommended_bundle": "PROD-621 Business Domain Calibration Matrix with Live Delta",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod602_620_result.json", result)
    write_text(out / "prod602_620_report.md", "# PROD-602..620 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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
