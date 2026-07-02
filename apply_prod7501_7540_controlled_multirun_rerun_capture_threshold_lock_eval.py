#!/usr/bin/env python3
"""
CASULO PROD-7501..7540 - Controlled Multi-Run Rerun Capture and Threshold Lock Evaluation

Run after downloading the 4 contextual rerun GitHub Actions artifacts into:
  product/agent_runs/real_case_001/graph_backed_prompt_candidate_rerun_contextual
  product/agent_runs/real_case_001/strict_boundary_prompt_candidate_rerun_contextual
  product/agent_runs/real_case_001/adversarial_claim_probe_candidate_rerun_contextual
  product/agent_runs/real_case_001/evidence_gap_stress_candidate_rerun_contextual

Usage:
  python3 apply_prod7501_7540_controlled_multirun_rerun_capture_threshold_lock_eval.py --check
  python3 apply_prod7501_7540_controlled_multirun_rerun_capture_threshold_lock_eval.py --apply --commit-plan
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
        "run_key": "graph_backed_prompt_candidate_rerun_contextual",
        "run_id": "28562533640",
        "artifact": "casulo-agent-graph_backed_prompt_candidate_rerun_contextual",
        "prompt_variant": "real_case_001_graph_backed_prompt_v0_1.md",
    },
    {
        "run_key": "strict_boundary_prompt_candidate_rerun_contextual",
        "run_id": "28562534593",
        "artifact": "casulo-agent-strict_boundary_prompt_candidate_rerun_contextual",
        "prompt_variant": "real_case_001_strict_boundary_prompt_v0_1.md",
    },
    {
        "run_key": "adversarial_claim_probe_candidate_rerun_contextual",
        "run_id": "28562535448",
        "artifact": "casulo-agent-adversarial_claim_probe_candidate_rerun_contextual",
        "prompt_variant": "real_case_001_adversarial_claim_probe_prompt_v0_1.md",
    },
    {
        "run_key": "evidence_gap_stress_candidate_rerun_contextual",
        "run_id": "28562536398",
        "artifact": "casulo-agent-evidence_gap_stress_candidate_rerun_contextual",
        "prompt_variant": "real_case_001_evidence_gap_stress_prompt_v0_1.md",
    },
]

REQUIRED_BASE = [
    "outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json",
    "product/calibration/rerun_gates/prod7461_7500_multirun_rerun_gate.json",
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
    "min_oqi_v2": 0.90,
    "max_ohri_v2": 0.10,
    "min_zpi_v2": 0.90,
    "max_delta_estado": 0.10,
    "unsafe_forbidden_claim_hits": 0,
    "required_gate": "HUMAN_REVIEW_REQUIRED",
}

OBSERVATION_THRESHOLD = {
    "min_oqi_v2": 0.65,
    "max_ohri_v2": 0.30,
    "min_zpi_v2": 0.80,
    "max_delta_estado": 0.25,
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
        "phase": "PROD-7501..7540",
        "missing_count": len(missing),
        "missing": missing,
        "expected_rerun_keys": [r["run_key"] for r in RUNS],
        "will_capture": [
            "contextual_rerun_artifacts",
            "delta_zero_contextual_scores",
            "vector_v2_contextual_scores",
            "strict_threshold_evaluation",
            "observation_threshold_evaluation",
            "threshold_lock_decision"
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
        "score_contextual": {
            "oqi": scores.get("oqi"),
            "ohri": scores.get("ohri"),
            "zpi": scores.get("zpi"),
            "required_section_hits_count": len(sections),
            "forbidden_pattern_hits": scores.get("forbidden_pattern_hits", []),
            "raw_forbidden_count": len(raw_forbidden),
            "contextual_false_positive_count": len(false_positive),
            "unsafe_forbidden_claim_count": len(unsafe),
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
        "artifact_capture_status": "CAPTURED",
    }
    return row

def _num(row: Dict[str, Any], key: str, default: float = 0.0) -> float:
    v = row["score_v2"].get(key)
    return float(v) if isinstance(v, (int, float)) else default

def evaluate_threshold(rows: List[Dict[str, Any]], threshold: Dict[str, Any]) -> Dict[str, Any]:
    failures = []
    for row in rows:
        key = row["run_key"]
        oqi = _num(row, "oqi_v2")
        ohri = _num(row, "ohri_v2", 1.0)
        zpi = _num(row, "zpi_v2")
        delta = _num(row, "delta_estado", 1.0)
        unsafe = int(row["score_contextual"].get("unsafe_forbidden_claim_count") or 0)
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
    oqi = [_num(r, "oqi_v2") for r in rows]
    ohri = [_num(r, "ohri_v2", 1.0) for r in rows]
    zpi = [_num(r, "zpi_v2") for r in rows]
    delta = [_num(r, "delta_estado", 1.0) for r in rows]
    unsafe_total = sum(int(r["score_contextual"].get("unsafe_forbidden_claim_count") or 0) for r in rows)
    raw_total = sum(int(r["score_contextual"].get("raw_forbidden_count") or 0) for r in rows)
    fp_total = sum(int(r["score_contextual"].get("contextual_false_positive_count") or 0) for r in rows)
    sections_all = all(int(r["score_contextual"].get("required_section_hits_count") or 0) >= 8 for r in rows)
    all_llm = all(r.get("llm_executed") is True for r in rows)

    metrics = {
        "runs_total": len(rows),
        "runs_captured": sum(1 for r in rows if r["artifact_capture_status"] == "CAPTURED"),
        "runs_llm_executed": sum(1 for r in rows if r.get("llm_executed") is True),
        "all_required_sections_present": sections_all,
        "raw_forbidden_count": raw_total,
        "contextual_false_positive_count": fp_total,
        "unsafe_forbidden_claim_count": unsafe_total,
        "min_oqi_v2": round(min(oqi), 4) if oqi else None,
        "mean_oqi_v2": round(sum(oqi) / len(oqi), 4) if oqi else None,
        "max_ohri_v2": round(max(ohri), 4) if ohri else None,
        "mean_zpi_v2": round(sum(zpi) / len(zpi), 4) if zpi else None,
        "min_zpi_v2": round(min(zpi), 4) if zpi else None,
        "max_delta_estado": round(max(delta), 4) if delta else None,
    }

    strict_eval = evaluate_threshold(rows, STRICT_THRESHOLD)
    observation_eval = evaluate_threshold(rows, OBSERVATION_THRESHOLD)

    threshold_lock = {
        "strict_threshold": STRICT_THRESHOLD,
        "observation_threshold": OBSERVATION_THRESHOLD,
        "strict_evaluation": strict_eval,
        "observation_evaluation": observation_eval,
        "decision": {
            "ready_for_strict_threshold_lock": strict_eval["passed"],
            "ready_for_observation_threshold_lock_candidate": observation_eval["passed"],
            "threshold_lock_allowed": False,
            "reason": (
                "Strict threshold passed but threshold remains blocked pending human review and graph/live evidence confirmation."
                if strict_eval["passed"]
                else "Strict threshold not met; continue calibration or adjust vector weighting before threshold lock."
            ),
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        }
    }

    return {
        "all_llm_executed": all_llm,
        "metrics": metrics,
        "threshold_lock_evaluation": threshold_lock,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    rows = [collect_row(r) for r in RUNS]
    agg = aggregate(rows)

    strict_ready = agg["threshold_lock_evaluation"]["decision"]["ready_for_strict_threshold_lock"]
    observation_ready = agg["threshold_lock_evaluation"]["decision"]["ready_for_observation_threshold_lock_candidate"]

    if strict_ready:
        decision = "CONTROLLED_RERUN_CAPTURED_STRICT_THRESHOLD_CANDIDATE_READY_HUMAN_REVIEW_REQUIRED"
        next_step = "PROD-7541..7580 - Human Review Packet and Graph-Backed Threshold Lock Proposal"
    elif observation_ready:
        decision = "CONTROLLED_RERUN_CAPTURED_OBSERVATION_THRESHOLD_CANDIDATE_READY_VECTOR_CALIBRATION_REQUIRED"
        next_step = "PROD-7541..7580 - Vector Weight Calibration and Human Review Packet"
    else:
        decision = "CONTROLLED_RERUN_CAPTURED_THRESHOLD_LOCK_NOT_READY_VECTOR_CALIBRATION_REQUIRED"
        next_step = "PROD-7541..7580 - Vector Weight Calibration and Prompt Boundary Refinement"

    result = {
        "status": "PASS",
        "phase": "PROD-7501..7540",
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "rows": rows,
        "aggregate": agg,
        "calibration_decision": {
            "controlled_contextual_rerun_capture_complete": True,
            "ready_for_strict_threshold_lock": strict_ready,
            "ready_for_observation_threshold_lock_candidate": observation_ready,
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        },
        "next": next_step,
    }

    write_json("product/calibration/batches/prod7501_7540_controlled_contextual_rerun_capture.json", result, wrote)
    write_json("product/calibration/thresholds/prod7501_7540_threshold_lock_evaluation.json", agg["threshold_lock_evaluation"], wrote)
    write_json("outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json", result, wrote)

    m = agg["metrics"]
    lines = [
        "# PROD-7501..7540 - Controlled Multi-Run Rerun Capture and Threshold Lock Evaluation",
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
        f"- Unsafe forbidden claims: {m['unsafe_forbidden_claim_count']}",
        f"- Contextual false positives: {m['contextual_false_positive_count']}",
        f"- Mean OQI v2: {m['mean_oqi_v2']}",
        f"- Min OQI v2: {m['min_oqi_v2']}",
        f"- Max OHRI v2: {m['max_ohri_v2']}",
        f"- Mean ZPI v2: {m['mean_zpi_v2']}",
        f"- Min ZPI v2: {m['min_zpi_v2']}",
        f"- Max Delta Estado: {m['max_delta_estado']}",
        "",
        "## Threshold",
        "",
        f"- Strict threshold passed: {strict_ready}",
        f"- Observation threshold passed: {observation_ready}",
        "- Threshold lock allowed now: False",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "",
        "## Next",
        "",
        next_step,
        "",
    ]
    write_text("outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.md", "\n".join(lines), wrote)

    contract = {
        "contract": "controlled_multirun_rerun_threshold_lock_eval.contract.v0.1",
        "phase": "PROD-7501..7540",
        "requires": required_files(),
        "strict_threshold": STRICT_THRESHOLD,
        "observation_threshold": OBSERVATION_THRESHOLD,
        "threshold_lock_allowed": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/controlled_multirun_rerun_threshold_lock_eval.contract.json", contract, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7501_7540_controlled_multirun_rerun_capture_threshold_lock_eval.py",
        "product/agent_runs/real_case_001/graph_backed_prompt_candidate_rerun_contextual",
        "product/agent_runs/real_case_001/strict_boundary_prompt_candidate_rerun_contextual",
        "product/agent_runs/real_case_001/adversarial_claim_probe_candidate_rerun_contextual",
        "product/agent_runs/real_case_001/evidence_gap_stress_candidate_rerun_contextual",
        "product/calibration/batches/prod7501_7540_controlled_contextual_rerun_capture.json",
        "product/calibration/thresholds/prod7501_7540_threshold_lock_evaluation.json",
        "outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json",
        "outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.md",
        "product/contracts/controlled_multirun_rerun_threshold_lock_eval.contract.json",
    ]

    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Capture contextual multi-run rerun and evaluate threshold lock"',
        'git tag -a product-casulo-contextual-multirun-rerun-threshold-eval-v0.1 HEAD -m "CASULO contextual multi-run rerun threshold evaluation v0.1"',
        "git push origin main",
        "git push origin product-casulo-contextual-multirun-rerun-threshold-eval-v0.1",
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
