#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2501..2540"
REQ_TAG = "product-memory-governor-synthetic-benchmark-dataset-v0.1"

DATASET = ROOT / "product/memory/memory_governor_synthetic_benchmark_dataset_v0_1.json"
DOC = ROOT / "docs/product/564_MEMORY_GOVERNOR_SYNTHETIC_BENCHMARK_EVALUATOR.md"
CONTRACT = ROOT / "product/contracts/memory_governor_synthetic_benchmark_evaluator.contract.json"
SCHEMA = ROOT / "product/schemas/memory_governor_synthetic_benchmark_evaluator.schema.json"
EVALUATOR = ROOT / "product/memory/memory_governor_synthetic_benchmark_evaluator_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2501_2540_memory_governor_synthetic_benchmark_evaluator.json"
OUT_MD = ROOT / "outputs/prod2501_2540_memory_governor_synthetic_benchmark_evaluator.md"

BLOCKED = [
    "validated_performance_claim",
    "real_world_token_savings_claim",
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "gpt_memory_api_execution",
    "production_activation",
    "client_facing_claim"
]

HIGHER_IS_BETTER = [
    "usable_turns_until_degradation",
    "context_compression_ratio",
    "state_retention_score",
    "decision_recall_accuracy",
    "output_quality_under_load",
    "rework_avoided"
]

LOWER_IS_BETTER = [
    "token_growth_rate",
    "stale_context_contamination_rate",
    "recovery_time_from_snapshot",
    "cost_per_valid_task",
    "gate_violation_rate"
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def avg(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else None

def delta(pure, casulo, metric):
    p = pure.get(metric)
    c = casulo.get(metric)
    if p is None or c is None:
        return None
    if metric in HIGHER_IS_BETTER:
        return c - p
    if metric in LOWER_IS_BETTER:
        return p - c
    return c - p

def main():
    errors = []
    dataset = read_json(DATASET) if DATASET.exists() else {}
    records = dataset.get("records", [])
    metrics = dataset.get("metrics", [])

    pure = [r for r in records if r.get("variant") == "PURE_HEAVY_CHAT"]
    casulo = [r for r in records if r.get("variant") == "CASULO_STATE_GOVERNED_MEMORY"]

    by_pair = {}
    for r in records:
        by_pair.setdefault(r.get("pair_id"), {})[r.get("variant")] = r

    pair_results = []
    for pair_id, variants in sorted(by_pair.items()):
        p = variants.get("PURE_HEAVY_CHAT", {}).get("simulated_metrics", {})
        c = variants.get("CASULO_STATE_GOVERNED_MEMORY", {}).get("simulated_metrics", {})
        metric_deltas = {m: delta(p, c, m) for m in metrics}
        pair_results.append({
            "pair_id": pair_id,
            "metric_deltas_positive_means_better": metric_deltas,
            "improved_metric_count": sum(1 for v in metric_deltas.values() if isinstance(v, (int, float)) and v > 0),
            "measured_metric_count": sum(1 for v in metric_deltas.values() if isinstance(v, (int, float)))
        })

    aggregate = {}
    for m in metrics:
        pure_avg = avg([r.get("simulated_metrics", {}).get(m) for r in pure])
        casulo_avg = avg([r.get("simulated_metrics", {}).get(m) for r in casulo])
        if pure_avg is None or casulo_avg is None:
            improvement = None
        elif m in HIGHER_IS_BETTER:
            improvement = casulo_avg - pure_avg
        elif m in LOWER_IS_BETTER:
            improvement = pure_avg - casulo_avg
        else:
            improvement = casulo_avg - pure_avg
        aggregate[m] = {
            "pure_avg": pure_avg,
            "casulo_avg": casulo_avg,
            "positive_delta_means_better": improvement
        }

    improved_metrics = [
        m for m, row in aggregate.items()
        if isinstance(row["positive_delta_means_better"], (int, float)) and row["positive_delta_means_better"] > 0
    ]

    evaluator = {
        "version": "memory_governor_synthetic_benchmark_evaluator.v0.1",
        "dataset": "product/memory/memory_governor_synthetic_benchmark_dataset_v0_1.json",
        "interpretation": "All results are synthetic fixture calculations. They do not validate real performance.",
        "higher_is_better": HIGHER_IS_BETTER,
        "lower_is_better": LOWER_IS_BETTER,
        "aggregate": aggregate,
        "pair_results": pair_results,
        "recommended_next_phase": "PROD-2541..2580 - Memory Governor Readiness Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "synthetic_evaluator_only",
        "allowed_claims": [
            "synthetic evaluator calculated fixture metrics",
            "CASULO synthetic variant outperforms pure synthetic variant in the fixture",
            "real-world validation is still required"
        ],
        "prohibited_claims": [
            "validated token savings",
            "validated longer chat lifetime",
            "validated production performance",
            "real memory cleanup performed",
            "GPT memory integration performed"
        ],
        "blocked_actions": BLOCKED,
        "recommended_next_phase": evaluator["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Memory Governor Synthetic Benchmark Evaluator",
        "type": "object",
        "required": ["status", "phase", "decision", "evaluator", "checks", "blocked_actions"]
    }

    doc = """# PROD-2501..2540 - Memory Governor Synthetic Benchmark Evaluator

Evaluates the synthetic Memory State Governor benchmark dataset.

Boundary: synthetic fixture calculation only. No real token savings claim, no real chat-lifetime claim, no memory deletion and no GPT memory API execution.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(EVALUATOR, evaluator)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "dataset_exists": DATASET.exists(),
        "dataset_type_synthetic": dataset.get("dataset_type") == "synthetic_controlled_fixture",
        "record_count": len(records),
        "pure_count": len(pure),
        "casulo_count": len(casulo),
        "metric_count": len(metrics),
        "pair_count": len(by_pair),
        "aggregate_metric_count": len(aggregate),
        "improved_metric_count": len(improved_metrics),
        "has_token_growth": "token_growth_rate" in aggregate,
        "has_decision_recall": "decision_recall_accuracy" in aggregate,
        "has_context_contamination": "stale_context_contamination_rate" in aggregate,
        "has_cost_per_task": "cost_per_valid_task" in aggregate,
        "validated_claim_blocked": "validated_performance_claim" in BLOCKED,
        "token_claim_blocked": "real_world_token_savings_claim" in BLOCKED,
        "memory_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED
    }

    if checks["record_count"] < 8:
        errors.append("record_count below 8")
    if checks["pure_count"] != checks["casulo_count"]:
        errors.append("pure/casulo count mismatch")
    if checks["metric_count"] < 10:
        errors.append("metric_count below 10")
    if checks["improved_metric_count"] < 8:
        errors.append("improved_metric_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "MEMORY_GOVERNOR_SYNTHETIC_EVALUATOR_READY" if status == "PASS" else "MEMORY_GOVERNOR_SYNTHETIC_EVALUATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluator": evaluator,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2501..2540 Memory Governor Synthetic Benchmark Evaluator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Records: `{len(records)}`",
        f"- Metrics: `{len(metrics)}`",
        f"- Improved synthetic metrics: `{len(improved_metrics)}`",
        f"- Next: `{evaluator['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Synthetic fixture only.",
        "- No validated token savings claim.",
        "- No real memory cleanup.",
        "- No GPT memory API execution.",
        "",
        "## Aggregate"
    ]
    for m, row in aggregate.items():
        report.append(f"- `{m}` pure `{row['pure_avg']}` casulo `{row['casulo_avg']}` delta `{row['positive_delta_means_better']}`")
    report += ["", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("records:", len(records))
    print("metrics:", len(metrics))
    print("improved_metrics:", len(improved_metrics))
    print("next:", evaluator["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
