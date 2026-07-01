#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

REQUIRED_FIELDS = [
    "external_evidence_grounding_score",
    "external_gate_compliance_score",
    "external_claim_boundary_score",
    "external_state_vector_reasonableness_score",
    "external_delta_reasonableness_score",
    "external_drd_dzr_reasonableness_score",
    "external_token_expansion_fidelity_score",
    "external_next_action_quality_score",
    "external_usefulness_score",
    "external_false_memory_risk",
    "external_hallucination_risk_flag",
    "external_over_review_flag",
    "external_under_review_flag",
    "external_accept_for_calibration_signal",
    "external_reviewer_notes"
]

SCORE_FIELDS = [
    "external_evidence_grounding_score",
    "external_gate_compliance_score",
    "external_claim_boundary_score",
    "external_state_vector_reasonableness_score",
    "external_delta_reasonableness_score",
    "external_drd_dzr_reasonableness_score",
    "external_token_expansion_fidelity_score",
    "external_next_action_quality_score",
    "external_usefulness_score"
]

BOOL_FIELDS = [
    "external_hallucination_risk_flag",
    "external_over_review_flag",
    "external_under_review_flag",
    "external_accept_for_calibration_signal"
]

def parse_score(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        x = float(str(v).strip())
        if 0 <= x <= 5:
            return x
    except Exception:
        return None
    return None

def parse_bool(v):
    if v is None or str(v).strip() == "":
        return None
    s = str(v).strip().lower()
    if s in ["true", "1", "yes", "y", "sim"]:
        return True
    if s in ["false", "0", "no", "n", "nao", "não"]:
        return False
    return None

def false_memory_score(v):
    s = str(v or "").strip().upper()
    return {"NOT_APPLICABLE": 0.0, "LOW": 0.15, "MEDIUM": 0.5, "HIGH": 1.0}.get(s, None)

def clamp(x):
    return max(0.0, min(1.0, float(x)))

def score_indices(row):
    evidence = parse_score(row["external_evidence_grounding_score"]) / 5
    gate = parse_score(row["external_gate_compliance_score"]) / 5
    claim = parse_score(row["external_claim_boundary_score"]) / 5
    vector = parse_score(row["external_state_vector_reasonableness_score"]) / 5
    delta = parse_score(row["external_delta_reasonableness_score"]) / 5
    drd_dzr = parse_score(row["external_drd_dzr_reasonableness_score"]) / 5
    token = parse_score(row["external_token_expansion_fidelity_score"]) / 5
    next_action = parse_score(row["external_next_action_quality_score"]) / 5
    usefulness = parse_score(row["external_usefulness_score"]) / 5

    hallucination = 1.0 if parse_bool(row["external_hallucination_risk_flag"]) else 0.0
    under_review = 1.0 if parse_bool(row["external_under_review_flag"]) else 0.0
    over_review = 1.0 if parse_bool(row["external_over_review_flag"]) else 0.0
    fm = false_memory_score(row["external_false_memory_risk"])

    ohri = clamp(
        0.18 * (1 - claim)
        + 0.16 * hallucination
        + 0.18 * (1 - gate)
        + 0.14 * (1 - next_action)
        + 0.10 * fm
        + 0.10 * (1 - evidence)
        + 0.08 * (1 - delta)
        + 0.04 * under_review
        + 0.02 * over_review
    )

    oqi = clamp(
        0.20 * evidence
        + 0.20 * gate
        + 0.15 * claim
        + 0.15 * vector
        + 0.10 * delta
        + 0.10 * next_action
        + 0.10 * usefulness
    )

    zpi = clamp(
        0.15 * evidence
        + 0.15 * gate
        + 0.15 * token
        + 0.15 * delta
        + 0.15 * drd_dzr
        + 0.10 * claim
        + 0.10 * vector
        + 0.05 * usefulness
    )

    dzr_external = clamp(
        0.25 * delta
        + 0.20 * drd_dzr
        + 0.20 * gate
        + 0.15 * token
        + 0.10 * evidence
        + 0.10 * claim
    )

    return {
        "external_ohri": round(ohri, 4),
        "external_oqi": round(oqi, 4),
        "external_zpi": round(zpi, 4),
        "external_dzr_reasoned": round(dzr_external, 4)
    }

def avg(vals):
    vals = [float(v) for v in vals if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None

def summarize(rows):
    return {
        "case_count": len(rows),
        "avg_external_ohri": avg([r.get("external_ohri") for r in rows]),
        "avg_external_oqi": avg([r.get("external_oqi") for r in rows]),
        "avg_external_zpi": avg([r.get("external_zpi") for r in rows]),
        "avg_external_dzr_reasoned": avg([r.get("external_dzr_reasoned") for r in rows]),
        "accepted_count": sum(1 for r in rows if parse_bool(r.get("external_accept_for_calibration_signal")) is True),
        "hallucination_risk_count": sum(1 for r in rows if parse_bool(r.get("external_hallucination_risk_flag")) is True),
        "over_review_count": sum(1 for r in rows if parse_bool(r.get("external_over_review_flag")) is True),
        "under_review_count": sum(1 for r in rows if parse_bool(r.get("external_under_review_flag")) is True)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.input, "r", encoding="utf-8")))
    complete = []
    incomplete = []

    for row in rows:
        missing = [f for f in REQUIRED_FIELDS if row.get(f) is None or str(row.get(f)).strip() == ""]
        invalid = []

        for f in SCORE_FIELDS:
            if row.get(f) not in [None, ""] and parse_score(row.get(f)) is None:
                invalid.append(f)

        for f in BOOL_FIELDS:
            if row.get(f) not in [None, ""] and parse_bool(row.get(f)) is None:
                invalid.append(f)

        if row.get("external_false_memory_risk") not in [None, ""] and false_memory_score(row.get("external_false_memory_risk")) is None:
            invalid.append("external_false_memory_risk")

        if missing or invalid:
            row["_external_score_complete"] = False
            row["_missing_external_score_fields"] = missing
            row["_invalid_external_score_fields"] = invalid
            incomplete.append(row)
            continue

        row.update(score_indices(row))
        row["_external_score_complete"] = True
        row["_missing_external_score_fields"] = []
        row["_invalid_external_score_fields"] = []
        complete.append(row)

    by_mode = defaultdict(list)
    by_domain = defaultdict(list)
    for row in complete:
        by_mode[row.get("mode")].append(row)
        by_domain[row.get("domain")].append(row)

    all_ready = len(rows) == 36 and len(complete) == 36

    result = {
        "version": "casulo_delta_zero_external_evaluator_score_result.v0.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all_ready else "BLOCKED_MISSING_EXTERNAL_SCORES",
        "case_count": len(rows),
        "complete_external_score_count": len(complete),
        "incomplete_external_score_count": len(incomplete),
        "final_indices_ready": all_ready,
        "external_evaluator_required": True,
        "validated_model_gain_claim": False,
        "validated_hallucination_reduction_claim": False,
        "delta_zero_ready_validated": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "by_mode": {k: summarize(v) for k, v in sorted(by_mode.items())},
        "by_domain": {k: summarize(v) for k, v in sorted(by_domain.items())},
        "scored_rows": complete,
        "incomplete_cases": [
            {
                "case_id": r.get("case_id"),
                "domain": r.get("domain"),
                "mode": r.get("mode"),
                "missing": r.get("_missing_external_score_fields"),
                "invalid": r.get("_invalid_external_score_fields")
            }
            for r in incomplete
        ]
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "case_count": result["case_count"],
        "complete_external_score_count": result["complete_external_score_count"],
        "incomplete_external_score_count": result["incomplete_external_score_count"],
        "final_indices_ready": result["final_indices_ready"],
        "output": str(out)
    }, indent=2, ensure_ascii=False))

    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
