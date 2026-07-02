#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]

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
    "neo4j_delete",
    "neo4j_reimport",
    "docker_volume_delete",
    "micrograph_runtime_claim",
    "delta_matrix_runtime_claim",
    "state_family_runtime_claim",
    "multi_llm_braid_runtime_claim",
    "invented_agent_concept_claim",
    "cockpit_as_primary_system_claim",
    "agent_as_primary_system_claim",
    "threshold_lock_claim",
]

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

services = load_module("operational_services", "product/services/operational_services.py")

def load_cases() -> List[Dict[str, Any]]:
    suite = read_json("product/calibration_loop/business_case_suite_v0_1.json", {})
    if suite.get("cases"):
        return suite["cases"]
    base = read_json("product/services/common_business_cases_v0_1.json", {})
    return base.get("cases", [])

def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    case_id = case.get("case_id", "COMMON-COMPANY-UNKNOWN")
    message = case.get("message", "")
    diagnostic = services.diagnostic_service(message, case_id)
    monitoring = services.monitoring_service(message, case_id)
    solutions = services.solutions_service(message, case_id)
    calibration = services.calibration_service(message, case_id)
    scores = diagnostic.get("scores", {})
    return {
        "case_id": case_id,
        "title": case.get("title"),
        "status": "PASS_INTERNAL_DRAFT",
        "diagnostic": diagnostic,
        "monitoring": monitoring,
        "solutions": solutions,
        "calibration": calibration,
        "score_snapshot": scores,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

def summarize_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    def avg(key: str) -> float:
        vals = [r.get("score_snapshot", {}).get(key) for r in runs if isinstance(r.get("score_snapshot", {}).get(key), (int, float))]
        return round(mean(vals), 4) if vals else 0.0

    risk_flags = []
    for r in runs:
        if r.get("score_snapshot", {}).get("ohri", 0) >= 0.25:
            risk_flags.append({"case_id": r.get("case_id"), "risk": "ohri_above_initial_internal_threshold"})
        if r.get("score_snapshot", {}).get("delta_estado", 0) >= 0.20:
            risk_flags.append({"case_id": r.get("case_id"), "risk": "delta_estado_above_initial_internal_threshold"})

    return {
        "case_count": len(runs),
        "avg_oqi": avg("oqi"),
        "avg_ohri": avg("ohri"),
        "avg_zpi": avg("zpi"),
        "avg_delta_estado": avg("delta_estado"),
        "risk_flags": risk_flags,
        "threshold_lock_ready": False,
        "method_canonization_ready_for_draft": True,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

def run_controlled_loop(max_cases: int | None = None) -> Dict[str, Any]:
    cases = load_cases()
    if max_cases is not None:
        cases = cases[:max_cases]
    runs = [run_case(c) for c in cases]
    summary = summarize_runs(runs)
    return {
        "version": "controlled_business_case_calibration_loop.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_INTERNAL_CONTROLLED_LOOP",
        "phase": "PROD-8461..8500",
        "mode": "INTERNAL_CONTROLLED_CASE_CALIBRATION",
        "runs": runs,
        "summary": summary,
        "blocked_actions": BLOCKED_ACTIONS,
        "next": "PROD-8501..8540 - CASULO Methodology Canonization and Data Mapping Playbook",
    }

def build_report_markdown(result: Dict[str, Any]) -> str:
    s = result.get("summary", {})
    lines = [
        "# Controlled Business Case Calibration Loop Report",
        "",
        f"Status: {result.get('status')}",
        f"Phase: {result.get('phase')}",
        "",
        "## Summary",
        "",
        f"- Cases: {s.get('case_count')}",
        f"- avg OQI: {s.get('avg_oqi')}",
        f"- avg OHRI: {s.get('avg_ohri')}",
        f"- avg ZPI: {s.get('avg_zpi')}",
        f"- avg Delta Estado: {s.get('avg_delta_estado')}",
        f"- threshold_lock_ready: {s.get('threshold_lock_ready')}",
        f"- method_canonization_ready_for_draft: {s.get('method_canonization_ready_for_draft')}",
        "",
        "## Case Runs",
        "",
    ]
    for r in result.get("runs", []):
        scores = r.get("score_snapshot", {})
        lines.extend([
            f"### {r.get('case_id')} - {r.get('title')}",
            "",
            f"- status: {r.get('status')}",
            f"- OQI: {scores.get('oqi')}",
            f"- OHRI: {scores.get('ohri')}",
            f"- ZPI: {scores.get('zpi')}",
            f"- Delta Estado: {scores.get('delta_estado')}",
            "- client claim: false",
            "- production: false",
            "",
        ])
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    print(json.dumps(run_controlled_loop(), indent=2, ensure_ascii=False))
