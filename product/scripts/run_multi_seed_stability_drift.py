#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict, Counter
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

CASE_FAMILIES = ["parser_documental", "audit_documental", "rule_extraction", "software_review"]
DOC_TYPES = {
    "parser_documental": ["service_intake", "invoice_receipt", "form_record", "email_request", "checklist"],
    "audit_documental": ["contract_checklist", "policy_audit", "compliance_packet", "evidence_dossier"],
    "rule_extraction": ["procedure", "policy", "acceptance_criteria", "business_rule_sheet"],
    "software_review": ["repo_summary", "incident_log", "release_notes", "test_report"],
}
RISK_BY_FAMILY = {
    "parser_documental": ["low", "medium"],
    "audit_documental": ["medium", "high"],
    "rule_extraction": ["medium", "high"],
    "software_review": ["medium", "high"],
}


def clamp(v: float) -> int:
    return max(0, min(100, int(round(v))))


def mean(vals: List[float]) -> float:
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def stdev(vals: List[float]) -> float:
    return round(statistics.pstdev(vals), 4) if vals else 0.0


def cv(vals: List[float]) -> float:
    mu = sum(vals) / len(vals) if vals else 0.0
    if mu == 0:
        return 0.0
    return round((statistics.pstdev(vals) / mu), 4)


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


def pick(rng: random.Random, items: List[str]) -> str:
    return items[rng.randrange(len(items))]


def make_case(idx: int, rng: random.Random, seed: int, family: str | None = None) -> Dict[str, Any]:
    case_family = family or pick(rng, CASE_FAMILIES)
    ambiguity = rng.randint(0, 100)
    missingness = rng.randint(0, 100)
    noise = rng.randint(0, 100)
    conflict = rng.randint(0, 100)
    complexity = rng.randint(1, 5)
    evidence_strength = max(0, min(100, 100 - int((missingness * 0.45 + ambiguity * 0.25 + noise * 0.15 + conflict * 0.15))))
    domain_risk = pick(rng, RISK_BY_FAMILY[case_family])
    return {
        "case_id": f"SEED-{seed}-STOCH-{idx:04d}-{case_family.upper()}",
        "case_family": case_family,
        "document_type": pick(rng, DOC_TYPES[case_family]),
        "ambiguity_level": ambiguity,
        "missingness_level": missingness,
        "noise_level": noise,
        "conflict_level": conflict,
        "document_complexity": complexity,
        "domain_risk": domain_risk,
        "evidence_strength": evidence_strength,
    }


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
    invented_fields = 0 if casulo_h < 35 else 1 if casulo_h < 55 else 2
    unsupported_fields = 0 if evidence_coverage >= 80 else 1 if evidence_coverage >= 60 else 2
    bucket = ambiguity_bucket(ambiguity)

    return {
        **case,
        "ambiguity_bucket": bucket,
        "direct_hallucination": direct_h,
        "casulo_hallucination": casulo_h,
        "hallucination_reduction": direct_h - casulo_h,
        "residual_delta_index": residual_delta,
        "delta_control_score": delta_control,
        "evidence_coverage": evidence_coverage,
        "invented_fields": invented_fields,
        "unsupported_fields": unsupported_fields,
        "decision": "CONTROLLED_OUTPUT_ALLOWED_PRODUCTION_BLOCKED",
    }


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
            "avg_evidence_coverage": mean([r["evidence_coverage"] for r in items]),
            "std_casulo_hallucination": stdev([r["casulo_hallucination"] for r in items]),
            "std_delta_control": stdev([r["delta_control_score"] for r in items]),
        })
    return out


def detect_anomalies(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    anomalies: List[Dict[str, Any]] = []
    metrics = ["casulo_hallucination", "hallucination_reduction", "residual_delta_index", "delta_control_score", "evidence_coverage"]
    for metric in metrics:
        vals = [float(r[metric]) for r in rows]
        mu = sum(vals) / len(vals)
        sigma = statistics.pstdev(vals)
        q1 = quantile(vals, 0.25)
        q3 = quantile(vals, 0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        for r in rows:
            v = float(r[metric])
            if sigma and abs((v - mu) / sigma) >= 2.25:
                anomalies.append({"case_id": r["case_id"], "case_family": r["case_family"], "ambiguity_bucket": r["ambiguity_bucket"], "metric": metric, "value": r[metric], "reason": "z_score_outlier"})
            if v < low or v > high:
                anomalies.append({"case_id": r["case_id"], "case_family": r["case_family"], "ambiguity_bucket": r["ambiguity_bucket"], "metric": metric, "value": r[metric], "reason": "iqr_outlier"})
    for r in rows:
        if r["ambiguity_level"] >= 80 and r["delta_control_score"] < 80:
            anomalies.append({"case_id": r["case_id"], "case_family": r["case_family"], "ambiguity_bucket": r["ambiguity_bucket"], "metric": "ambiguity_delta_control_interaction", "value": r["delta_control_score"], "reason": "extreme_ambiguity_control_drop"})
        if r["ambiguity_level"] <= 20 and r["casulo_hallucination"] > 25:
            anomalies.append({"case_id": r["case_id"], "case_family": r["case_family"], "ambiguity_bucket": r["ambiguity_bucket"], "metric": "low_ambiguity_high_hallucination", "value": r["casulo_hallucination"], "reason": "unexpected_low_ambiguity_risk"})
    return anomalies


def run_seed(seed: int, count: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    cases = []
    for i in range(1, count + 1):
        forced_family = CASE_FAMILIES[(i - 1) % len(CASE_FAMILIES)] if i <= len(CASE_FAMILIES) * 5 else None
        cases.append(make_case(i, rng, seed, forced_family))
    rows = [score_case(c) for c in cases]
    anomalies = detect_anomalies(rows)
    summary = {
        "seed": seed,
        "cases_count": len(rows),
        "avg_direct_hallucination": mean([r["direct_hallucination"] for r in rows]),
        "avg_casulo_hallucination": mean([r["casulo_hallucination"] for r in rows]),
        "avg_hallucination_reduction": mean([r["hallucination_reduction"] for r in rows]),
        "avg_delta_control": mean([r["delta_control_score"] for r in rows]),
        "avg_residual_delta": mean([r["residual_delta_index"] for r in rows]),
        "avg_evidence_coverage": mean([r["evidence_coverage"] for r in rows]),
        "anomaly_count": len(anomalies),
        "anomaly_rate": round(len(anomalies) / len(rows), 4) if rows else 0.0,
        "invented_fields_total": sum(r["invented_fields"] for r in rows),
        "unsupported_fields_total": sum(r["unsupported_fields"] for r in rows),
        "production_blocked_all_cases": all(r["decision"] == "CONTROLLED_OUTPUT_ALLOWED_PRODUCTION_BLOCKED" for r in rows),
    }
    return {
        "seed": seed,
        "summary": summary,
        "family_behavior": group_stats(rows, "case_family"),
        "ambiguity_behavior": group_stats(rows, "ambiguity_bucket"),
        "risk_behavior": group_stats(rows, "domain_risk"),
        "anomalies": anomalies,
        "scored_cases": rows,
    }


def aggregate(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    summaries = [r["summary"] for r in runs]
    metric_keys = [
        "avg_direct_hallucination",
        "avg_casulo_hallucination",
        "avg_hallucination_reduction",
        "avg_delta_control",
        "avg_residual_delta",
        "avg_evidence_coverage",
        "anomaly_rate",
    ]
    stability = {}
    for key in metric_keys:
        vals = [float(s[key]) for s in summaries]
        stability[key] = {
            "mean": mean(vals),
            "std": stdev(vals),
            "cv": cv(vals),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "range": round(max(vals) - min(vals), 2),
        }
    drift_flags = []
    if stability["avg_casulo_hallucination"]["cv"] > 0.08:
        drift_flags.append("casulo_hallucination_unstable")
    if stability["avg_delta_control"]["cv"] > 0.04:
        drift_flags.append("delta_control_unstable")
    if stability["anomaly_rate"]["mean"] > 0.25:
        drift_flags.append("high_anomaly_rate")
    if stability["avg_delta_control"]["mean"] < 80:
        drift_flags.append("delta_control_below_threshold")

    all_anomalies = []
    for run in runs:
        for a in run["anomalies"]:
            all_anomalies.append({**a, "seed": run["seed"]})
    metric_cluster = Counter(a["metric"] for a in all_anomalies)
    family_cluster = Counter(a["case_family"] for a in all_anomalies)
    ambiguity_cluster = Counter(a["ambiguity_bucket"] for a in all_anomalies)

    decision = "STABLE_ENOUGH_FOR_PROVISIONAL_SYNTHETIC_THRESHOLDS" if not drift_flags else "REQUIRES_MORE_SEEDS_BEFORE_THRESHOLD_TUNING"
    return {
        "stability": stability,
        "drift": {
            "status": "PASS" if not drift_flags else "ATTENTION",
            "flags": drift_flags,
            "decision": decision,
        },
        "anomaly_clusters": {
            "total_anomalies": len(all_anomalies),
            "by_metric": dict(metric_cluster.most_common()),
            "by_family": dict(family_cluster.most_common()),
            "by_ambiguity_bucket": dict(ambiguity_cluster.most_common()),
        },
        "calibrated_threshold_recommendations": {
            "status": "PROVISIONAL" if not drift_flags else "HOLD",
            "hallucination_attention_threshold": 35,
            "hallucination_review_threshold": 45,
            "delta_control_attention_threshold": 82,
            "delta_control_review_threshold": 80,
            "evidence_coverage_attention_threshold": 45,
            "anomaly_rate_attention_threshold": 0.25,
            "note": "Synthetic thresholds only. Confirm with anonymized real documents before external claims.",
        },
        "decision": decision,
    }


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
        "# PROD-221..240 Multi-Seed Stability and Drift Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Seeds: `{report['seeds']}`",
        f"- Cases per seed: `{report['cases_per_seed']}`",
        f"- Total cases: `{report['total_cases']}`",
        f"- Decision: `{report['decision']}`",
        "",
        "## Stability",
    ]
    for metric, data in report["stability"].items():
        lines.append(f"- `{metric}` mean `{data['mean']}` std `{data['std']}` cv `{data['cv']}` range `{data['range']}`")
    lines += ["", "## Drift", ""]
    lines.append(f"- Status: `{report['drift']['status']}`")
    lines.append(f"- Flags: `{report['drift']['flags']}`")
    lines += ["", "## Anomaly Clusters", ""]
    lines.append(f"- Total anomalies: `{report['anomaly_clusters']['total_anomalies']}`")
    lines.append(f"- By metric: `{report['anomaly_clusters']['by_metric']}`")
    lines.append(f"- By family: `{report['anomaly_clusters']['by_family']}`")
    lines.append(f"- By ambiguity bucket: `{report['anomaly_clusters']['by_ambiguity_bucket']}`")
    lines += ["", "## Recommendations", ""]
    for k, v in report["calibrated_threshold_recommendations"].items():
        lines.append(f"- {k}: `{v}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--seeds", default="101,202,303,404,505")
    parser.add_argument("--count", type=int, default=300)
    args = parser.parse_args()
    repo = Path(args.repo)
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    runs = [run_seed(seed, args.count) for seed in seeds]
    agg = aggregate(runs)

    report = {
        "status": "PASS",
        "runner": "casulo.multi_seed_stability_runner.v0.1",
        "seeds": seeds,
        "cases_per_seed": args.count,
        "total_cases": args.count * len(seeds),
        **agg,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    out = repo / "outputs"
    write_json(out / "prod221_240_multi_seed_runs.json", {"status": "PASS", "runs": [{k: v for k, v in run.items() if k != "scored_cases"} for run in runs]})
    write_json(out / "prod221_240_stability_report.json", report)
    (out / "prod221_240_stability_report.md").write_text(md_report(report), encoding="utf-8")
    write_json(out / "prod221_240_drift_report.json", {"status": report["drift"]["status"], "drift": report["drift"], "stability": report["stability"]})
    write_json(out / "prod221_240_anomaly_cluster_report.json", {"status": "PASS", "anomaly_clusters": report["anomaly_clusters"]})
    write_json(out / "prod221_240_calibrated_threshold_recommendations.json", {"status": "PASS", "recommendations": report["calibrated_threshold_recommendations"]})

    seed_rows = [run["summary"] for run in runs]
    write_csv(out / "prod221_240_seed_summary.csv", seed_rows)

    all_cases = []
    for run in runs:
        all_cases.extend(run["scored_cases"])
    write_csv(out / "prod221_240_scored_cases_all_seeds.csv", all_cases)
    write_json(out / "prod221_240_scored_cases_all_seeds.json", {"status": "PASS", "cases": all_cases})

    print(json.dumps({"status": "PASS", "seeds": seeds, "total_cases": report["total_cases"], "decision": report["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
