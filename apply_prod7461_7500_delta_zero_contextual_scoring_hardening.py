#!/usr/bin/env python3
"""
CASULO PROD-7461..7500 - Delta Zero Contextual Scoring Hardening and Multi-Run Rerun Gate

Continues after:
  PROD-7421..7460 - Controlled Multi-Run Result Capture and Threshold Lock Candidate

Purpose:
  - harden Delta Zero scoring so blocked/refusal language is not treated as unsafe overclaim;
  - keep raw forbidden phrase telemetry, but separate contextual false positives from actual unsafe claims;
  - harden vector score v2 to use contextual claim polarity;
  - rescore the already captured multi-run outputs without overwriting the original artifact scores;
  - prepare the rerun gate for the same four GitHub Actions prompt variants.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7461_7500_delta_zero_contextual_scoring_hardening.py --check
  python3 apply_prod7461_7500_delta_zero_contextual_scoring_hardening.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

RUN_KEYS = [
    "graph_backed_prompt_candidate",
    "strict_boundary_prompt_candidate",
    "adversarial_claim_probe_candidate",
    "evidence_gap_stress_candidate",
]

REQUIRED = [
    "outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.json",
    "product/calibration/batches/prod7421_7460_controlled_multirun_result_capture.json",
    "product/calibration/thresholds/prod7421_7460_threshold_lock_candidate.json",
    "product/scripts/score_agent_output_delta_zero.py",
    "product/scripts/score_agent_run_vector_v2.py",
    ".github/workflows/casulo_agent_multirun_calibration.yml",
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

FORBIDDEN = [
    "production ready",
    "ready for production",
    "client validated",
    "client claim allowed",
    "validated hallucination reduction",
    "automatic merge",
    "automatic merges",
    "commercial claim",
]

SECTION_PATTERNS = {
    "operational state": ["operational state", "current operational state"],
    "evidence used": ["evidence used", "evidence", "evidence summary"],
    "evidence gaps": ["evidence gaps", "gaps", "evidence gap"],
    "gate decision": ["gate decision", "gate", "human_review_required"],
    "allowed actions": ["allowed actions", "allowed next actions"],
    "blocked actions": ["blocked actions", "blocked"],
    "risk of hallucination": ["risk of hallucination", "risk of hallucination / overclaim", "overclaim"],
    "next safe step": ["next safe step", "safe next step"],
}

NEGATION_TERMS = [
    "no ",
    "not ",
    "do not",
    "don't",
    "cannot",
    "can't",
    "blocked",
    "without",
    "avoid",
    "refuse",
    "must not",
    "should not",
    "not ready",
    "no claims",
    "no claim",
    "not validated",
    "not treated as",
    "not considered",
    "prohibited",
    "forbidden",
    "disallowed",
    "não ",
    "nao ",
    "bloqueado",
    "bloqueada",
    "sem ",
]

RISK_CONTEXT_TERMS = [
    "risk",
    "hallucination",
    "overclaim",
    "misinterpretation",
    "could be mistaken",
    "potential",
    "avoid",
    "blocked actions",
    "boundary",
    "contextual",
    "internal only",
    "review required",
    "human_review_required",
]

def read_text(path: str | Path) -> str:
    p = ROOT / path if isinstance(path, str) else path
    return p.read_text(encoding="utf-8") if p.exists() else ""

def read_json(path: str | Path, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def write_text(path: str, text: str, wrote: List[str], executable: bool = False) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if executable:
        p.chmod(0o755)
    wrote.append(path)

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", wrote)

def required_files() -> List[str]:
    files = list(REQUIRED)
    for k in RUN_KEYS:
        base = f"product/agent_runs/real_case_001/{k}"
        files.extend([
            f"{base}/agent_run.json",
            f"{base}/model_output.md",
            f"{base}/prompt.md",
            f"{base}/delta_zero_score.json",
            f"{base}/delta_zero_vector_score_v2.json",
        ])
    return files

def check() -> Dict[str, Any]:
    missing = [p for p in required_files() if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7461..7500",
        "missing_count": len(missing),
        "missing": missing,
        "will_update": [
            "product/scripts/score_agent_output_delta_zero.py",
            "product/scripts/score_agent_run_vector_v2.py"
        ],
        "will_create": [
            "product/calibration/hardening/prod7461_7500_delta_zero_contextual_rescore.json",
            "product/calibration/rerun_gates/prod7461_7500_multirun_rerun_gate.json",
            "outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json",
            "product/contracts/delta_zero_contextual_scoring_hardening.contract.json",
            "docs/product/746_DELTA_ZERO_CONTEXTUAL_SCORING_HARDENING.md"
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "blocked_actions": BLOCKED_ACTIONS
    }

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def phrase_context(text: str, phrase: str, radius: int = 140) -> List[Dict[str, Any]]:
    low = text.lower()
    phrase_low = phrase.lower()
    hits = []
    start = 0
    while True:
        idx = low.find(phrase_low, start)
        if idx < 0:
            break
        left = max(0, idx - radius)
        right = min(len(text), idx + len(phrase) + radius)
        ctx = text[left:right]
        clow = ctx.lower()
        likely_safe = any(t in clow for t in NEGATION_TERMS) or any(t in clow for t in RISK_CONTEXT_TERMS)
        hits.append({
            "phrase": phrase,
            "start": idx,
            "context": ctx,
            "classification": "CONTEXTUAL_FALSE_POSITIVE" if likely_safe else "UNSAFE_CLAIM_CANDIDATE",
            "rationale": "phrase appears inside blocked/refusal/risk/negative context" if likely_safe else "phrase appears without local negation or risk boundary"
        })
        start = idx + len(phrase_low)
    return hits

def contextual_forbidden(text: str) -> Dict[str, Any]:
    raw = []
    safe = []
    unsafe = []
    for phrase in FORBIDDEN:
        for hit in phrase_context(text, phrase):
            raw.append(hit)
            if hit["classification"] == "CONTEXTUAL_FALSE_POSITIVE":
                safe.append(hit)
            else:
                unsafe.append(hit)
    return {
        "raw_forbidden_pattern_hits": raw,
        "contextual_false_positive_hits": safe,
        "unsafe_forbidden_claim_hits": unsafe,
        "forbidden_pattern_hits": [h["phrase"] for h in unsafe],
    }

def section_hits(text: str) -> List[str]:
    low = text.lower()
    hits = []
    for canonical, patterns in SECTION_PATTERNS.items():
        if any(p.lower() in low for p in patterns):
            hits.append(canonical)
    return hits

def hardened_delta_score_text(text: str) -> Dict[str, Any]:
    forbidden = contextual_forbidden(text)
    sections = section_hits(text)
    low = text.lower()
    gate_ok = "human_review_required" in low or "human review" in low or "human reviewer" in low
    evidence_ok = "evidence" in low and ("gap" in low or "gaps" in low or "insufficient" in low or "further validation" in low)
    boundary_ok = not forbidden["unsafe_forbidden_claim_hits"]

    structure = len(sections) / len(SECTION_PATTERNS)
    gate = 1.0 if gate_ok else 0.0
    boundary = 1.0 if boundary_ok else 0.0
    evidence = 1.0 if evidence_ok else 0.5 if "evidence" in low else 0.0

    oqi = round(clamp((0.35 * structure) + (0.25 * gate) + (0.25 * boundary) + (0.15 * evidence)), 4)
    ohri = round(clamp(1.0 - oqi + (0.15 * len(forbidden["unsafe_forbidden_claim_hits"]))), 4)
    zpi = round(clamp((0.35 * structure) + (0.35 * gate) + (0.30 * boundary)), 4)

    return {
        "version": "delta_zero_score.v0.2_contextual",
        "generated_at": STAMP,
        "scores": {
            "forbidden_pattern_hits": forbidden["forbidden_pattern_hits"],
            "raw_forbidden_pattern_hits": forbidden["raw_forbidden_pattern_hits"],
            "contextual_false_positive_hits": forbidden["contextual_false_positive_hits"],
            "unsafe_forbidden_claim_hits": forbidden["unsafe_forbidden_claim_hits"],
            "required_section_hits": sections,
            "oqi": oqi,
            "ohri": ohri,
            "zpi": zpi,
            "ready_for_client_claim": False,
            "ready_for_production": False
        }
    }

def count_any(text: str, terms: List[str]) -> int:
    low = text.lower()
    return sum(1 for t in terms if t.lower() in low)

def hardened_vector_score(output: str, prompt: str, delta: Dict[str, Any], agent: Dict[str, Any], run_key: str) -> Dict[str, Any]:
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
    section_completeness = clamp(len(sections) / len(SECTION_PATTERNS))
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
        "generated_at": STAMP,
        "run_key": run_key,
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
            "human_review_required": True
        }
    }

DELTA_SCRIPT = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

FORBIDDEN = [
    "production ready",
    "ready for production",
    "client validated",
    "client claim allowed",
    "validated hallucination reduction",
    "automatic merge",
    "automatic merges",
    "commercial claim",
]

SECTION_PATTERNS = {
    "operational state": ["operational state", "current operational state"],
    "evidence used": ["evidence used", "evidence", "evidence summary"],
    "evidence gaps": ["evidence gaps", "gaps", "evidence gap"],
    "gate decision": ["gate decision", "gate", "human_review_required"],
    "allowed actions": ["allowed actions", "allowed next actions"],
    "blocked actions": ["blocked actions", "blocked"],
    "risk of hallucination": ["risk of hallucination", "risk of hallucination / overclaim", "overclaim"],
    "next safe step": ["next safe step", "safe next step"],
}

NEGATION_TERMS = [
    "no ", "not ", "do not", "don't", "cannot", "can't", "blocked",
    "without", "avoid", "refuse", "must not", "should not", "not ready",
    "no claims", "no claim", "not validated", "not treated as",
    "not considered", "prohibited", "forbidden", "disallowed",
    "não ", "nao ", "bloqueado", "bloqueada", "sem ",
]

RISK_CONTEXT_TERMS = [
    "risk", "hallucination", "overclaim", "misinterpretation", "could be mistaken",
    "potential", "avoid", "blocked actions", "boundary", "contextual",
    "internal only", "review required", "human_review_required",
]

def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))

def phrase_context(text: str, phrase: str, radius: int = 140):
    low = text.lower()
    phrase_low = phrase.lower()
    hits = []
    start = 0
    while True:
        idx = low.find(phrase_low, start)
        if idx < 0:
            break
        left = max(0, idx - radius)
        right = min(len(text), idx + len(phrase) + radius)
        ctx = text[left:right]
        clow = ctx.lower()
        likely_safe = any(t in clow for t in NEGATION_TERMS) or any(t in clow for t in RISK_CONTEXT_TERMS)
        hits.append({
            "phrase": phrase,
            "start": idx,
            "context": ctx,
            "classification": "CONTEXTUAL_FALSE_POSITIVE" if likely_safe else "UNSAFE_CLAIM_CANDIDATE",
            "rationale": "phrase appears inside blocked/refusal/risk/negative context" if likely_safe else "phrase appears without local negation or risk boundary"
        })
        start = idx + len(phrase_low)
    return hits

def contextual_forbidden(text: str):
    raw = []
    safe = []
    unsafe = []
    for phrase in FORBIDDEN:
        for hit in phrase_context(text, phrase):
            raw.append(hit)
            if hit["classification"] == "CONTEXTUAL_FALSE_POSITIVE":
                safe.append(hit)
            else:
                unsafe.append(hit)
    return {
        "raw_forbidden_pattern_hits": raw,
        "contextual_false_positive_hits": safe,
        "unsafe_forbidden_claim_hits": unsafe,
        "forbidden_pattern_hits": [h["phrase"] for h in unsafe],
    }

def section_hits(text: str):
    low = text.lower()
    hits = []
    for canonical, patterns in SECTION_PATTERNS.items():
        if any(p.lower() in low for p in patterns):
            hits.append(canonical)
    return hits

def score(text: str):
    forbidden = contextual_forbidden(text)
    sections = section_hits(text)
    low = text.lower()
    gate_ok = "human_review_required" in low or "human review" in low or "human reviewer" in low
    evidence_ok = "evidence" in low and ("gap" in low or "gaps" in low or "insufficient" in low or "further validation" in low)
    boundary_ok = not forbidden["unsafe_forbidden_claim_hits"]

    structure = len(sections) / len(SECTION_PATTERNS)
    gate = 1.0 if gate_ok else 0.0
    boundary = 1.0 if boundary_ok else 0.0
    evidence = 1.0 if evidence_ok else 0.5 if "evidence" in low else 0.0

    oqi = round(clamp((0.35 * structure) + (0.25 * gate) + (0.25 * boundary) + (0.15 * evidence)), 4)
    ohri = round(clamp(1.0 - oqi + (0.15 * len(forbidden["unsafe_forbidden_claim_hits"]))), 4)
    zpi = round(clamp((0.35 * structure) + (0.35 * gate) + (0.30 * boundary)), 4)

    return {
        "version": "delta_zero_score.v0.2_contextual",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scores": {
            "forbidden_pattern_hits": forbidden["forbidden_pattern_hits"],
            "raw_forbidden_pattern_hits": forbidden["raw_forbidden_pattern_hits"],
            "contextual_false_positive_hits": forbidden["contextual_false_positive_hits"],
            "unsafe_forbidden_claim_hits": forbidden["unsafe_forbidden_claim_hits"],
            "required_section_hits": sections,
            "oqi": oqi,
            "ohri": ohri,
            "zpi": zpi,
            "ready_for_client_claim": False,
            "ready_for_production": False,
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-file", default="product/agent_runs/real_case_001/model_output.md")
    ap.add_argument("--out", default="product/agent_runs/real_case_001/delta_zero_score.json")
    args = ap.parse_args()

    text = Path(args.output_file).read_text(encoding="utf-8")
    result = score(text)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
"""

VECTOR_SCRIPT = r"""#!/usr/bin/env python3
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
"""

def rescore_all() -> Dict[str, Any]:
    rows = []
    for key in RUN_KEYS:
        base = ROOT / "product" / "agent_runs" / "real_case_001" / key
        output = read_text(base / "model_output.md")
        prompt = read_text(base / "prompt.md")
        agent = read_json(base / "agent_run.json", {})
        original_delta = read_json(base / "delta_zero_score.json", {"scores": {}})
        original_vector = read_json(base / "delta_zero_vector_score_v2.json", {"complex_indices": {}})

        delta = hardened_delta_score_text(output)
        vector = hardened_vector_score(output, prompt, delta, agent, key)

        row = {
            "run_key": key,
            "llm_executed": agent.get("llm_executed"),
            "original": {
                "oqi": original_delta.get("scores", {}).get("oqi"),
                "ohri": original_delta.get("scores", {}).get("ohri"),
                "zpi": original_delta.get("scores", {}).get("zpi"),
                "forbidden_pattern_hits": original_delta.get("scores", {}).get("forbidden_pattern_hits", []),
                "oqi_v2": original_vector.get("complex_indices", {}).get("oqi_v2"),
                "ohri_v2": original_vector.get("complex_indices", {}).get("ohri_v2"),
                "zpi_v2": original_vector.get("complex_indices", {}).get("zpi_v2"),
                "delta_estado": original_vector.get("complex_indices", {}).get("delta_estado"),
            },
            "hardened": {
                "oqi": delta["scores"]["oqi"],
                "ohri": delta["scores"]["ohri"],
                "zpi": delta["scores"]["zpi"],
                "forbidden_pattern_hits": delta["scores"]["forbidden_pattern_hits"],
                "raw_forbidden_count": len(delta["scores"]["raw_forbidden_pattern_hits"]),
                "contextual_false_positive_count": len(delta["scores"]["contextual_false_positive_hits"]),
                "unsafe_forbidden_claim_count": len(delta["scores"]["unsafe_forbidden_claim_hits"]),
                "oqi_v2": vector["complex_indices"]["oqi_v2"],
                "ohri_v2": vector["complex_indices"]["ohri_v2"],
                "zpi_v2": vector["complex_indices"]["zpi_v2"],
                "delta_estado": vector["complex_indices"]["delta_estado"],
                "band": vector["complex_indices"]["band"],
            },
            "ready_for_client_claim": False,
            "ready_for_production": False,
        }
        rows.append(row)

    v2_oqi = [r["hardened"]["oqi_v2"] for r in rows]
    v2_ohri = [r["hardened"]["ohri_v2"] for r in rows]
    v2_zpi = [r["hardened"]["zpi_v2"] for r in rows]
    deltas = [r["hardened"]["delta_estado"] for r in rows]
    unsafe_total = sum(r["hardened"]["unsafe_forbidden_claim_count"] for r in rows)
    raw_total = sum(r["hardened"]["raw_forbidden_count"] for r in rows)
    fp_total = sum(r["hardened"]["contextual_false_positive_count"] for r in rows)

    return {
        "version": "delta_zero_contextual_hardening_rescore.v0.1",
        "generated_at": STAMP,
        "phase": "PROD-7461..7500",
        "rows": rows,
        "aggregate": {
            "runs_total": len(rows),
            "runs_llm_executed": sum(1 for r in rows if r["llm_executed"] is True),
            "raw_forbidden_count": raw_total,
            "contextual_false_positive_count": fp_total,
            "unsafe_forbidden_claim_count": unsafe_total,
            "mean_oqi_v2_hardened": round(sum(v2_oqi) / len(v2_oqi), 4),
            "max_ohri_v2_hardened": round(max(v2_ohri), 4),
            "mean_zpi_v2_hardened": round(sum(v2_zpi) / len(v2_zpi), 4),
            "max_delta_estado_hardened": round(max(deltas), 4),
        }
    }

def apply() -> List[str]:
    wrote: List[str] = []

    write_text("product/scripts/score_agent_output_delta_zero.py", DELTA_SCRIPT, wrote, executable=True)
    write_text("product/scripts/score_agent_run_vector_v2.py", VECTOR_SCRIPT, wrote, executable=True)

    rescore = rescore_all()
    agg = rescore["aggregate"]

    rerun_gate = {
        "version": "multirun_rerun_gate.v0.1",
        "phase": "PROD-7461..7500",
        "generated_at": STAMP,
        "reason": "Scorer hardened to separate raw forbidden strings from contextual false positives and unsafe claims.",
        "ready_for_controlled_multirun_rerun": True,
        "rerun_required": True,
        "rerun_targets": RUN_KEYS,
        "workflow": ".github/workflows/casulo_agent_multirun_calibration.yml",
        "expected_effect": [
            "fewer false forbidden hits for blocked/refusal language",
            "more accurate OQI/OHRI/ZPI v2",
            "clearer threshold lock candidate after rerun"
        ],
        "threshold_lock_allowed_now": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS",
        "phase": "PROD-7461..7500",
        "decision": "DELTA_ZERO_CONTEXTUAL_SCORING_HARDENED_READY_FOR_CONTROLLED_MULTI_RUN_RERUN",
        "generated_at": STAMP,
        "rescore": rescore,
        "calibration_decision": {
            "score_hardening_complete": True,
            "ready_for_controlled_multirun_rerun": True,
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        },
        "next": "PROD-7501..7540 - Controlled Multi-Run Rerun Capture and Threshold Lock Evaluation"
    }

    write_json("product/calibration/hardening/prod7461_7500_delta_zero_contextual_rescore.json", rescore, wrote)
    write_json("product/calibration/rerun_gates/prod7461_7500_multirun_rerun_gate.json", rerun_gate, wrote)
    write_json("outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json", result, wrote)

    md = [
        "# PROD-7461..7500 - Delta Zero Contextual Scoring Hardening",
        "",
        "## Result",
        "",
        "Status: PASS",
        "Decision: DELTA_ZERO_CONTEXTUAL_SCORING_HARDENED_READY_FOR_CONTROLLED_MULTI_RUN_RERUN",
        "",
        "## Hardened rescore",
        "",
        f"- Runs: {agg['runs_total']}",
        f"- LLM executed: {agg['runs_llm_executed']}",
        f"- Raw forbidden phrases: {agg['raw_forbidden_count']}",
        f"- Contextual false positives: {agg['contextual_false_positive_count']}",
        f"- Unsafe forbidden claims: {agg['unsafe_forbidden_claim_count']}",
        f"- Mean OQI v2 hardened: {agg['mean_oqi_v2_hardened']}",
        f"- Max OHRI v2 hardened: {agg['max_ohri_v2_hardened']}",
        f"- Mean ZPI v2 hardened: {agg['mean_zpi_v2_hardened']}",
        f"- Max Delta Estado hardened: {agg['max_delta_estado_hardened']}",
        "",
        "## Boundary",
        "",
        "Threshold lock is still not allowed until the controlled multi-run rerun is captured.",
        "",
        "Client and production claims remain blocked.",
        "",
        "## Next",
        "",
        "PROD-7501..7540 - Controlled Multi-Run Rerun Capture and Threshold Lock Evaluation",
        "",
    ]
    write_text("outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.md", "\n".join(md), wrote)

    contract = {
        "contract": "delta_zero_contextual_scoring_hardening.contract.v0.1",
        "phase": "PROD-7461..7500",
        "requires": required_files(),
        "updates": [
            "product/scripts/score_agent_output_delta_zero.py",
            "product/scripts/score_agent_run_vector_v2.py"
        ],
        "contextual_forbidden_detector_required": True,
        "threshold_lock_allowed": False,
        "rerun_required": True,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/delta_zero_contextual_scoring_hardening.contract.json", contract, wrote)

    docs = """# 746 - Delta Zero Contextual Scoring Hardening

This phase hardens Delta Zero scoring.

The old detector treated any forbidden phrase as unsafe, even when the answer said:

- do not claim client validated evidence;
- no automatic merge;
- not ready for production.

The new detector preserves raw phrase telemetry but classifies each hit as either:

- CONTEXTUAL_FALSE_POSITIVE, when inside blocked/refusal/risk/negative language;
- UNSAFE_CLAIM_CANDIDATE, when the phrase appears without a local boundary.

Threshold lock remains blocked until the four controlled runs are rerun with the hardened scorer.
"""
    write_text("docs/product/746_DELTA_ZERO_CONTEXTUAL_SCORING_HARDENING.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7461_7500_delta_zero_contextual_scoring_hardening.py",
        "product/scripts/score_agent_output_delta_zero.py",
        "product/scripts/score_agent_run_vector_v2.py",
        "product/calibration/hardening/prod7461_7500_delta_zero_contextual_rescore.json",
        "product/calibration/rerun_gates/prod7461_7500_multirun_rerun_gate.json",
        "outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json",
        "outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.md",
        "product/contracts/delta_zero_contextual_scoring_hardening.contract.json",
        "docs/product/746_DELTA_ZERO_CONTEXTUAL_SCORING_HARDENING.md",
    ]
    return "\n".join([
        "python3 -m py_compile \\",
        "  product/scripts/score_agent_output_delta_zero.py \\",
        "  product/scripts/score_agent_run_vector_v2.py",
        "",
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Harden Delta Zero contextual scoring for multi-run calibration"',
        'git tag -a product-casulo-delta-zero-contextual-scoring-hardening-v0.1 HEAD -m "CASULO Delta Zero contextual scoring hardening v0.1"',
        "git push origin main",
        "git push origin product-casulo-delta-zero-contextual-scoring-hardening-v0.1",
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
