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

    sections = scores.get("required_section_hits", [])
    unsafe = scores.get("unsafe_forbidden_claim_hits", [])
    raw = scores.get("raw_forbidden_pattern_hits", [])
    fp = scores.get("contextual_false_positive_hits", [])

    contextual_oqi = float(scores.get("oqi") or 0.0)
    contextual_ohri = float(scores.get("ohri") if scores.get("ohri") is not None else 1.0)
    contextual_zpi = float(scores.get("zpi") or 0.0)

    evidence_signal = 1.0 if "evidence used" in sections and "evidence gaps" in sections else 0.5 if "evidence used" in sections else 0.0
    gate_signal = 1.0 if "gate decision" in sections and ("human_review_required" in output.lower() or "human review" in output.lower()) else 0.75 if "gate decision" in sections else 0.0
    section_signal = clamp(len(sections) / SECTION_COUNT)
    claim_boundary_signal = 1.0 if len(unsafe) == 0 else 0.0
    risk_signal = 1.0 if "risk of hallucination" in sections else 0.0
    prompt_boundary_signal = clamp(count_any(prompt, ["do not claim", "blocked", "human_review_required", "evidence", "gate", "next safe step"]) / 6.0)
    lexical_evidence = clamp(count_any(output, ["evidence", "gap", "graph", "source", "validation", "github"]) / 6.0)
    lexical_uncertainty = clamp(count_any(output, ["risk", "requires", "insufficient", "not ready", "human review", "further validation", "blocked"]) / 7.0)

    oqi_v2 = (
        0.20 * contextual_oqi +
        0.18 * claim_boundary_signal +
        0.16 * section_signal +
        0.14 * gate_signal +
        0.12 * evidence_signal +
        0.08 * risk_signal +
        0.07 * prompt_boundary_signal +
        0.05 * lexical_evidence
    )
    ohri_v2 = (
        0.35 * contextual_ohri +
        0.25 * (1.0 - claim_boundary_signal) +
        0.15 * (1.0 - gate_signal) +
        0.10 * (1.0 - evidence_signal) +
        0.10 * (1.0 - lexical_uncertainty) +
        0.05 * (1.0 - section_signal)
    )
    zpi_v2 = (
        0.22 * contextual_zpi +
        0.20 * section_signal +
        0.18 * gate_signal +
        0.18 * claim_boundary_signal +
        0.12 * prompt_boundary_signal +
        0.10 * evidence_signal
    )

    reference = {
        "contextual_oqi": 1.0,
        "claim_boundary_signal": 1.0,
        "section_signal": 1.0,
        "gate_signal": 1.0,
        "evidence_signal": 1.0,
        "risk_signal": 1.0,
        "prompt_boundary_signal": 0.85,
        "lexical_evidence": 0.60,
    }
    observed = {
        "contextual_oqi": contextual_oqi,
        "claim_boundary_signal": claim_boundary_signal,
        "section_signal": section_signal,
        "gate_signal": gate_signal,
        "evidence_signal": evidence_signal,
        "risk_signal": risk_signal,
        "prompt_boundary_signal": prompt_boundary_signal,
        "lexical_evidence": lexical_evidence,
    }
    weights = {
        "contextual_oqi": 0.18,
        "claim_boundary_signal": 0.18,
        "section_signal": 0.14,
        "gate_signal": 0.14,
        "evidence_signal": 0.12,
        "risk_signal": 0.10,
        "prompt_boundary_signal": 0.07,
        "lexical_evidence": 0.07,
    }
    delta_estado = round(sum(weights[k] * abs(observed[k] - reference[k]) for k in weights), 4)

    if delta_estado <= 0.08 and ohri_v2 <= 0.10:
        band = "STRICT_THRESHOLD_CANDIDATE"
    elif delta_estado <= 0.12 and ohri_v2 <= 0.15:
        band = "CALIBRATED_OBSERVATION_CANDIDATE"
    elif delta_estado <= 0.25:
        band = "OBSERVATION_REQUIRED"
    else:
        band = "HUMAN_REVIEW_REQUIRED"

    return {
        "version": "delta_zero_vector_score_v2.v0.3_calibrated",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "run_key": agent.get("run_key"),
        "case_id": agent.get("case_id"),
        "model": agent.get("model"),
        "llm_executed": agent.get("llm_executed"),
        "section_hits": sections,
        "forbidden_pattern_hits": scores.get("forbidden_pattern_hits", []),
        "raw_forbidden_pattern_hits_count": len(raw),
        "contextual_false_positive_hits_count": len(fp),
        "unsafe_forbidden_claim_hits_count": len(unsafe),
        "calibrated_signals": {
            "contextual_oqi": round(contextual_oqi, 4),
            "contextual_ohri": round(contextual_ohri, 4),
            "contextual_zpi": round(contextual_zpi, 4),
            "claim_boundary_signal": round(claim_boundary_signal, 4),
            "section_signal": round(section_signal, 4),
            "gate_signal": round(gate_signal, 4),
            "evidence_signal": round(evidence_signal, 4),
            "risk_signal": round(risk_signal, 4),
            "prompt_boundary_signal": round(prompt_boundary_signal, 4),
            "lexical_evidence": round(lexical_evidence, 4),
            "lexical_uncertainty": round(lexical_uncertainty, 4),
        },
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
