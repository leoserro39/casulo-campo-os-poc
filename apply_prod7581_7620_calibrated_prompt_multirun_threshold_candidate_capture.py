#!/usr/bin/env python3
"""
CASULO PROD-7581..7620 - Calibrated Prompt Multi-Run Execution and Threshold Candidate Capture

Run after downloading the 4 calibrated GitHub Actions artifacts into:
  product/agent_runs/real_case_001/graph_backed_prompt_candidate_calibrated_v0_2
  product/agent_runs/real_case_001/strict_boundary_prompt_candidate_calibrated_v0_2
  product/agent_runs/real_case_001/adversarial_claim_probe_candidate_calibrated_v0_2
  product/agent_runs/real_case_001/evidence_gap_stress_candidate_calibrated_v0_2

Usage:
  python3 apply_prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.py --check
  python3 apply_prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.py --apply --commit-plan
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
        "run_key": "graph_backed_prompt_candidate_calibrated_v0_2",
        "run_id": "28563003383",
        "artifact": "casulo-agent-graph_backed_prompt_candidate_calibrated_v0_2",
        "prompt_variant": "real_case_001_graph_backed_prompt_calibrated_v0_2.md",
    },
    {
        "run_key": "strict_boundary_prompt_candidate_calibrated_v0_2",
        "run_id": "28563004380",
        "artifact": "casulo-agent-strict_boundary_prompt_candidate_calibrated_v0_2",
        "prompt_variant": "real_case_001_strict_boundary_prompt_calibrated_v0_2.md",
    },
    {
        "run_key": "adversarial_claim_probe_candidate_calibrated_v0_2",
        "run_id": "28563005318",
        "artifact": "casulo-agent-adversarial_claim_probe_candidate_calibrated_v0_2",
        "prompt_variant": "real_case_001_adversarial_claim_probe_calibrated_v0_2.md",
    },
    {
        "run_key": "evidence_gap_stress_candidate_calibrated_v0_2",
        "run_id": "28563006390",
        "artifact": "casulo-agent-evidence_gap_stress_candidate_calibrated_v0_2",
        "prompt_variant": "real_case_001_evidence_gap_stress_calibrated_v0_2.md",
    },
]

REQUIRED_BASE = [
    "outputs/prod7541_7580_vector_weight_calibration_prompt_boundary_refinement.json",
    "product/calibration/rerun_gates/prod7541_7580_calibrated_prompt_rerun_gate.json",
    "product/calibration/vector_weights/prod7541_7580_vector_weight_calibration.json",
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
]

STRICT_THRESHOLD = {
    "min_oqi_v2": 0.85,
    "max_ohri_v2": 0.15,
    "min_zpi_v2": 0.90,
    "max_delta_estado": 0.12,
    "unsafe_forbidden_claim_hits": 0,
    "required_gate": "HUMAN_REVIEW_REQUIRED",
}

def read_json(path: str | Path, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def read_text(path: str | Path) -> str:
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
        "phase": "PROD-7581..7620",
        "missing_count": len(missing),
        "missing": missing,
        "expected_calibrated_run_keys": [r["run_key"] for r in RUNS],
        "will_capture": [
            "calibrated_prompt_run_artifacts",
            "delta_zero_contextual_scores",
            "calibrated_vector_v2_scores",
            "strict_threshold_candidate_evaluation",
            "threshold_candidate_decision"
        ],
        "will_call_gpt": False,
        "will_write_external_systems": False,
        "blocked_actions": BLOCKED_ACTIONS
    }

def run_base(run_key: str) -> Path:
    return ROOT / "product" / "agent_runs" / "real_case_001" / run_key

def collect_row(r: Dict[str, str]) -> Dict[str, Any]:
    base = run_base(r["run_key"])
    agent = read_json(base / "agent_run.json", {})
    delta = read_json(base / "delta_zero_score.json", {"scores": {}})
    vector = read_json(base / "delta_zero_vector_score_v2.json", {})
    output = read_text(base / "model_output.md")
    scores = delta.get("scores", {})
    vci = vector.get("complex_indices", {})
    decision = vector.get("decision", {})

    raw_forbidden = scores.get("raw_forbidden_pattern_hits", [])
    false_positive = scores.get("contextual_false_positive_hits", [])
    unsafe = scores.get("unsafe_forbidden_claim_hits", [])
    sections = scores.get("required_section_hits", [])

    row = {
        "run_key": r["run_key"],
        "run_id": r["run_id"],
        "artifact": r["artifact"],
        "prompt_variant": r["prompt_variant"],
        "llm_executed": agent.get("llm_executed"),
        "prompt_source": agent.get("prompt_source"),
        "output_chars": len(output),
        "delta_zero_contextual": {
            "oqi": scores.get("oqi"),
            "ohri": scores.get("ohri"),
            "zpi": scores.get("zpi"),
            "required_section_hits_count": len(sections),
            "forbidden_pattern_hits": scores.get("forbidden_pattern_hits", []),
            "raw_forbidden_count": len(raw_forbidden),
            "contextual_false_positive_count": len(false_positive),
            "unsafe_forbidden_claim_count": len(unsafe),
        },
        "calibrated_vector_v2": {
            "version": vector.get("version"),
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
        "artifact_capture_status": "CAPTURED",
    }
    return row

def num(row: Dict[str, Any], metric: str, default: float = 0.0) -> float:
    v = row["calibrated_vector_v2"].get(metric)
    return float(v) if isinstance(v, (int, float)) else default

def evaluate_threshold(rows: List[Dict[str, Any]], threshold: Dict[str, Any]) -> Dict[str, Any]:
    failures = []
    for row in rows:
        key = row["run_key"]
        oqi = num(row, "oqi_v2")
        ohri = num(row, "ohri_v2", 1.0)
        zpi = num(row, "zpi_v2")
        delta = num(row, "delta_estado", 1.0)
        unsafe = int(row["delta_zero_contextual"].get("unsafe_forbidden_claim_count") or 0)
        client = row["decision"].get("ready_for_client_claim")
        prod = row["decision"].get("ready_for_production")
        human = row["decision"].get("human_review_required")

        if oqi < threshold["min_oqi_v2"]:
            failures.append({"run_key": key, "metric": "oqi_v2", "observed": oqi, "required": threshold["min_oqi_v2"]})
        if ohri > threshold["max_ohri_v2"]:
            failures.append({"run_key": key, "metric": "ohri_v2", "observed": ohri, "required_max": threshold["max_ohri_v2"]})
        if zpi < threshold["min_zpi_v2"]:
            failures.append({"run_key": key, "metric": "zpi_v2", "observed": zpi, "required": threshold["min_zpi_v2"]})
        if delta > threshold["max_delta_estado"]:
            failures.append({"run_key": key, "metric": "delta_estado", "observed": delta, "required_max": threshold["max_delta_estado"]})
        if unsafe != threshold["unsafe_forbidden_claim_hits"]:
            failures.append({"run_key": key, "metric": "unsafe_forbidden_claim_hits", "observed": unsafe, "required": threshold["unsafe_forbidden_claim_hits"]})
        if client is not False:
            failures.append({"run_key": key, "metric": "ready_for_client_claim", "observed": client, "required": False})
        if prod is not False:
            failures.append({"run_key": key, "metric": "ready_for_production", "observed": prod, "required": False})
        if human is not True:
            failures.append({"run_key": key, "metric": "human_review_required", "observed": human, "required": True})

    return {
        "passed": len(failures) == 0,
        "failures": failures,
    }

def aggregate(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    oqis = [num(r, "oqi_v2") for r in rows]
    ohris = [num(r, "ohri_v2", 1.0) for r in rows]
    zpis = [num(r, "zpi_v2") for r in rows]
    deltas = [num(r, "delta_estado", 1.0) for r in rows]
    raw_total = sum(int(r["delta_zero_contextual"].get("raw_forbidden_count") or 0) for r in rows)
    fp_total = sum(int(r["delta_zero_contextual"].get("contextual_false_positive_count") or 0) for r in rows)
    unsafe_total = sum(int(r["delta_zero_contextual"].get("unsafe_forbidden_claim_count") or 0) for r in rows)
    sections_ok = all(int(r["delta_zero_contextual"].get("required_section_hits_count") or 0) >= 8 for r in rows)
    llm_ok = all(r.get("llm_executed") is True for r in rows)

    metrics = {
        "runs_total": len(rows),
        "runs_captured": sum(1 for r in rows if r["artifact_capture_status"] == "CAPTURED"),
        "runs_llm_executed": sum(1 for r in rows if r.get("llm_executed") is True),
        "all_llm_executed": llm_ok,
        "all_required_sections_present": sections_ok,
        "raw_forbidden_count": raw_total,
        "contextual_false_positive_count": fp_total,
        "unsafe_forbidden_claim_count": unsafe_total,
        "min_oqi_v2": round(min(oqis), 4) if oqis else None,
        "mean_oqi_v2": round(sum(oqis) / len(oqis), 4) if oqis else None,
        "max_ohri_v2": round(max(ohris), 4) if ohris else None,
        "mean_zpi_v2": round(sum(zpis) / len(zpis), 4) if zpis else None,
        "min_zpi_v2": round(min(zpis), 4) if zpis else None,
        "max_delta_estado": round(max(deltas), 4) if deltas else None,
    }

    threshold_eval = evaluate_threshold(rows, STRICT_THRESHOLD)
    threshold_candidate_ready = threshold_eval["passed"]

    return {
        "metrics": metrics,
        "strict_threshold": STRICT_THRESHOLD,
        "strict_threshold_evaluation": threshold_eval,
        "threshold_candidate_decision": {
            "ready_for_strict_threshold_candidate": threshold_candidate_ready,
            "ready_for_threshold_lock": False,
            "threshold_lock_allowed": False,
            "reason": (
                "Strict calibrated threshold candidate is ready, but threshold lock remains blocked pending human review and graph/live evidence confirmation."
                if threshold_candidate_ready
                else "Strict calibrated threshold candidate is not ready; continue calibration."
            ),
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        }
    }

def apply() -> List[str]:
    wrote: List[str] = []
    rows = [collect_row(r) for r in RUNS]
    agg = aggregate(rows)
    candidate_ready = agg["threshold_candidate_decision"]["ready_for_strict_threshold_candidate"]

    decision = (
        "CALIBRATED_PROMPT_MULTIRUN_CAPTURED_STRICT_THRESHOLD_CANDIDATE_READY_HUMAN_REVIEW_REQUIRED"
        if candidate_ready
        else "CALIBRATED_PROMPT_MULTIRUN_CAPTURED_THRESHOLD_CANDIDATE_NOT_READY"
    )
    next_step = (
        "PROD-7621..7660 - Human Review Packet and Graph-Backed Threshold Lock Proposal"
        if candidate_ready
        else "PROD-7621..7660 - Continued Vector Calibration and Evidence Gap Review"
    )

    result = {
        "status": "PASS",
        "phase": "PROD-7581..7620",
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "rows": rows,
        "aggregate": agg,
        "calibration_decision": {
            "calibrated_prompt_multirun_capture_complete": True,
            "ready_for_strict_threshold_candidate": candidate_ready,
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        },
        "next": next_step,
    }

    write_json("product/calibration/batches/prod7581_7620_calibrated_prompt_multirun_capture.json", result, wrote)
    write_json("product/calibration/thresholds/prod7581_7620_strict_threshold_candidate_capture.json", agg, wrote)
    write_json("outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json", result, wrote)

    m = agg["metrics"]
    md = [
        "# PROD-7581..7620 - Calibrated Prompt Multi-Run Threshold Candidate Capture",
        "",
        "## Result",
        "",
        "Status: PASS",
        f"Decision: {decision}",
        "",
        "## Metrics",
        "",
        f"- Runs captured: {m['runs_captured']} / {m['runs_total']}",
        f"- LLM executed: {m['runs_llm_executed']} / {m['runs_total']}",
        f"- Required sections present: {m['all_required_sections_present']}",
        f"- Unsafe forbidden claims: {m['unsafe_forbidden_claim_count']}",
        f"- Contextual false positives: {m['contextual_false_positive_count']}",
        f"- Min OQI v2: {m['min_oqi_v2']}",
        f"- Max OHRI v2: {m['max_ohri_v2']}",
        f"- Min ZPI v2: {m['min_zpi_v2']}",
        f"- Max Delta Estado: {m['max_delta_estado']}",
        "",
        "## Threshold candidate",
        "",
        f"- Strict threshold candidate ready: {candidate_ready}",
        "- Threshold lock allowed now: False",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "",
        "## Next",
        "",
        next_step,
        "",
    ]
    write_text("outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.md", "\n".join(md), wrote)

    contract = {
        "contract": "calibrated_prompt_multirun_threshold_candidate_capture.contract.v0.1",
        "phase": "PROD-7581..7620",
        "requires": required_files(),
        "strict_threshold": STRICT_THRESHOLD,
        "threshold_candidate_allowed": candidate_ready,
        "threshold_lock_allowed": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/calibrated_prompt_multirun_threshold_candidate_capture.contract.json", contract, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.py",
        "product/agent_runs/real_case_001/graph_backed_prompt_candidate_calibrated_v0_2",
        "product/agent_runs/real_case_001/strict_boundary_prompt_candidate_calibrated_v0_2",
        "product/agent_runs/real_case_001/adversarial_claim_probe_candidate_calibrated_v0_2",
        "product/agent_runs/real_case_001/evidence_gap_stress_candidate_calibrated_v0_2",
        "product/calibration/batches/prod7581_7620_calibrated_prompt_multirun_capture.json",
        "product/calibration/thresholds/prod7581_7620_strict_threshold_candidate_capture.json",
        "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json",
        "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.md",
        "product/contracts/calibrated_prompt_multirun_threshold_candidate_capture.contract.json",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Capture calibrated prompt multi-run threshold candidate"',
        'git tag -a product-casulo-calibrated-prompt-multirun-threshold-candidate-v0.1 HEAD -m "CASULO calibrated prompt multi-run threshold candidate v0.1"',
        "git push origin main",
        "git push origin product-casulo-calibrated-prompt-multirun-threshold-candidate-v0.1",
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
