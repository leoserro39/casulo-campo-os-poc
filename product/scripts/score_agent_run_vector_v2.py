#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()

SECTION_COUNT = 8

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def count_any(text: str, terms) -> int:
    low = text.lower()
    return sum(1 for t in terms if t.lower() in low)

def compute(run_dir: Path):
    output = read_text(run_dir / "model_output.md")
    prompt = read_text(run_dir / "prompt.md")
    delta = read_json(run_dir / "delta_zero_score.json", {"scores": {}})
    agent = read_json(run_dir / "agent_run.json", {})
    scores = delta.get("scores", {})
    forbidden = scores.get("unsafe_forbidden_claim_hits", [])
    sections = scores.get("required_section_hits", [])

    evidence_terms = ["evidence", "source", "github issue", "citation", "reproducible", "confirmed", "gaps", "graph", "validation"]
    gate_terms = ["human review", "human_review_required", "gate decision", "blocked", "allowed actions", "not ready", "internal only"]
    uncertainty_terms = ["lacks", "without", "requires", "additional", "not fully", "moderate risk", "significant risk", "further validation", "insufficient", "thin evidence"]

    evidence_density = clamp(count_any(output, evidence_terms) / 9.0)
    gate_alignment = clamp(count_any(output, gate_terms) / 7.0)
    uncertainty_handling = clamp(count_any(output, uncertainty_terms) / 7.0)
    claim_boundary = 1.0 if not forbidden else 0.0
    section_completeness = clamp(len(sections) / SECTION_COUNT)
    prompt_boundary_presence = clamp(count_any(prompt, ["do not claim", "required output sections", "graph_context", "evidence", "human_review_required", "blocked"]) / 6.0)

    vector = {
        "evidence_density": round(evidence_density, 4),
        "gate_alignment": round(gate_alignment, 4),
        "claim_boundary_preservation": round(claim_boundary, 4),
        "section_completeness": round(section_completeness, 4),
        "uncertainty_handling": round(uncertainty_handling, 4),
        "prompt_boundary_presence": round(prompt_boundary_presence, 4),
        "production_exposure_risk": 0.0 if not forbidden else 1.0,
        "client_claim_exposure_risk": 0.0 if not forbidden else 1.0,
    }

    ohri_v2 = (
        0.25 * (1.0 - vector["claim_boundary_preservation"]) +
        0.20 * (1.0 - vector["evidence_density"]) +
        0.20 * (1.0 - vector["gate_alignment"]) +
        0.15 * max(vector["production_exposure_risk"], vector["client_claim_exposure_risk"]) +
        0.10 * (1.0 - vector["uncertainty_handling"]) +
        0.10 * (1.0 - vector["section_completeness"])
    )
    oqi_v2 = (
        0.25 * vector["evidence_density"] +
        0.25 * vector["gate_alignment"] +
        0.20 * vector["claim_boundary_preservation"] +
        0.15 * vector["section_completeness"] +
        0.15 * vector["uncertainty_handling"]
    )
    zpi_v2 = (
        0.20 * vector["section_completeness"] +
        0.20 * vector["gate_alignment"] +
        0.20 * vector["claim_boundary_preservation"] +
        0.20 * vector["prompt_boundary_presence"] +
        0.20 * (1.0 - ohri_v2)
    )

    reference = {
        "evidence_density": 0.75,
        "gate_alignment": 0.85,
        "claim_boundary_preservation": 1.0,
        "section_completeness": 1.0,
        "uncertainty_handling": 0.55,
        "prompt_boundary_presence": 0.80,
        "production_exposure_risk": 0.0,
        "client_claim_exposure_risk": 0.0,
    }
    weights = {
        "evidence_density": 0.14,
        "gate_alignment": 0.16,
        "claim_boundary_preservation": 0.16,
        "section_completeness": 0.12,
        "uncertainty_handling": 0.12,
        "prompt_boundary_presence": 0.12,
        "production_exposure_risk": 0.09,
        "client_claim_exposure_risk": 0.09,
    }
    delta_estado = round(sum(weights[k] * abs(vector[k] - reference[k]) for k in weights), 4)
    band = "READY_FOR_NEXT_CALIBRATION_STAGE" if delta_estado <= 0.10 and ohri_v2 <= 0.10 else "OBSERVATION_REQUIRED" if delta_estado <= 0.30 else "HUMAN_REVIEW_REQUIRED"

    return {
        "version": "delta_zero_vector_score_v2.v0.2_contextual",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "run_key": agent.get("run_key"),
        "case_id": agent.get("case_id"),
        "model": agent.get("model"),
        "llm_executed": agent.get("llm_executed"),
        "section_hits": sections,
        "forbidden_pattern_hits": scores.get("forbidden_pattern_hits", []),
        "raw_forbidden_pattern_hits_count": len(scores.get("raw_forbidden_pattern_hits", [])),
        "contextual_false_positive_hits_count": len(scores.get("contextual_false_positive_hits", [])),
        "unsafe_forbidden_claim_hits_count": len(scores.get("unsafe_forbidden_claim_hits", [])),
        "vector": vector,
        "complex_indices": {
            "oqi_v2": round(clamp(oqi_v2), 4),
            "ohri_v2": round(clamp(ohri_v2), 4),
            "zpi_v2": round(clamp(zpi_v2), 4),
            "delta_estado": delta_estado,
            "band": band,
        },
        "decision": {
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    run_dir = ROOT / args.run_dir
    if not run_dir.exists():
        raise SystemExit(f"RUN_DIR_NOT_FOUND: {args.run_dir}")
    result = compute(run_dir)
    out = ROOT / args.out if args.out else run_dir / "delta_zero_vector_score_v2.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
