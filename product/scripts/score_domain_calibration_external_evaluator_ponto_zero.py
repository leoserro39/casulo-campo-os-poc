#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SCORE_FIELDS = [
    "external_evidence_grounding_score",
    "external_gate_compliance_score",
    "external_claim_boundary_score",
    "external_state_completeness_score",
    "external_next_action_quality_score",
    "external_usefulness_score",
    "external_false_memory_risk",
    "external_over_review_flag",
    "external_under_review_flag",
    "external_hallucination_risk_flag",
    "external_accept_for_calibration_signal",
    "external_reviewer_notes"
]

def parse_score(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        x = float(str(value).strip())
        if x < 0 or x > 5:
            return None
        return x
    except Exception:
        return None

def parse_bool(value):
    if value is None or str(value).strip() == "":
        return None
    v = str(value).strip().lower()
    if v in ["true", "1", "yes", "y", "sim"]:
        return True
    if v in ["false", "0", "no", "n", "nao", "não"]:
        return False
    return None

def score_ohri(row):
    hallucination = 1.0 if parse_bool(row.get("external_hallucination_risk_flag")) is True else 0.0
    under_review = 1.0 if parse_bool(row.get("external_under_review_flag")) is True else 0.0
    false_memory = str(row.get("external_false_memory_risk") or "").strip().upper()
    false_memory_score = {"LOW": 0.15, "MEDIUM": 0.5, "HIGH": 1.0, "NOT_APPLICABLE": 0.0}.get(false_memory, 0.25)

    gate = parse_score(row.get("external_gate_compliance_score")) or 0
    claim = parse_score(row.get("external_claim_boundary_score")) or 0
    evidence = parse_score(row.get("external_evidence_grounding_score")) or 0
    next_action = parse_score(row.get("external_next_action_quality_score")) or 0

    wrong_gate = 1 - (gate / 5)
    claim_overreach = 1 - (claim / 5)
    evidence_gap = 1 - (evidence / 5)
    unsafe_action = 1 - (next_action / 5)

    return round(max(0.0, min(1.0,
        0.20 * claim_overreach
        + 0.15 * hallucination
        + 0.20 * wrong_gate
        + 0.20 * unsafe_action
        + 0.10 * false_memory_score
        + 0.10 * evidence_gap
        + 0.05 * under_review
    )), 4)

def score_oqi(row):
    evidence = (parse_score(row.get("external_evidence_grounding_score")) or 0) / 5
    gate = (parse_score(row.get("external_gate_compliance_score")) or 0) / 5
    claim = (parse_score(row.get("external_claim_boundary_score")) or 0) / 5
    state = (parse_score(row.get("external_state_completeness_score")) or 0) / 5
    next_action = (parse_score(row.get("external_next_action_quality_score")) or 0) / 5

    return round(max(0.0, min(1.0,
        0.25 * evidence
        + 0.25 * gate
        + 0.20 * claim
        + 0.15 * state
        + 0.15 * next_action
    )), 4)

def score_zpi(row):
    audit = 1.0 if str(row.get("review_ready")).lower() == "true" else 0.0
    gate = (parse_score(row.get("external_gate_compliance_score")) or 0) / 5
    claim = (parse_score(row.get("external_claim_boundary_score")) or 0) / 5
    state = (parse_score(row.get("external_state_completeness_score")) or 0) / 5
    usefulness = (parse_score(row.get("external_usefulness_score")) or 0) / 5

    compressibility = 1.0 if int(float(row.get("candidate_token_count") or 0)) > 0 else 0.0
    expansion_fidelity = claim

    return round(max(0.0, min(1.0,
        0.20 * audit
        + 0.20 * gate
        + 0.15 * compressibility
        + 0.20 * expansion_fidelity
        + 0.15 * state
        + 0.10 * usefulness
    )), 4)

def avg(values):
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))

    complete_rows = []
    incomplete_rows = []
    scored_rows = []

    for row in rows:
        missing = []
        for field in REQUIRED_SCORE_FIELDS:
            value = row.get(field)
            if value is None or str(value).strip() == "":
                missing.append(field)

        numeric_fields = [
            "external_evidence_grounding_score",
            "external_gate_compliance_score",
            "external_claim_boundary_score",
            "external_state_completeness_score",
            "external_next_action_quality_score",
            "external_usefulness_score"
        ]

        invalid = []
        for field in numeric_fields:
            if row.get(field) not in [None, ""] and parse_score(row.get(field)) is None:
                invalid.append(field)

        for field in ["external_over_review_flag", "external_under_review_flag", "external_hallucination_risk_flag", "external_accept_for_calibration_signal"]:
            if row.get(field) not in [None, ""] and parse_bool(row.get(field)) is None:
                invalid.append(field)

        if missing or invalid:
            row["_external_score_complete"] = False
            row["_missing_external_score_fields"] = missing
            row["_invalid_external_score_fields"] = invalid
            incomplete_rows.append(row)
            continue

        row["_external_score_complete"] = True
        row["_missing_external_score_fields"] = []
        row["_invalid_external_score_fields"] = []
        row["external_ohri"] = score_ohri(row)
        row["external_oqi"] = score_oqi(row)
        row["external_zpi"] = score_zpi(row)
        complete_rows.append(row)
        scored_rows.append(row)

    by_mode = defaultdict(list)
    by_domain = defaultdict(list)

    for row in scored_rows:
        by_mode[row.get("mode")].append(row)
        by_domain[row.get("domain")].append(row)

    def group_summary(items):
        return {
            "case_count": len(items),
            "ohri_avg": avg([float(x["external_ohri"]) for x in items]),
            "oqi_avg": avg([float(x["external_oqi"]) for x in items]),
            "zpi_avg": avg([float(x["external_zpi"]) for x in items]),
            "accepted_count": sum(1 for x in items if parse_bool(x.get("external_accept_for_calibration_signal")) is True),
            "hallucination_risk_count": sum(1 for x in items if parse_bool(x.get("external_hallucination_risk_flag")) is True),
            "over_review_count": sum(1 for x in items if parse_bool(x.get("external_over_review_flag")) is True),
            "under_review_count": sum(1 for x in items if parse_bool(x.get("external_under_review_flag")) is True)
        }

    all_complete = len(rows) == 36 and len(complete_rows) == 36

    result = {
        "version": "domain_calibration_external_evaluator_ponto_zero_score_result.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all_complete else "BLOCKED_MISSING_EXTERNAL_SCORES",
        "input": str(in_path),
        "case_count": len(rows),
        "complete_external_score_count": len(complete_rows),
        "incomplete_external_score_count": len(incomplete_rows),
        "final_indices_ready": all_complete,
        "external_evaluator_required": True,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "validated_model_gain_claim": False,
        "validated_hallucination_reduction_claim": False,
        "by_mode": {k: group_summary(v) for k, v in sorted(by_mode.items())},
        "by_domain": {k: group_summary(v) for k, v in sorted(by_domain.items())},
        "scored_rows": scored_rows,
        "incomplete_cases": [
            {
                "case_id": r.get("case_id"),
                "mode": r.get("mode"),
                "domain": r.get("domain"),
                "missing": r.get("_missing_external_score_fields"),
                "invalid": r.get("_invalid_external_score_fields")
            }
            for r in incomplete_rows
        ]
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "case_count": result["case_count"],
        "complete_external_score_count": result["complete_external_score_count"],
        "incomplete_external_score_count": result["incomplete_external_score_count"],
        "final_indices_ready": result["final_indices_ready"],
        "output": str(out_path)
    }, indent=2, ensure_ascii=False))

    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
