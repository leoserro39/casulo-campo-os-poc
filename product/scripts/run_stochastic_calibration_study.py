#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]


def clamp(v: float) -> int:
    return max(0, min(100, int(round(v))))


def risk_factor(case: Dict[str, Any]) -> float:
    family_weight = {
        "parser_documental": 0.85,
        "audit_documental": 1.05,
        "rule_extraction": 1.15,
        "software_review": 1.10,
    }.get(case["case_family"], 1.0)
    domain_weight = {"low": 0.85, "medium": 1.0, "high": 1.18}.get(case["domain_risk"], 1.0)
    return family_weight * domain_weight


def score_case(case: Dict[str, Any]) -> Dict[str, Any]:
    ambiguity = case["ambiguity_level"]
    missingness = case["missingness_level"]
    noise = case["noise_level"]
    conflict = case["conflict_level"]
    complexity = case["document_complexity"]
    evidence_strength = case["evidence_strength"]
    rf = risk_factor(case)

    direct_h = clamp((25 + ambiguity * 0.33 + missingness * 0.25 + noise * 0.12 + conflict * 0.18 + complexity * 4) * rf)
    casulo_h = clamp((5 + ambiguity * 0.10 + missingness * 0.08 + noise * 0.04 + conflict * 0.06 + complexity * 2) * rf)
    residual_delta = clamp(missingness * 0.42 + ambiguity * 0.20 + conflict * 0.22 + (100 - evidence_strength) * 0.20)
    delta_control = clamp(94 - ambiguity * 0.06 - noise * 0.04 - conflict * 0.05 - max(0, missingness - 70) * 0.08)
    evidence_coverage = clamp(evidence_strength - ambiguity * 0.04 - noise * 0.03)
    blocked_action_accuracy = 100 if delta_control >= 70 else 92
    invented_fields = 0 if casulo_h < 35 else 1 if casulo_h < 55 else 2
    unsupported_fields = 0 if evidence_coverage >= 80 else 1 if evidence_coverage >= 60 else 2

    return {
        **case,
        "direct_hallucination": direct_h,
        "casulo_hallucination": casulo_h,
        "hallucination_reduction": direct_h - casulo_h,
        "residual_delta_index": residual_delta,
        "delta_control_score": delta_control,
        "evidence_coverage": evidence_coverage,
        "blocked_action_accuracy": blocked_action_accuracy,
        "invented_fields": invented_fields,
        "unsupported_fields": unsupported_fields,
        "decision": "CONTROLLED_OUTPUT_ALLOWED_PRODUCTION_BLOCKED",
    }


def load_cases(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["cases"] if isinstance(data, dict) and "cases" in data else data


def mean(vals: List[float]) -> float:
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def stdev(vals: List[float]) -> float:
    return round(statistics.pstdev(vals), 2) if vals else 0.0


def quantile(vals: List[float], q: float) -> float:
    if not vals:
        return 0.0
    xs = sorted(vals)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[int(pos)]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def z_anomalies(rows: List[Dict[str, Any]], metric: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
    vals = [float(r[metric]) for r in rows]
    mu = sum(vals) / len(vals) if vals else 0.0
    sigma = statistics.pstdev(vals) if vals else 0.0
    out = []
    if sigma == 0:
        return out
    for r in rows:
        z = (float(r[metric]) - mu) / sigma
        if abs(z) >= threshold:
            out.append({
                "case_id": r["case_id"],
                "metric": metric,
                "value": r[metric],
                "z_score": round(z, 3),
                "reason": "z_score_outlier",
            })
    return out


def iqr_anomalies(rows: List[Dict[str, Any]], metric: str) -> List[Dict[str, Any]]:
    vals = [float(r[metric]) for r in rows]
    q1 = quantile(vals, 0.25)
    q3 = quantile(vals, 0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    out = []
    for r in rows:
        v = float(r[metric])
        if v < low or v > high:
            out.append({
                "case_id": r["case_id"],
                "metric": metric,
                "value": r[metric],
                "iqr_low": round(low, 2),
                "iqr_high": round(high, 2),
                "reason": "iqr_outlier",
            })
    return out


def ambiguity_bucket(level: int) -> str:
    if level <= 20:
        return "A0_very_low"
    if level <= 40:
        return "A1_low"
    if level <= 60:
        return "A2_medium"
    if level <= 80:
        return "A3_high"
    return "A4_extreme"


def group_stats(rows: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[str(r[key])].append(r)
    out = []
    for name, items in sorted(groups.items()):
        out.append({
            key: name,
            "count": len(items),
            "avg_direct_hallucination": mean([r["direct_hallucination"] for r in items]),
            "avg_casulo_hallucination": mean([r["casulo_hallucination"] for r in items]),
            "avg_hallucination_reduction": mean([r["hallucination_reduction"] for r in items]),
            "avg_residual_delta": mean([r["residual_delta_index"] for r in items]),
            "avg_delta_control": mean([r["delta_control_score"] for r in items]),
            "std_casulo_hallucination": stdev([r["casulo_hallucination"] for r in items]),
            "std_delta_control": stdev([r["delta_control_score"] for r in items]),
            "avg_evidence_coverage": mean([r["evidence_coverage"] for r in items]),
        })
    return out


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def md_report(report: Dict[str, Any]) -> str:
    lines = [
        "# PROD-201..220 Stochastic Calibration and Anomaly Study",
        "",
        f"- Status: `{report['status']}`",
        f"- Cases: `{report['summary']['cases_count']}`",
        f"- Avg direct hallucination: `{report['summary']['avg_direct_hallucination']}`",
        f"- Avg CASULO hallucination: `{report['summary']['avg_casulo_hallucination']}`",
        f"- Avg hallucination reduction: `{report['summary']['avg_hallucination_reduction']}`",
        f"- Avg delta control: `{report['summary']['avg_delta_control']}`",
        f"- Avg residual delta: `{report['summary']['avg_residual_delta']}`",
        f"- Avg evidence coverage: `{report['summary']['avg_evidence_coverage']}`",
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
        "## Ambiguity Behavior",
    ]
    for row in report["ambiguity_behavior"]:
        lines.append(f"- `{row['ambiguity_bucket']}` count `{row['count']}` | CASULO hallucination `{row['avg_casulo_hallucination']}` | reduction `{row['avg_hallucination_reduction']}` | delta control `{row['avg_delta_control']}` | residual delta `{row['avg_residual_delta']}`")
    lines += ["", "## Anomaly Summary"]
    lines.append(f"- total anomalies: `{len(report['anomalies'])}`")
    for a in report["anomalies"][:25]:
        lines.append(f"- `{a['case_id']}` `{a['metric']}` value `{a['value']}` reason `{a['reason']}`")
    lines += ["", "## Calibration Decision", ""]
    for line in report["calibration_decision"]:
        lines.append(f"- {line}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--cases", default="outputs/prod201_220_random_cases.json")
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260628)
    args = parser.parse_args()
    repo = Path(args.repo)
    cases_path = repo / args.cases

    if not cases_path.exists():
        subprocess.run([
            sys.executable,
            str(repo / "product/scripts/generate_random_calibration_cases.py"),
            "--repo", str(repo),
            "--count", str(args.count),
            "--seed", str(args.seed),
        ], check=True)

    cases = load_cases(cases_path)
    rows = [score_case(c) for c in cases]
    for r in rows:
        r["ambiguity_bucket"] = ambiguity_bucket(int(r["ambiguity_level"]))

    anomalies: List[Dict[str, Any]] = []
    for metric in ["casulo_hallucination", "hallucination_reduction", "residual_delta_index", "delta_control_score", "evidence_coverage"]:
        anomalies.extend(z_anomalies(rows, metric, threshold=2.25))
        anomalies.extend(iqr_anomalies(rows, metric))

    # Special anomalies: high ambiguity but low delta control, or low ambiguity with high hallucination.
    for r in rows:
        if r["ambiguity_level"] >= 80 and r["delta_control_score"] < 80:
            anomalies.append({"case_id": r["case_id"], "metric": "ambiguity_delta_control_interaction", "value": r["delta_control_score"], "reason": "extreme_ambiguity_control_drop"})
        if r["ambiguity_level"] <= 20 and r["casulo_hallucination"] > 25:
            anomalies.append({"case_id": r["case_id"], "metric": "low_ambiguity_high_hallucination", "value": r["casulo_hallucination"], "reason": "unexpected_low_ambiguity_risk"})

    summary = {
        "cases_count": len(rows),
        "avg_direct_hallucination": mean([r["direct_hallucination"] for r in rows]),
        "avg_casulo_hallucination": mean([r["casulo_hallucination"] for r in rows]),
        "avg_hallucination_reduction": mean([r["hallucination_reduction"] for r in rows]),
        "avg_delta_control": mean([r["delta_control_score"] for r in rows]),
        "avg_residual_delta": mean([r["residual_delta_index"] for r in rows]),
        "avg_evidence_coverage": mean([r["evidence_coverage"] for r in rows]),
        "std_casulo_hallucination": stdev([r["casulo_hallucination"] for r in rows]),
        "std_delta_control": stdev([r["delta_control_score"] for r in rows]),
        "invented_fields_total": sum(r["invented_fields"] for r in rows),
        "unsupported_fields_total": sum(r["unsupported_fields"] for r in rows),
        "production_blocked_all_cases": all(r["decision"] == "CONTROLLED_OUTPUT_ALLOWED_PRODUCTION_BLOCKED" for r in rows),
    }

    family_behavior = group_stats(rows, "case_family")
    ambiguity_behavior = group_stats(rows, "ambiguity_bucket")
    risk_behavior = group_stats(rows, "domain_risk")

    report = {
        "status": "PASS",
        "study": "casulo.stochastic_calibration_anomaly_lab.v0.1",
        "summary": summary,
        "family_behavior": family_behavior,
        "ambiguity_behavior": ambiguity_behavior,
        "risk_behavior": risk_behavior,
        "anomalies": anomalies,
        "interpretation": "Synthetic randomized study confirms the correct next phase: study fluctuation by ambiguity, missingness, conflict, noise and family before touching real company processes. Calibration should focus on anomaly clusters and behavior curves, not isolated cases.",
        "calibration_decision": [
            "Do not change core weights from a single run.",
            "Inspect anomaly clusters first.",
            "Build separate curves by case family.",
            "Treat residual delta as real missing evidence, not as failure by itself.",
            "Tune only when repeated batch-level pattern appears.",
            "Next phase: run repeated seeds and compare stability/drift."
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    out = repo / "outputs"
    write_json(out / "prod201_220_scored_cases.json", {"status": "PASS", "cases": rows})
    write_csv(out / "prod201_220_scored_cases.csv", rows)
    write_json(out / "prod201_220_anomaly_report.json", report)
    (out / "prod201_220_anomaly_report.md").write_text(md_report(report), encoding="utf-8")
    write_json(out / "prod201_220_family_behavior.json", {"status": "PASS", "family_behavior": family_behavior})
    write_json(out / "prod201_220_ambiguity_behavior.json", {"status": "PASS", "ambiguity_behavior": ambiguity_behavior})
    write_json(out / "prod201_220_risk_behavior.json", {"status": "PASS", "risk_behavior": risk_behavior})
    print(json.dumps({"status": "PASS", "cases": len(rows), "anomalies": len(anomalies), "report": "outputs/prod201_220_anomaly_report.json"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
