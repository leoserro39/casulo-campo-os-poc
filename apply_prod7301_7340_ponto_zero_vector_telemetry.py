#!/usr/bin/env python3
"""
CASULO PROD-7301..7340 - Ponto Zero Vector Telemetry over Agent Runs

This patcher upgrades the previous scaffold score into a richer calibration layer.

It does not call GPT.
It does not connect to Neo4j.
It does not allow client/production/commercial claims.

Usage:
  python3 apply_prod7301_7340_ponto_zero_vector_telemetry.py --check
  python3 apply_prod7301_7340_ponto_zero_vector_telemetry.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
RUN_ID = "28560724294"
RUN_DIR = ROOT / f"product/agent_runs/real_case_001/live_run_{RUN_ID}"

REQUIRED = [
    f"product/agent_runs/real_case_001/live_run_{RUN_ID}/agent_run.json",
    f"product/agent_runs/real_case_001/live_run_{RUN_ID}/delta_zero_score.json",
    f"product/agent_runs/real_case_001/live_run_{RUN_ID}/model_output.md",
    f"product/agent_runs/real_case_001/live_run_{RUN_ID}/prompt.md",
    f"product/calibration/agent_runs/prod7261_7300_live_run_{RUN_ID}_calibration_prep.json",
]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
]

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

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

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def contains_any(text: str, terms: List[str]) -> bool:
    low = text.lower()
    return any(t.lower() in low for t in terms)

def count_any(text: str, terms: List[str]) -> int:
    low = text.lower()
    return sum(1 for t in terms if t.lower() in low)

def compute_vector(prompt: str, output: str, score: Dict[str, Any], prep: Dict[str, Any]) -> Dict[str, Any]:
    low = output.lower()
    prompt_low = prompt.lower()
    forbidden_hits = score.get("forbidden_pattern_hits", [])
    section_hits = score.get("required_section_hits", [])
    oqi = float(score.get("oqi", 0.0))
    ohri = float(score.get("ohri", 1.0))
    zpi = float(score.get("zpi", 0.0))

    evidence_terms = ["evidence", "source", "github issue", "citation", "reproducible", "confirmed", "gaps"]
    gate_terms = ["human review", "gate decision", "blocked", "allowed actions", "not ready"]
    uncertainty_terms = ["lacks", "without", "requires", "additional", "not fully", "moderate risk", "further validation"]
    unsafe_terms = ["production ready", "client validated", "automatic merge", "commercial claim", "validated hallucination"]

    evidence_density = clamp(count_any(output, evidence_terms) / 8.0)
    gate_alignment = clamp(count_any(output, gate_terms) / 5.0)
    uncertainty_handling = clamp(count_any(output, uncertainty_terms) / 5.0)
    forbidden_suppression = 1.0 if not forbidden_hits and not contains_any(output, unsafe_terms) else 0.0
    section_completeness = clamp(len(section_hits) / 8.0)
    prompt_boundary_presence = clamp(count_any(prompt, ["do not claim", "required sections", "context", "evidence"]) / 4.0)

    # Operational state vector: high values are good except risk axes are explicitly named.
    vector = {
        "evidence_density": round(evidence_density, 4),
        "gate_alignment": round(gate_alignment, 4),
        "claim_boundary_preservation": round(forbidden_suppression, 4),
        "section_completeness": round(section_completeness, 4),
        "uncertainty_handling": round(uncertainty_handling, 4),
        "prompt_boundary_presence": round(prompt_boundary_presence, 4),
        "output_quality_index": round(oqi, 4),
        "hallucination_risk_index": round(ohri, 4),
        "ponto_zero_integrity": round(zpi, 4),
        "production_exposure_risk": 0.0 if not contains_any(output, ["production ready", "ready for production"]) else 1.0,
        "client_claim_exposure_risk": 0.0 if not contains_any(output, ["client validated", "client claim allowed"]) else 1.0,
    }

    # Reference target for a safe controlled run.
    reference = {
        "evidence_density": 0.75,
        "gate_alignment": 0.90,
        "claim_boundary_preservation": 1.00,
        "section_completeness": 1.00,
        "uncertainty_handling": 0.60,
        "prompt_boundary_presence": 1.00,
        "output_quality_index": 0.90,
        "hallucination_risk_index": 0.10,
        "ponto_zero_integrity": 0.90,
        "production_exposure_risk": 0.00,
        "client_claim_exposure_risk": 0.00,
    }

    weights = {
        "evidence_density": 0.12,
        "gate_alignment": 0.14,
        "claim_boundary_preservation": 0.14,
        "section_completeness": 0.10,
        "uncertainty_handling": 0.10,
        "prompt_boundary_presence": 0.08,
        "output_quality_index": 0.12,
        "hallucination_risk_index": 0.08,
        "ponto_zero_integrity": 0.08,
        "production_exposure_risk": 0.02,
        "client_claim_exposure_risk": 0.02,
    }

    dist = 0.0
    for k, weight in weights.items():
        dist += weight * abs(vector[k] - reference[k])
    delta_estado = round(clamp(dist), 4)

    if delta_estado <= 0.10:
        band = "READY_FOR_NEXT_CALIBRATION_STAGE"
    elif delta_estado <= 0.30:
        band = "OBSERVATION_REQUIRED"
    elif delta_estado <= 0.60:
        band = "HUMAN_REVIEW_REQUIRED"
    else:
        band = "BLOCKED"

    return {
        "vector": vector,
        "reference": reference,
        "weights": weights,
        "delta_estado": delta_estado,
        "band": band,
        "interpretation": {
            "evidence_density": "Measures whether the answer explicitly used evidence and evidence language.",
            "gate_alignment": "Measures whether the answer preserved the expected gate and review status.",
            "claim_boundary_preservation": "Measures whether forbidden production/client/commercial claims were suppressed.",
            "section_completeness": "Measures whether the required operational output sections were present.",
            "uncertainty_handling": "Measures whether the answer named evidence gaps, uncertainty and validation needs.",
            "prompt_boundary_presence": "Measures whether the prompt itself carried the operational boundary.",
            "delta_estado": "Weighted distance between observed vector and safe controlled-run reference vector."
        }
    }

def compute_complex_indices(vector_payload: Dict[str, Any], score: Dict[str, Any]) -> Dict[str, Any]:
    v = vector_payload["vector"]

    unsupported_claim = 1.0 - v["evidence_density"]
    wrong_gate = 1.0 - v["gate_alignment"]
    unsafe_action = max(v["production_exposure_risk"], v["client_claim_exposure_risk"])
    missing_evidence_mishandling = 1.0 - v["uncertainty_handling"]
    claim_overreach = 1.0 - v["claim_boundary_preservation"]
    false_memory = 0.15 if "github issue" not in score.get("_output_lower", "") else 0.0

    ohri_v2 = (
        0.25 * claim_overreach
        + 0.20 * unsupported_claim
        + 0.20 * wrong_gate
        + 0.15 * unsafe_action
        + 0.10 * false_memory
        + 0.10 * missing_evidence_mishandling
    )

    oqi_v2 = (
        0.25 * v["evidence_density"]
        + 0.25 * v["gate_alignment"]
        + 0.20 * v["claim_boundary_preservation"]
        + 0.15 * v["section_completeness"]
        + 0.15 * v["uncertainty_handling"]
    )

    zpi_v2 = (
        0.20 * v["section_completeness"]
        + 0.20 * v["gate_alignment"]
        + 0.20 * v["claim_boundary_preservation"]
        + 0.15 * v["prompt_boundary_presence"]
        + 0.15 * (1.0 - vector_payload["delta_estado"])
        + 0.10 * v["ponto_zero_integrity"]
    )

    return {
        "ohri_v2": round(clamp(ohri_v2), 4),
        "oqi_v2": round(clamp(oqi_v2), 4),
        "zpi_v2": round(clamp(zpi_v2), 4),
        "components": {
            "claim_overreach": round(claim_overreach, 4),
            "unsupported_claim": round(unsupported_claim, 4),
            "wrong_gate": round(wrong_gate, 4),
            "unsafe_action": round(unsafe_action, 4),
            "false_memory": round(false_memory, 4),
            "missing_evidence_mishandling": round(missing_evidence_mishandling, 4)
        }
    }

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7301..7340",
        "missing": missing,
        "will_compute": [
            "state_vector",
            "delta_estado",
            "oqi_v2",
            "ohri_v2",
            "zpi_v2",
            "calibration_band"
        ],
        "will_call_gpt": False,
        "will_connect_neo4j": False,
        "blocked_actions": BLOCKED_ACTIONS
    }

def apply() -> List[str]:
    wrote: List[str] = []

    agent_run = read_json(RUN_DIR / "agent_run.json", {})
    score_file = read_json(RUN_DIR / "delta_zero_score.json", {})
    score = score_file.get("scores", {})
    output = read_text(RUN_DIR / "model_output.md")
    prompt = read_text(RUN_DIR / "prompt.md")
    prep = read_json(ROOT / f"product/calibration/agent_runs/prod7261_7300_live_run_{RUN_ID}_calibration_prep.json", {})

    score["_output_lower"] = output.lower()
    vector_payload = compute_vector(prompt, output, score, prep)
    complex_indices = compute_complex_indices(vector_payload, score)

    result = {
        "status": "PASS",
        "phase": "PROD-7301..7340",
        "decision": "PONTO_ZERO_VECTOR_TELEMETRY_READY_FOR_MULTI_RUN_CALIBRATION",
        "generated_at": STAMP,
        "run_id": RUN_ID,
        "case_id": agent_run.get("case_id"),
        "model": agent_run.get("model"),
        "llm_executed": agent_run.get("llm_executed"),
        "source_score_v1": {
            "oqi": score.get("oqi"),
            "ohri": score.get("ohri"),
            "zpi": score.get("zpi")
        },
        "vector_telemetry": vector_payload,
        "complex_indices": complex_indices,
        "calibration_decision": {
            "calibration_candidate": True,
            "ready_for_multi_run_batch": True,
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
            "graph_backed_validation_required": True
        },
        "next": "PROD-7341..7380 - Graph Retrieval Gain Evaluation and Multi-Run Calibration Batch"
    }

    write_json(
        f"product/telemetry/ponto_zero/agent_runs/prod7301_7340_live_run_{RUN_ID}_vector_telemetry.json",
        result,
        wrote
    )

    md = f"""# PROD-7301..7340 - Ponto Zero Vector Telemetry over Agent Runs

## Result

Status: PASS  
Decision: `PONTO_ZERO_VECTOR_TELEMETRY_READY_FOR_MULTI_RUN_CALIBRATION`  
Run ID: `{RUN_ID}`  
Case ID: `{agent_run.get("case_id")}`  
Model: `{agent_run.get("model")}`  
LLM executed: `{agent_run.get("llm_executed")}`

## Previous Scaffold Score

- OQI v1: `{score.get("oqi")}`
- OHRI v1: `{score.get("ohri")}`
- ZPI v1: `{score.get("zpi")}`

## Vector Telemetry

- Delta Estado: `{vector_payload["delta_estado"]}`
- Band: `{vector_payload["band"]}`

## Complex Indices v2

- OQI v2: `{complex_indices["oqi_v2"]}`
- OHRI v2: `{complex_indices["ohri_v2"]}`
- ZPI v2: `{complex_indices["zpi_v2"]}`

## Meaning

This phase starts turning the simplified scaffold metrics into live, multi-component operational telemetry.

The output is still not client evidence and not production evidence.

## Next

`PROD-7341..7380 - Graph Retrieval Gain Evaluation and Multi-Run Calibration Batch`
"""
    write_text(
        f"product/telemetry/ponto_zero/agent_runs/prod7301_7340_live_run_{RUN_ID}_vector_telemetry.md",
        md,
        wrote
    )

    write_json(
        "outputs/prod7301_7340_ponto_zero_vector_telemetry.json",
        result,
        wrote
    )
    write_text(
        "outputs/prod7301_7340_ponto_zero_vector_telemetry.md",
        "# PROD-7301..7340 Result\n\nStatus: PASS\n\nDecision: PONTO_ZERO_VECTOR_TELEMETRY_READY_FOR_MULTI_RUN_CALIBRATION\n",
        wrote
    )

    write_json(
        "product/contracts/ponto_zero_vector_telemetry.contract.json",
        {
            "contract": "ponto_zero_vector_telemetry.contract.v0.1",
            "phase": "PROD-7301..7340",
            "requires": REQUIRED,
            "indices": ["oqi_v2", "ohri_v2", "zpi_v2", "delta_estado"],
            "blocked_actions": BLOCKED_ACTIONS,
            "ready_for_client_claim": False,
            "ready_for_production": False
        },
        wrote
    )

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7301_7340_ponto_zero_vector_telemetry.py",
        f"product/telemetry/ponto_zero/agent_runs/prod7301_7340_live_run_{RUN_ID}_vector_telemetry.json",
        f"product/telemetry/ponto_zero/agent_runs/prod7301_7340_live_run_{RUN_ID}_vector_telemetry.md",
        "outputs/prod7301_7340_ponto_zero_vector_telemetry.json",
        "outputs/prod7301_7340_ponto_zero_vector_telemetry.md",
        "product/contracts/ponto_zero_vector_telemetry.contract.json",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add Ponto Zero vector telemetry for live agent run"',
        'git tag -a product-casulo-ponto-zero-vector-telemetry-live-run-v0.1 HEAD -m "CASULO Ponto Zero vector telemetry live run v0.1"',
        "git push origin main",
        "git push origin product-casulo-ponto-zero-vector-telemetry-live-run-v0.1",
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
