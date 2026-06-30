#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2741..2780"
REQ_TAG = "product-exocortex-runtime-snapshot-evaluator-v0.1"

EVAL_OUT = ROOT / "outputs/prod2701_2740_exocortex_runtime_snapshot_evaluator.json"
EVALUATOR = ROOT / "product/memory/exocortex_runtime_snapshot_evaluator_v0_1.json"

DOC = ROOT / "docs/product/570_EXOCORTEX_DECISION_POLICY_MATRIX.md"
CONTRACT = ROOT / "product/contracts/exocortex_decision_policy_matrix.contract.json"
SCHEMA = ROOT / "product/schemas/exocortex_decision_policy_matrix.schema.json"
MATRIX = ROOT / "product/memory/exocortex_decision_policy_matrix_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2741_2780_exocortex_decision_policy_matrix.json"
OUT_MD = ROOT / "outputs/prod2741_2780_exocortex_decision_policy_matrix.md"

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "validated_performance_claim",
    "real_world_token_savings_claim",
    "client_facing_claim",
    "production_activation",
    "gpt_memory_api_execution"
]

POLICIES = [
    {
        "verdict": "SNAPSHOT_READY",
        "decision": "ALLOW_MANUAL_SNAPSHOT_COMPRESSION",
        "allowed_actions": ["create_manual_snapshot", "archive_heavy_context_pointer"],
        "blocked_actions": BLOCKED,
        "value_delta_effect": "positive_context_compression_candidate",
        "input_quality_dependency": "medium"
    },
    {
        "verdict": "ARCHIVE_READY",
        "decision": "ALLOW_ARCHIVE_TO_REPO",
        "allowed_actions": ["archive_to_repo", "preserve_evidence_pointer"],
        "blocked_actions": BLOCKED,
        "value_delta_effect": "positive_auditability_and_context_reduction_candidate",
        "input_quality_dependency": "medium"
    },
    {
        "verdict": "DISCARD_ALLOWED_AFTER_REVIEW",
        "decision": "HOLD_BEFORE_DISCARD",
        "allowed_actions": ["manual_review", "discard_ephemeral_after_review"],
        "blocked_actions": BLOCKED,
        "value_delta_effect": "possible_token_waste_reduction_after_review",
        "input_quality_dependency": "high"
    },
    {
        "verdict": "HOLD_REVIEW_REQUIRED",
        "decision": "BLOCK_AND_REQUIRE_REVIEW",
        "allowed_actions": ["human_review", "contradiction_resolution", "state_reconciliation"],
        "blocked_actions": BLOCKED,
        "value_delta_effect": "risk_avoidance_candidate",
        "input_quality_dependency": "high"
    },
    {
        "verdict": "REVIEW_REQUIRED",
        "decision": "BLOCK_AND_REQUIRE_REVIEW",
        "allowed_actions": ["human_review", "state_reconciliation"],
        "blocked_actions": BLOCKED,
        "value_delta_effect": "risk_avoidance_candidate",
        "input_quality_dependency": "high"
    },
    {
        "verdict": "PROTECTED_STATE",
        "decision": "PROTECT_DO_NOT_DELETE",
        "allowed_actions": ["protect_canonical_decision", "preserve_state_pointer"],
        "blocked_actions": BLOCKED,
        "value_delta_effect": "decision_loss_avoidance_candidate",
        "input_quality_dependency": "medium"
    }
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

def main():
    errors = []
    eval_out = read_json(EVAL_OUT) if EVAL_OUT.exists() else {}
    evaluator = read_json(EVALUATOR) if EVALUATOR.exists() else {}
    evaluations = evaluator.get("evaluations", [])
    observed_verdicts = set(eval_out.get("verdicts", []))
    policy_by_verdict = {p["verdict"]: p for p in POLICIES}

    decisions = []
    for e in evaluations:
        verdict = e.get("verdict")
        policy = policy_by_verdict.get(verdict)
        if not policy:
            errors.append("missing policy for verdict: " + str(verdict))
            continue
        decisions.append({
            "snapshot_id": e.get("snapshot_id"),
            "title": e.get("title"),
            "verdict": verdict,
            "risk": e.get("risk"),
            "gate": e.get("gate"),
            "priority_score": e.get("priority_score"),
            "policy_decision": policy["decision"],
            "allowed_actions": policy["allowed_actions"],
            "blocked_actions": policy["blocked_actions"],
            "value_delta_effect": policy["value_delta_effect"],
            "input_quality_dependency": policy["input_quality_dependency"]
        })

    matrix = {
        "version": "exocortex_decision_policy_matrix.v0.1",
        "phase": PHASE,
        "purpose": "Map Exocortex runtime snapshot evaluator verdicts to governed operational decisions.",
        "policies": POLICIES,
        "runtime_decisions": decisions,
        "future_phases": [
            "PROD-2781..2820 - Prompt and Input Data Quality Gate",
            "PROD-2821..2860 - Exocortex Value Delta Engine Contract"
        ],
        "recommended_next_phase": "PROD-2781..2820 - Prompt and Input Data Quality Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "decision_policy_matrix",
        "blocked_actions": BLOCKED,
        "recommended_next_phase": matrix["recommended_next_phase"],
        "future_value_delta_phase": "PROD-2821..2860 - Exocortex Value Delta Engine Contract"
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Decision Policy Matrix",
        "type": "object",
        "required": ["version", "phase", "policies", "runtime_decisions"]
    }

    doc = """# PROD-2741..2780 - Exocortex Decision Policy Matrix

Maps Exocortex runtime snapshot verdicts to operational policy decisions.

The matrix connects snapshot evaluation to lifecycle action, review requirement, value-delta effect and input-quality dependency.

Boundary: policy matrix only. No automatic memory deletion, no real memory mutation, no production and no client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(MATRIX, matrix)

    policy_verdicts = set(policy_by_verdict.keys())
    decisions_by_verdict = {d["verdict"] for d in decisions}

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "eval_output_exists": EVAL_OUT.exists(),
        "eval_output_pass": eval_out.get("status") == "PASS",
        "evaluator_exists": EVALUATOR.exists(),
        "policy_count": len(POLICIES),
        "runtime_decision_count": len(decisions),
        "observed_verdict_count": len(observed_verdicts),
        "all_observed_verdicts_have_policy": observed_verdicts.issubset(policy_verdicts),
        "has_snapshot_ready_policy": "SNAPSHOT_READY" in policy_verdicts,
        "has_archive_ready_policy": "ARCHIVE_READY" in policy_verdicts,
        "has_discard_policy": "DISCARD_ALLOWED_AFTER_REVIEW" in policy_verdicts,
        "has_hold_policy": "HOLD_REVIEW_REQUIRED" in policy_verdicts,
        "has_protected_policy": "PROTECTED_STATE" in policy_verdicts,
        "decisions_cover_snapshots": len(decisions) == len(evaluations),
        "all_decisions_have_blocked_actions": all(set(BLOCKED).issubset(set(d["blocked_actions"])) for d in decisions),
        "all_decisions_have_value_delta_effect": all(d.get("value_delta_effect") for d in decisions),
        "all_decisions_have_input_quality_dependency": all(d.get("input_quality_dependency") for d in decisions),
        "future_input_quality_gate_registered": "PROD-2781..2820 - Prompt and Input Data Quality Gate" in matrix["future_phases"],
        "future_value_delta_registered": "PROD-2821..2860 - Exocortex Value Delta Engine Contract" in matrix["future_phases"],
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED,
        "client_claim_blocked": "client_facing_claim" in BLOCKED,
        "production_blocked": "production_activation" in BLOCKED
    }

    if checks["policy_count"] < 6:
        errors.append("policy_count below 6")
    if checks["runtime_decision_count"] < 6:
        errors.append("runtime_decision_count below 6")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXOCORTEX_DECISION_POLICY_MATRIX_READY" if status == "PASS" else "EXOCORTEX_DECISION_POLICY_MATRIX_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matrix": "product/memory/exocortex_decision_policy_matrix_v0_1.json",
        "policy_count": len(POLICIES),
        "runtime_decision_count": len(decisions),
        "recommended_next_phase": matrix["recommended_next_phase"],
        "future_phases": matrix["future_phases"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2741..2780 Exocortex Decision Policy Matrix",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Policies: `{len(POLICIES)}`",
        f"- Runtime decisions: `{len(decisions)}`",
        f"- Next: `{matrix['recommended_next_phase']}`",
        "",
        "## Decisions"
    ]
    for d in decisions:
        report.append(f"- `{d['snapshot_id']}` `{d['verdict']}` -> `{d['policy_decision']}`")
    report += ["", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("policies:", len(POLICIES))
    print("runtime_decisions:", len(decisions))
    print("next:", matrix["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
