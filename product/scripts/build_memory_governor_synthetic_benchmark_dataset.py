#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2461..2500"
REQ_TAG = "product-context-lifecycle-memory-governor-benchmark-v0.1"

BENCH = ROOT / "outputs/prod2421_2460_context_lifecycle_memory_governor_benchmark.json"
DOC = ROOT / "docs/product/563_MEMORY_GOVERNOR_SYNTHETIC_BENCHMARK_DATASET.md"
CONTRACT = ROOT / "product/contracts/memory_governor_synthetic_benchmark_dataset.contract.json"
SCHEMA = ROOT / "product/schemas/memory_governor_synthetic_benchmark_dataset.schema.json"
DATASET = ROOT / "product/memory/memory_governor_synthetic_benchmark_dataset_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2461_2500_memory_governor_synthetic_benchmark_dataset.json"
OUT_MD = ROOT / "outputs/prod2461_2500_memory_governor_synthetic_benchmark_dataset.md"

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "validated_performance_claim",
    "production_activation",
    "client_facing_claim",
    "gpt_memory_api_execution"
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

def synthetic_records(prompt_pairs):
    records = []
    for pair in prompt_pairs:
        pid = pair["id"]
        theme = pair["theme"]

        records.append({
            "id": pid + "-PURE",
            "pair_id": pid,
            "variant": "PURE_HEAVY_CHAT",
            "theme": theme,
            "condition": pair["pure_condition"],
            "expected_failure_mode": "context_bloat_or_stale_context_contamination",
            "simulated_metrics": {
                "usable_turns_until_degradation": 18,
                "token_growth_rate": 1.0,
                "context_compression_ratio": 1.0,
                "state_retention_score": 0.62,
                "decision_recall_accuracy": 0.58,
                "stale_context_contamination_rate": 0.31,
                "recovery_time_from_snapshot": None,
                "output_quality_under_load": 0.61,
                "rework_avoided": 0.0,
                "cost_per_valid_task": 1.0,
                "gate_violation_rate": 0.18
            }
        })

        records.append({
            "id": pid + "-CASULO",
            "pair_id": pid,
            "variant": "CASULO_STATE_GOVERNED_MEMORY",
            "theme": theme,
            "condition": pair["casulo_condition"],
            "expected_control": "snapshot_gates_operational_cube_repo_pointers",
            "simulated_metrics": {
                "usable_turns_until_degradation": 44,
                "token_growth_rate": 0.42,
                "context_compression_ratio": 0.28,
                "state_retention_score": 0.91,
                "decision_recall_accuracy": 0.93,
                "stale_context_contamination_rate": 0.07,
                "recovery_time_from_snapshot": 0.22,
                "output_quality_under_load": 0.88,
                "rework_avoided": 0.36,
                "cost_per_valid_task": 0.54,
                "gate_violation_rate": 0.04
            }
        })

    return records

def main():
    errors = []
    bench = read_json(BENCH) if BENCH.exists() else {}
    benchmark = bench.get("benchmark", {})
    prompt_pairs = benchmark.get("prompt_pairs", [])
    metrics = benchmark.get("metrics", [])
    gates = benchmark.get("gates", [])

    records = synthetic_records(prompt_pairs)

    dataset = {
        "version": "memory_governor_synthetic_benchmark_dataset.v0.1",
        "phase": PHASE,
        "dataset_type": "synthetic_controlled_fixture",
        "important_boundary": "Synthetic dataset only. Does not prove real performance.",
        "baseline_variant": "PURE_HEAVY_CHAT",
        "casulo_variant": "CASULO_STATE_GOVERNED_MEMORY",
        "metrics": metrics,
        "gates": gates,
        "records": records,
        "recommended_next_phase": "PROD-2501..2540 - Memory Governor Synthetic Benchmark Evaluator"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "synthetic_dataset_only",
        "allowed_claims": [
            "synthetic dataset created",
            "benchmark variants represented",
            "metrics are ready for evaluator testing"
        ],
        "prohibited_claims": [
            "validated token reduction",
            "validated chat lifetime improvement",
            "validated performance improvement",
            "real memory deletion performed",
            "GPT memory integration performed"
        ],
        "blocked_actions": BLOCKED,
        "recommended_next_phase": dataset["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Memory Governor Synthetic Benchmark Dataset",
        "type": "object",
        "required": ["version", "dataset_type", "metrics", "gates", "records"]
    }

    doc = """# PROD-2461..2500 - Memory Governor Synthetic Benchmark Dataset

Creates the controlled synthetic dataset for the Memory State Governor benchmark.

It compares PURE_HEAVY_CHAT versus CASULO_STATE_GOVERNED_MEMORY.

Boundary: synthetic fixture only. No real performance claim, no memory deletion and no GPT memory API execution.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(DATASET, dataset)

    variants = {r["variant"] for r in records}
    pair_ids = {r["pair_id"] for r in records}
    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "prior_benchmark_pass": bench.get("status") == "PASS",
        "prompt_pair_count": len(prompt_pairs),
        "metric_count": len(metrics),
        "gate_count": len(gates),
        "record_count": len(records),
        "has_pure_variant": "PURE_HEAVY_CHAT" in variants,
        "has_casulo_variant": "CASULO_STATE_GOVERNED_MEMORY" in variants,
        "two_records_per_pair": len(records) == len(prompt_pairs) * 2,
        "all_pairs_represented": len(pair_ids) == len(prompt_pairs),
        "has_token_metric": "token_growth_rate" in metrics,
        "has_recall_metric": "decision_recall_accuracy" in metrics,
        "has_contamination_metric": "stale_context_contamination_rate" in metrics,
        "has_gate_metric": "gate_violation_rate" in metrics,
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "performance_claim_blocked": "validated_performance_claim" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED
    }

    if checks["prompt_pair_count"] < 4:
        errors.append("prompt_pair_count below 4")
    if checks["metric_count"] < 10:
        errors.append("metric_count below 10")
    if checks["record_count"] < 8:
        errors.append("record_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "MEMORY_GOVERNOR_SYNTHETIC_DATASET_READY" if status == "PASS" else "MEMORY_GOVERNOR_SYNTHETIC_DATASET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "path": "product/memory/memory_governor_synthetic_benchmark_dataset_v0_1.json",
            "record_count": len(records),
            "prompt_pair_count": len(prompt_pairs),
            "metric_count": len(metrics),
            "recommended_next_phase": dataset["recommended_next_phase"],
            "calibration_status": "SYNTHETIC_FIXTURE_NOT_REAL_WORLD_CALIBRATED"
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2461..2500 Memory Governor Synthetic Benchmark Dataset",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Records: `{len(records)}`",
        f"- Prompt pairs: `{len(prompt_pairs)}`",
        f"- Metrics: `{len(metrics)}`",
        f"- Next: `{dataset['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Synthetic fixture only.",
        "- No validated performance claim.",
        "- No memory deletion.",
        "- No GPT memory API execution.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("records:", len(records))
    print("prompt_pairs:", len(prompt_pairs))
    print("metrics:", len(metrics))
    print("next:", dataset["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
