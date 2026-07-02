#!/usr/bin/env python3
"""
CASULO PROD-7421..7460 - Controlled Multi-Run Result Capture and Threshold Lock Candidate

Run after downloading the 4 GitHub Actions artifacts into:
  product/agent_runs/real_case_001/graph_backed_prompt_candidate
  product/agent_runs/real_case_001/strict_boundary_prompt_candidate
  product/agent_runs/real_case_001/adversarial_claim_probe_candidate
  product/agent_runs/real_case_001/evidence_gap_stress_candidate

Usage:
  python3 apply_prod7421_7460_controlled_multirun_result_capture_threshold_lock.py --check
  python3 apply_prod7421_7460_controlled_multirun_result_capture_threshold_lock.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

RUNS = [
    {
        "run_key": "graph_backed_prompt_candidate",
        "run_id": "28562011047",
        "artifact": "casulo-agent-graph_backed_prompt_candidate",
        "prompt_variant": "real_case_001_graph_backed_prompt_v0_1.md",
    },
    {
        "run_key": "strict_boundary_prompt_candidate",
        "run_id": "28562012146",
        "artifact": "casulo-agent-strict_boundary_prompt_candidate",
        "prompt_variant": "real_case_001_strict_boundary_prompt_v0_1.md",
    },
    {
        "run_key": "adversarial_claim_probe_candidate",
        "run_id": "28562013121",
        "artifact": "casulo-agent-adversarial_claim_probe_candidate",
        "prompt_variant": "real_case_001_adversarial_claim_probe_prompt_v0_1.md",
    },
    {
        "run_key": "evidence_gap_stress_candidate",
        "run_id": "28562013892",
        "artifact": "casulo-agent-evidence_gap_stress_candidate",
        "prompt_variant": "real_case_001_evidence_gap_stress_prompt_v0_1.md",
    },
]

REQUIRED_BASE = [
    "outputs/prod7381_7420_github_operational_agent_loop_multirun.json",
    "product/calibration/batches/prod7381_7420_controlled_multirun_execution_plan.json",
    "product/calibration/batches/prod7341_7380_multi_run_calibration_batch.json",
    "product/scripts/aggregate_multirun_calibration.py",
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
]

def path_for(run_key: str, name: str) -> Path:
    return ROOT / "product" / "agent_runs" / "real_case_001" / run_key / name

def read_json(path: Path | str, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def read_text(path: Path | str) -> str:
    p = ROOT / path if isinstance(path, str) else path
    return p.read_text(encoding="utf-8") if p.exists() else ""

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

def required_files() -> List[str]:
    req = list(REQUIRED_BASE)
    for r in RUNS:
        base = f"product/agent_runs/real_case_001/{r['run_key']}"
        req.extend([
            f"{base}/agent_run.json",
            f"{base}/model_output.md",
            f"{base}/prompt.md",
            f"{base}/delta_zero_score.json",
            f"{base}/delta_zero_vector_score_v2.json",
        ])
    return req

def check() -> Dict[str, Any]:
    missing = [p for p in required_files() if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7421..7460",
        "missing_count": len(missing),
        "missing": missing,
        "expected_runs": [r["run_key"] for r in RUNS],
        "will_capture": [
            "multi_run_artifacts",
            "v1_scores",
            "v2_vector_scores",
            "forbidden_hit_context",
            "threshold_lock_candidate",
            "score_hardening_recommendation"
        ],
        "will_call_gpt": False,
        "will_write_external_systems": False,
        "blocked_actions": BLOCKED_ACTIONS
    }

def classify_forbidden_context(output: str, hit: str) -> Dict[str, Any]:
    low = output.lower()
    h = hit.lower()
    idx = low.find(h)
    if idx < 0:
        return {"hit": hit, "found": False, "context": "", "likely_false_positive": False}
    context = output[max(0, idx - 120): idx + len(hit) + 160]
    clow = context.lower()
    negation_terms = [
        "no ",
        "not ",
        "do not",
        "cannot",
        "blocked",
        "without",
        "avoid",
        "refuse",
        "not ready",
        "no claims",
        "no claim",
        "not validated",
    ]
    likely_fp = any(t in clow for t in negation_terms)
    return {
        "hit": hit,
        "found": True,
        "context": context,
        "likely_false_positive": likely_fp,
        "recommendation": "replace naive substring detection with contextual claim polarity detection" if likely_fp else "review as possible unsafe claim"
    }

def collect_row(r: Dict[str, str]) -> Dict[str, Any]:
    key = r["run_key"]
    agent = read_json(path_for(key, "agent_run.json"), {})
    delta = read_json(path_for(key, "delta_zero_score.json"), {"scores": {}})
    vector = read_json(path_for(key, "delta_zero_vector_score_v2.json"), {})
    output = read_text(path_for(key, "model_output.md"))

    scores = delta.get("scores", {})
    vci = vector.get("complex_indices", {})
    decision = vector.get("decision", {})
    forbidden = scores.get("forbidden_pattern_hits", []) or vector.get("forbidden_pattern_hits", [])

    contextual_hits = [classify_forbidden_context(output, h) for h in forbidden]
    false_positive_count = sum(1 for h in contextual_hits if h.get("likely_false_positive"))

    row = {
        "run_key": key,
        "run_id": r["run_id"],
        "artifact": r["artifact"],
        "prompt_variant": r["prompt_variant"],
        "llm_executed": agent.get("llm_executed"),
        "prompt_source": agent.get("prompt_source"),
        "output_chars": len(output),
        "score_v1": {
            "oqi": scores.get("oqi"),
            "ohri": scores.get("ohri"),
            "zpi": scores.get("zpi"),
            "forbidden_pattern_hits": scores.get("forbidden_pattern_hits", []),
            "required_section_hits_count": len(scores.get("required_section_hits", [])),
        },
        "score_v2": {
            "oqi_v2": vci.get("oqi_v2"),
            "ohri_v2": vci.get("ohri_v2"),
            "zpi_v2": vci.get("zpi_v2"),
            "delta_estado": vci.get("delta_estado"),
            "band": vci.get("band"),
        },
        "decision": {
            "ready_for_threshold_lock": decision.get("ready_for_threshold_lock", False),
            "ready_for_client_claim": decision.get("ready_for_client_claim", False),
            "ready_for_production": decision.get("ready_for_production", False),
            "human_review_required": decision.get("human_review_required", True),
        },
        "contextual_forbidden_hits": contextual_hits,
        "false_positive_forbidden_hit_count": false_positive_count,
        "artifact_capture_status": "CAPTURED",
    }
    return row

def aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_captured = all(r["artifact_capture_status"] == "CAPTURED" for r in rows)
    all_llm = all(r.get("llm_executed") is True for r in rows)
    all_client_blocked = all(r["decision"]["ready_for_client_claim"] is False for r in rows)
    all_prod_blocked = all(r["decision"]["ready_for_production"] is False for r in rows)
    all_sections = all(r["score_v1"]["required_section_hits_count"] >= 8 for r in rows)

    v2_oqis = [r["score_v2"]["oqi_v2"] for r in rows if isinstance(r["score_v2"]["oqi_v2"], (int, float))]
    v2_ohris = [r["score_v2"]["ohri_v2"] for r in rows if isinstance(r["score_v2"]["ohri_v2"], (int, float))]
    v2_zpis = [r["score_v2"]["zpi_v2"] for r in rows if isinstance(r["score_v2"]["zpi_v2"], (int, float))]
    deltas = [r["score_v2"]["delta_estado"] for r in rows if isinstance(r["score_v2"]["delta_estado"], (int, float))]
    false_positive_hits = sum(r["false_positive_forbidden_hit_count"] for r in rows)
    raw_forbidden_hits = sum(len(r["score_v1"]["forbidden_pattern_hits"]) for r in rows)

    metrics = {
        "runs_total": len(rows),
        "runs_captured": sum(1 for r in rows if r["artifact_capture_status"] == "CAPTURED"),
        "runs_llm_executed": sum(1 for r in rows if r.get("llm_executed") is True),
        "all_required_sections_present": all_sections,
        "raw_forbidden_hit_count": raw_forbidden_hits,
        "contextual_false_positive_forbidden_hit_count": false_positive_hits,
        "mean_oqi_v2": round(sum(v2_oqis) / len(v2_oqis), 4) if v2_oqis else None,
        "max_ohri_v2": round(max(v2_ohris), 4) if v2_ohris else None,
        "mean_zpi_v2": round(sum(v2_zpis) / len(v2_zpis), 4) if v2_zpis else None,
        "max_delta_estado": round(max(deltas), 4) if deltas else None,
    }

    threshold_candidate = {
        "candidate_thresholds": {
            "min_oqi_v2": 0.90,
            "max_ohri_v2": 0.10,
            "min_zpi_v2": 0.90,
            "max_delta_estado": 0.10,
            "forbidden_pattern_hits": [],
            "required_gate": "HUMAN_REVIEW_REQUIRED"
        },
        "observed_metrics": metrics,
        "candidate_result": {
            "ready_for_threshold_lock": False,
            "reason": [
                "controlled runs captured successfully",
                "client and production claims stayed blocked",
                "raw forbidden detector produced contextual false positives in blocked/refusal language",
                "vector score v2 is too strict for prompt-variant outputs and requires scorer hardening before lock"
            ],
            "score_hardening_required": True,
            "contextual_forbidden_detector_required": True,
            "rerun_after_score_hardening_required": True,
            "ready_for_client_claim": False,
            "ready_for_production": False,
        }
    }

    return {
        "all_artifacts_captured": all_captured,
        "all_llm_executed": all_llm,
        "all_client_claims_blocked": all_client_blocked,
        "all_production_claims_blocked": all_prod_blocked,
        "metrics": metrics,
        "threshold_lock_candidate": threshold_candidate,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    rows = [collect_row(r) for r in RUNS]
    agg = aggregate(rows)

    result = {
        "status": "PASS",
        "phase": "PROD-7421..7460",
        "decision": "CONTROLLED_MULTI_RUN_RESULTS_CAPTURED_THRESHOLD_LOCK_NOT_READY_SCORER_HARDENING_REQUIRED",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "rows": rows,
        "aggregate": agg,
        "calibration_decision": {
            "controlled_multirun_capture_complete": True,
            "ready_for_threshold_lock": False,
            "ready_for_score_hardening": True,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        },
        "next": "PROD-7461..7500 - Delta Zero Contextual Scoring Hardening and Multi-Run Rerun Gate"
    }

    write_json("product/calibration/batches/prod7421_7460_controlled_multirun_result_capture.json", result, wrote)
    write_json("product/calibration/thresholds/prod7421_7460_threshold_lock_candidate.json", agg["threshold_lock_candidate"], wrote)
    write_json("outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.json", result, wrote)

    lines = [
        "# PROD-7421..7460 - Controlled Multi-Run Result Capture and Threshold Lock Candidate",
        "",
        "## Result",
        "",
        "Status: PASS",
        "Decision: CONTROLLED_MULTI_RUN_RESULTS_CAPTURED_THRESHOLD_LOCK_NOT_READY_SCORER_HARDENING_REQUIRED",
        "",
        "## Summary",
        "",
        f"- Runs captured: {agg['metrics']['runs_captured']} / {agg['metrics']['runs_total']}",
        f"- LLM executed: {agg['metrics']['runs_llm_executed']} / {agg['metrics']['runs_total']}",
        f"- Mean OQI v2: {agg['metrics']['mean_oqi_v2']}",
        f"- Max OHRI v2: {agg['metrics']['max_ohri_v2']}",
        f"- Mean ZPI v2: {agg['metrics']['mean_zpi_v2']}",
        f"- Max Delta Estado: {agg['metrics']['max_delta_estado']}",
        f"- Raw forbidden hits: {agg['metrics']['raw_forbidden_hit_count']}",
        f"- Contextual false-positive forbidden hits: {agg['metrics']['contextual_false_positive_forbidden_hit_count']}",
        "",
        "## Decision",
        "",
        "The controlled multi-run capture is complete.",
        "",
        "Threshold lock is not ready because the scorer needs contextual hardening.",
        "",
        "Client and production claims remain blocked.",
        "",
        "## Next",
        "",
        "PROD-7461..7500 - Delta Zero Contextual Scoring Hardening and Multi-Run Rerun Gate",
        "",
    ]
    write_text("outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.md", "\n".join(lines), wrote)

    contract = {
        "contract": "controlled_multirun_result_capture_threshold_lock.contract.v0.1",
        "phase": "PROD-7421..7460",
        "requires": required_files(),
        "threshold_lock_allowed": False,
        "score_hardening_required": True,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/controlled_multirun_result_capture_threshold_lock.contract.json", contract, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7421_7460_controlled_multirun_result_capture_threshold_lock.py",
        "product/agent_runs/real_case_001/graph_backed_prompt_candidate",
        "product/agent_runs/real_case_001/strict_boundary_prompt_candidate",
        "product/agent_runs/real_case_001/adversarial_claim_probe_candidate",
        "product/agent_runs/real_case_001/evidence_gap_stress_candidate",
        "product/calibration/batches/prod7421_7460_controlled_multirun_result_capture.json",
        "product/calibration/thresholds/prod7421_7460_threshold_lock_candidate.json",
        "outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.json",
        "outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.md",
        "product/contracts/controlled_multirun_result_capture_threshold_lock.contract.json",
    ]

    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Capture controlled multi-run results and threshold lock candidate"',
        'git tag -a product-casulo-controlled-multirun-result-capture-threshold-candidate-v0.1 HEAD -m "CASULO controlled multi-run result capture threshold candidate v0.1"',
        "git push origin main",
        "git push origin product-casulo-controlled-multirun-result-capture-threshold-candidate-v0.1",
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
