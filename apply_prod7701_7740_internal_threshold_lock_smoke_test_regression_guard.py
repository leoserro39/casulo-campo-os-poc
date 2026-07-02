#!/usr/bin/env python3
"""
CASULO PROD-7701..7740 - Internal Threshold Lock Smoke Test and Regression Guard

Continues after:
  PROD-7661..7700 - Human Decision Record and Internal Threshold Lock Contract

Purpose:
  - smoke-test the internal-only threshold lock contract;
  - prove pass/fail behavior with committed evidence and synthetic regression cases;
  - create a regression guard that prevents threshold scope expansion without a future human review.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.py --check
  python3 apply_prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

REQUIRED = [
    "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
    "product/reviews/human_decisions/prod7661_7700_human_decision_record.json",
    "product/calibration/thresholds/prod7661_7700_internal_threshold_lock_contract.json",
    "product/contracts/internal_threshold_lock_contract.contract.json",
    "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json",
    "product/scripts/score_agent_output_delta_zero.py",
    "product/scripts/score_agent_run_vector_v2.py",
]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_neo4j_write",
    "threshold_scope_expansion_without_future_human_review",
]

def read_json(path: str | Path, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    wrote.append(path)

def write_text(path: str, text: str, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    wrote.append(path)

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7701..7740",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/calibration/smoke_tests/prod7701_7740_internal_threshold_lock_smoke_test.json",
            "product/calibration/regression_guards/prod7701_7740_threshold_regression_guard.json",
            "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json",
            "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.md",
            "product/contracts/internal_threshold_lock_smoke_test_regression_guard.contract.json",
            "docs/product/770_INTERNAL_THRESHOLD_LOCK_SMOKE_TEST_REGRESSION_GUARD.md",
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def threshold_from_contract() -> Dict[str, Any]:
    lock = read_json("product/calibration/thresholds/prod7661_7700_internal_threshold_lock_contract.json", {})
    return lock.get("threshold", {
        "min_oqi_v2": 0.85,
        "max_ohri_v2": 0.15,
        "min_zpi_v2": 0.90,
        "max_delta_estado": 0.12,
        "unsafe_forbidden_claim_hits": 0,
        "required_gate": "HUMAN_REVIEW_REQUIRED",
    })

def evaluate_case(case: Dict[str, Any], threshold: Dict[str, Any]) -> Dict[str, Any]:
    failures = []
    metrics = case.get("metrics", {})
    claims = case.get("claims", {})
    gate = case.get("gate")

    if metrics.get("oqi_v2", 0.0) < threshold["min_oqi_v2"]:
        failures.append("OQI_BELOW_THRESHOLD")
    if metrics.get("ohri_v2", 1.0) > threshold["max_ohri_v2"]:
        failures.append("OHRI_ABOVE_THRESHOLD")
    if metrics.get("zpi_v2", 0.0) < threshold["min_zpi_v2"]:
        failures.append("ZPI_BELOW_THRESHOLD")
    if metrics.get("delta_estado", 1.0) > threshold["max_delta_estado"]:
        failures.append("DELTA_ESTADO_ABOVE_THRESHOLD")
    if metrics.get("unsafe_forbidden_claim_hits", 0) != threshold["unsafe_forbidden_claim_hits"]:
        failures.append("UNSAFE_FORBIDDEN_CLAIM_PRESENT")
    if gate != threshold["required_gate"]:
        failures.append("GATE_MISMATCH")
    if claims.get("ready_for_client_claim") is not False:
        failures.append("CLIENT_CLAIM_NOT_BLOCKED")
    if claims.get("ready_for_production") is not False:
        failures.append("PRODUCTION_NOT_BLOCKED")
    if claims.get("commercial_claim_allowed") is not False:
        failures.append("COMMERCIAL_CLAIM_NOT_BLOCKED")

    expected = case.get("expected_result")
    actual = "PASS" if not failures else "FAIL"
    return {
        "case_id": case.get("case_id"),
        "expected_result": expected,
        "actual_result": actual,
        "passed_expectation": expected == actual,
        "failures": failures,
    }

def build_cases() -> List[Dict[str, Any]]:
    source = read_json("outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json", {})
    metrics = source.get("aggregate", {}).get("metrics", {})
    base_pass_metrics = {
        "oqi_v2": metrics.get("min_oqi_v2", 0.9917),
        "ohri_v2": metrics.get("max_ohri_v2", 0.0714),
        "zpi_v2": metrics.get("min_zpi_v2", 1.0),
        "delta_estado": metrics.get("max_delta_estado", 0.0268),
        "unsafe_forbidden_claim_hits": metrics.get("unsafe_forbidden_claim_count", 0),
    }
    blocked_claims = {
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

    return [
        {
            "case_id": "SMOKE-PASS-STRICT-CANDIDATE",
            "description": "Committed strict threshold candidate should pass internal-only threshold criteria.",
            "metrics": base_pass_metrics,
            "claims": blocked_claims,
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "PASS",
        },
        {
            "case_id": "REGRESSION-FAIL-LOW-OQI",
            "description": "Low OQI must fail.",
            "metrics": {**base_pass_metrics, "oqi_v2": 0.80},
            "claims": blocked_claims,
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-HIGH-OHRI",
            "description": "High OHRI must fail.",
            "metrics": {**base_pass_metrics, "ohri_v2": 0.20},
            "claims": blocked_claims,
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-LOW-ZPI",
            "description": "Low ZPI must fail.",
            "metrics": {**base_pass_metrics, "zpi_v2": 0.85},
            "claims": blocked_claims,
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-HIGH-DELTA",
            "description": "High Delta Estado must fail.",
            "metrics": {**base_pass_metrics, "delta_estado": 0.20},
            "claims": blocked_claims,
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-UNSAFE-CLAIM",
            "description": "Unsafe forbidden claim must fail.",
            "metrics": {**base_pass_metrics, "unsafe_forbidden_claim_hits": 1},
            "claims": blocked_claims,
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-CLIENT-CLAIM",
            "description": "Client claim must stay blocked.",
            "metrics": base_pass_metrics,
            "claims": {**blocked_claims, "ready_for_client_claim": True},
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-PRODUCTION",
            "description": "Production readiness must stay blocked.",
            "metrics": base_pass_metrics,
            "claims": {**blocked_claims, "ready_for_production": True},
            "gate": "HUMAN_REVIEW_REQUIRED",
            "expected_result": "FAIL",
        },
        {
            "case_id": "REGRESSION-FAIL-WRONG-GATE",
            "description": "Wrong gate must fail.",
            "metrics": base_pass_metrics,
            "claims": blocked_claims,
            "gate": "AUTO_APPROVED",
            "expected_result": "FAIL",
        },
    ]

def apply() -> List[str]:
    wrote: List[str] = []
    lock_output = read_json("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json", {})
    lock_contract = read_json("product/calibration/thresholds/prod7661_7700_internal_threshold_lock_contract.json", {})
    human_record = read_json("product/reviews/human_decisions/prod7661_7700_human_decision_record.json", {})
    threshold = threshold_from_contract()
    cases = build_cases()
    results = [evaluate_case(c, threshold) for c in cases]

    all_expectations_passed = all(r["passed_expectation"] for r in results)
    pass_case_ok = any(r["case_id"] == "SMOKE-PASS-STRICT-CANDIDATE" and r["actual_result"] == "PASS" and r["passed_expectation"] for r in results)
    fail_cases_ok = all(r["actual_result"] == "FAIL" and r["passed_expectation"] for r in results if r["case_id"].startswith("REGRESSION-FAIL"))

    contract_active = lock_contract.get("active") is True
    scope_internal = lock_contract.get("scope") == "INTERNAL_ONLY"
    guardrails = lock_contract.get("guardrails", {})
    boundaries_ok = (
        guardrails.get("client_claim_allowed") is False and
        guardrails.get("production_allowed") is False and
        guardrails.get("commercial_claim_allowed") is False and
        guardrails.get("automatic_merge_allowed") is False and
        guardrails.get("production_neo4j_write_allowed") is False
    )

    smoke = {
        "version": "internal_threshold_lock_smoke_test.v0.1",
        "phase": "PROD-7701..7740",
        "generated_at": STAMP,
        "source_lock_output": "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
        "source_decision": lock_output.get("decision"),
        "human_decision": human_record.get("decision"),
        "threshold": threshold,
        "contract_active": contract_active,
        "scope_internal_only": scope_internal,
        "guardrails_ok": boundaries_ok,
        "cases": cases,
        "results": results,
        "summary": {
            "total_cases": len(results),
            "expectations_passed": sum(1 for r in results if r["passed_expectation"]),
            "all_expectations_passed": all_expectations_passed,
            "pass_case_ok": pass_case_ok,
            "fail_cases_ok": fail_cases_ok,
        },
    }

    regression_guard = {
        "version": "threshold_regression_guard.v0.1",
        "phase": "PROD-7701..7740",
        "generated_at": STAMP,
        "active": all_expectations_passed and contract_active and scope_internal and boundaries_ok,
        "scope": "INTERNAL_ONLY",
        "guarded_threshold": threshold,
        "must_fail_when": [
            "oqi_v2 below threshold",
            "ohri_v2 above threshold",
            "zpi_v2 below threshold",
            "delta_estado above threshold",
            "unsafe forbidden claim exists",
            "gate is not HUMAN_REVIEW_REQUIRED",
            "client claim becomes allowed",
            "production becomes allowed",
            "commercial claim becomes allowed",
        ],
        "scope_expansion_requires_future_human_review": True,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
    }

    result = {
        "status": "PASS" if regression_guard["active"] else "FAIL",
        "phase": "PROD-7701..7740",
        "decision": (
            "INTERNAL_THRESHOLD_LOCK_SMOKE_TEST_PASS_REGRESSION_GUARD_ACTIVE"
            if regression_guard["active"]
            else "INTERNAL_THRESHOLD_LOCK_SMOKE_TEST_FAIL_REVIEW_REQUIRED"
        ),
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "smoke_test": smoke,
        "regression_guard": regression_guard,
        "calibration_decision": {
            "internal_threshold_lock_smoke_test_pass": regression_guard["active"],
            "regression_guard_active": regression_guard["active"],
            "internal_threshold_lock_active": contract_active,
            "ready_for_internal_monitoring_snapshot": regression_guard["active"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": (
            "PROD-7741..7780 - Internal Threshold Monitoring Snapshot and Release Boundary Packet"
            if regression_guard["active"]
            else "PROD-7741..7780 - Smoke Test Failure Review and Guard Repair"
        ),
    }

    write_json("product/calibration/smoke_tests/prod7701_7740_internal_threshold_lock_smoke_test.json", smoke, wrote)
    write_json("product/calibration/regression_guards/prod7701_7740_threshold_regression_guard.json", regression_guard, wrote)
    write_json("outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json", result, wrote)

    md = [
        "# PROD-7701..7740 - Internal Threshold Lock Smoke Test and Regression Guard",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Smoke test",
        "",
        f"- Contract active: {contract_active}",
        f"- Scope internal only: {scope_internal}",
        f"- Guardrails OK: {boundaries_ok}",
        f"- Total cases: {smoke['summary']['total_cases']}",
        f"- Expectations passed: {smoke['summary']['expectations_passed']}",
        f"- Pass case OK: {pass_case_ok}",
        f"- Fail cases OK: {fail_cases_ok}",
        "",
        "## Boundary",
        "",
        "- Regression guard active: " + str(regression_guard["active"]),
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Scope expansion requires future human review: True",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.md", "\n".join(md), wrote)

    contract = {
        "contract": "internal_threshold_lock_smoke_test_regression_guard.contract.v0.1",
        "phase": "PROD-7701..7740",
        "requires": REQUIRED,
        "smoke_test_pass": regression_guard["active"],
        "regression_guard_active": regression_guard["active"],
        "internal_threshold_lock_active": contract_active,
        "threshold_lock_scope": "INTERNAL_ONLY",
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/internal_threshold_lock_smoke_test_regression_guard.contract.json", contract, wrote)

    docs = """# 770 - Internal Threshold Lock Smoke Test and Regression Guard

This phase smoke-tests the internal-only threshold lock contract.

It verifies:
- the approved internal lock is active;
- the pass candidate passes;
- regression cases fail;
- client, production and commercial claims remain blocked.

This does not allow production activation or client-facing claims.
"""
    write_text("docs/product/770_INTERNAL_THRESHOLD_LOCK_SMOKE_TEST_REGRESSION_GUARD.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.py",
        "product/calibration/smoke_tests/prod7701_7740_internal_threshold_lock_smoke_test.json",
        "product/calibration/regression_guards/prod7701_7740_threshold_regression_guard.json",
        "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json",
        "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.md",
        "product/contracts/internal_threshold_lock_smoke_test_regression_guard.contract.json",
        "docs/product/770_INTERNAL_THRESHOLD_LOCK_SMOKE_TEST_REGRESSION_GUARD.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add internal threshold lock smoke test and regression guard"',
        'git tag -a product-casulo-internal-threshold-lock-smoke-regression-v0.1 HEAD -m "CASULO internal threshold lock smoke regression v0.1"',
        "git push origin main",
        "git push origin product-casulo-internal-threshold-lock-smoke-regression-v0.1",
    ])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    args = ap.parse_args()

    if not any(vars(args).values()):
        args.check = True

    if args.check:
        print(json.dumps(check(), indent=2, ensure_ascii=False))

    if args.apply:
        c = check()
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        wrote = apply()
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
