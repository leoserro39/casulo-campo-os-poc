#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2421..2460"
REQ_TAG = "product-demo-readiness-review-gate-v0.1"

DOC = ROOT / "docs/product/562_CONTEXT_LIFECYCLE_MEMORY_GOVERNOR_BENCHMARK.md"
CONTRACT = ROOT / "product/contracts/context_lifecycle_memory_governor_benchmark.contract.json"
SCHEMA = ROOT / "product/schemas/context_lifecycle_memory_governor_benchmark.schema.json"
MODEL = ROOT / "product/memory/context_lifecycle_memory_governor_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2421_2460_context_lifecycle_memory_governor_benchmark.json"
OUT_MD = ROOT / "outputs/prod2421_2460_context_lifecycle_memory_governor_benchmark.md"

GATES = [
    "PROMOTE_TO_MEMORY",
    "COMPRESS_TO_SNAPSHOT",
    "ARCHIVE_TO_REPO",
    "DISCARD_EPHEMERAL",
    "HOLD_HUMAN_REVIEW",
    "PROTECT_DO_NOT_DELETE"
]

METRICS = [
    "usable_turns_until_degradation",
    "token_growth_rate",
    "context_compression_ratio",
    "state_retention_score",
    "decision_recall_accuracy",
    "stale_context_contamination_rate",
    "recovery_time_from_snapshot",
    "output_quality_under_load",
    "rework_avoided",
    "cost_per_valid_task",
    "gate_violation_rate"
]

PROMPT_PAIRS = [
    {
        "id": "MEM-PAIR-001",
        "theme": "long_task_history",
        "pure_condition": "Chat keeps full logs, failed attempts, commands and outputs active.",
        "casulo_condition": "Chat uses current state snapshot plus repo pointers.",
        "expected_measure": "usable_turns_until_degradation"
    },
    {
        "id": "MEM-PAIR-002",
        "theme": "decision_recall",
        "pure_condition": "Chat recalls commits, tags and decisions from heavy accumulated context.",
        "casulo_condition": "Chat recalls compact state with commit, tag, decision and next gate.",
        "expected_measure": "decision_recall_accuracy"
    },
    {
        "id": "MEM-PAIR-003",
        "theme": "stale_context",
        "pure_condition": "Resolved errors and obsolete commands remain active.",
        "casulo_condition": "Resolved noise is archived or discarded by gate.",
        "expected_measure": "stale_context_contamination_rate"
    },
    {
        "id": "MEM-PAIR-004",
        "theme": "snapshot_recovery",
        "pure_condition": "Chat resumes from long transcript.",
        "casulo_condition": "Chat resumes from state snapshot and repo evidence.",
        "expected_measure": "recovery_time_from_snapshot"
    }
]

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "production_activation",
    "client_facing_claim",
    "validated_performance_claim",
    "gpt_memory_api_execution"
]

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def main():
    errors = []

    thesis = "Memory is not storage. Memory is living state governed by evidence, gates and lifecycle."

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "benchmark_contract_only",
        "thesis": thesis,
        "hypothesis": "State-governed memory increases useful chat lifetime, reduces token waste, improves recall and reduces stale-context contamination.",
        "baseline": "pure_chat_with_heavy_accumulated_context",
        "casulo_stack": "snapshot_plus_gates_plus_operational_cube_repo_pointers",
        "gates": GATES,
        "metrics": METRICS,
        "prompt_pairs": PROMPT_PAIRS,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-2461..2500 - Memory Governor Synthetic Benchmark Dataset"
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Context Lifecycle Memory Governor Benchmark",
        "type": "object",
        "required": ["status", "phase", "decision", "benchmark", "checks", "blocked_actions"]
    }

    model = {
        "version": "context_lifecycle_memory_governor.v0.1",
        "state_types": [
            "canonical_decision",
            "current_phase_state",
            "repo_pointer",
            "evidence_pointer",
            "ephemeral_log",
            "resolved_error",
            "obsolete_command",
            "human_preference",
            "gate_policy"
        ],
        "lifecycle_actions": GATES,
        "memory_policy": {
            "chat_memory": "anchors, decisions, preferences, current state and pointers",
            "operational_cube": "living state, relations, gates and lifecycle decisions",
            "repo_outputs": "auditable heavy evidence, logs, reports and generated artifacts",
            "discardable": "resolved noise, failed attempts, obsolete commands and duplicate outputs"
        }
    }

    doc = """# PROD-2421..2460 - Context Lifecycle Telemetry and Memory State Governor Benchmark

Defines the benchmark for a CASULO Memory State Governor.

The governor treats memory as living operational state, not as a passive storage bucket.

It compares pure heavy chat context against CASULO snapshot, gates and Operational Cube/repo pointers.

Boundary: no automatic memory deletion, no GPT memory API execution, no production and no client-facing performance claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(MODEL, model)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "gate_count": len(GATES),
        "metric_count": len(METRICS),
        "prompt_pair_count": len(PROMPT_PAIRS),
        "has_promote": "PROMOTE_TO_MEMORY" in GATES,
        "has_compress": "COMPRESS_TO_SNAPSHOT" in GATES,
        "has_archive": "ARCHIVE_TO_REPO" in GATES,
        "has_discard": "DISCARD_EPHEMERAL" in GATES,
        "has_hold_review": "HOLD_HUMAN_REVIEW" in GATES,
        "has_protect": "PROTECT_DO_NOT_DELETE" in GATES,
        "has_token_metric": "token_growth_rate" in METRICS,
        "has_retention_metric": "state_retention_score" in METRICS,
        "has_contamination_metric": "stale_context_contamination_rate" in METRICS,
        "has_recovery_metric": "recovery_time_from_snapshot" in METRICS,
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "unreviewed_mutation_blocked": "unreviewed_memory_mutation" in BLOCKED,
        "performance_claim_blocked": "validated_performance_claim" in BLOCKED
    }

    if checks["gate_count"] < 6:
        errors.append("gate_count below 6")
    if checks["metric_count"] < 10:
        errors.append("metric_count below 10")
    if checks["prompt_pair_count"] < 4:
        errors.append("prompt_pair_count below 4")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "MEMORY_STATE_GOVERNOR_BENCHMARK_READY" if status == "PASS" else "MEMORY_STATE_GOVERNOR_BENCHMARK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark": contract,
        "model": model,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2421..2460 Context Lifecycle Memory Governor Benchmark",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Gates: `{len(GATES)}`",
        f"- Metrics: `{len(METRICS)}`",
        f"- Prompt pairs: `{len(PROMPT_PAIRS)}`",
        f"- Next: `{contract['recommended_next_phase']}`",
        "",
        "## Thesis",
        thesis,
        "",
        "## Boundary",
        "- No automatic memory deletion.",
        "- No unreviewed memory mutation.",
        "- No validated performance claim yet.",
        "- Benchmark contract only.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("gates:", len(GATES))
    print("metrics:", len(METRICS))
    print("prompt_pairs:", len(PROMPT_PAIRS))
    print("next:", contract["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
