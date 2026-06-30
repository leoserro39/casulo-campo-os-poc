#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2541..2580"
REQ_TAG = "product-memory-governor-synthetic-benchmark-evaluator-v0.1"

EVAL_OUT = ROOT / "outputs/prod2501_2540_memory_governor_synthetic_benchmark_evaluator.json"
DATASET_OUT = ROOT / "outputs/prod2461_2500_memory_governor_synthetic_benchmark_dataset.json"
BENCH_OUT = ROOT / "outputs/prod2421_2460_context_lifecycle_memory_governor_benchmark.json"

DOC = ROOT / "docs/product/565_MEMORY_GOVERNOR_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/memory_governor_readiness_gate.contract.json"
SCHEMA = ROOT / "product/schemas/memory_governor_readiness_gate.schema.json"
GATE = ROOT / "product/memory/MEMORY_GOVERNOR_READINESS_GATE.md"
OUT_JSON = ROOT / "outputs/prod2541_2580_memory_governor_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod2541_2580_memory_governor_readiness_gate.md"

BLOCKED = [
    "validated_performance_claim",
    "real_world_token_savings_claim",
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "gpt_memory_api_execution",
    "production_activation",
    "client_facing_claim"
]

ALLOWED = [
    "internal_research_continuation",
    "synthetic_benchmark_review",
    "manual_snapshot_policy_design",
    "memory_lifecycle_contract_design",
    "future_controlled_real_session_plan"
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

def main():
    errors = []

    evaluator = read_json(EVAL_OUT) if EVAL_OUT.exists() else {}
    dataset = read_json(DATASET_OUT) if DATASET_OUT.exists() else {}
    benchmark = read_json(BENCH_OUT) if BENCH_OUT.exists() else {}

    checks_source = evaluator.get("checks", {})
    improved = checks_source.get("improved_metric_count", 0)
    metrics = checks_source.get("metric_count", 0)
    records = checks_source.get("record_count", 0)

    decision = "APPROVED_FOR_INTERNAL_RESEARCH_AND_CONTROLLED_BENCHMARK_ONLY"

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "readiness_gate",
        "decision": decision,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "readiness_summary": {
            "synthetic_benchmark_contract_ready": benchmark.get("status") == "PASS",
            "synthetic_dataset_ready": dataset.get("status") == "PASS",
            "synthetic_evaluator_ready": evaluator.get("status") == "PASS",
            "synthetic_improved_metrics": improved,
            "synthetic_metric_count": metrics,
            "synthetic_record_count": records
        },
        "claim_boundary": {
            "can_claim_internal_synthetic_fixture_improvement": True,
            "can_claim_real_world_token_savings": False,
            "can_claim_longer_real_chat_lifetime": False,
            "can_claim_production_readiness": False,
            "can_claim_client_validated_evidence": False,
            "can_mutate_real_memory_without_review": False
        },
        "recommended_next_phase": "PROD-2581..2620 - Manual Context Snapshot Policy Contract"
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Memory Governor Readiness Gate",
        "type": "object",
        "required": ["status", "phase", "decision", "checks", "blocked_actions"]
    }

    doc = """# PROD-2541..2580 - Memory Governor Readiness Gate

Gate for the Memory State Governor benchmark line.

Decision: approved for internal research and controlled benchmark only.

This does not approve real-world performance claims, automatic memory deletion, unreviewed memory mutation, GPT memory API execution, production activation or client-facing claims.
"""

    gate_text = f"""# CASULO Memory Governor Readiness Gate

Decision:
{decision}

Allowed:
- internal research continuation
- synthetic benchmark review
- manual snapshot policy design
- memory lifecycle contract design
- future controlled real session plan

Blocked:
- validated performance claim
- real-world token savings claim
- automatic memory delete
- unreviewed memory mutation
- GPT memory API execution
- production activation
- client-facing claim

Synthetic status:
- records: {records}
- metrics: {metrics}
- improved synthetic metrics: {improved}

Next:
PROD-2581..2620 - Manual Context Snapshot Policy Contract
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write(GATE, gate_text)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "benchmark_pass": benchmark.get("status") == "PASS",
        "dataset_pass": dataset.get("status") == "PASS",
        "evaluator_pass": evaluator.get("status") == "PASS",
        "record_count": records,
        "metric_count": metrics,
        "improved_metric_count": improved,
        "allowed_action_count": len(ALLOWED),
        "blocked_action_count": len(BLOCKED),
        "performance_claim_blocked": "validated_performance_claim" in BLOCKED,
        "token_savings_claim_blocked": "real_world_token_savings_claim" in BLOCKED,
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "unreviewed_mutation_blocked": "unreviewed_memory_mutation" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED,
        "production_blocked": "production_activation" in BLOCKED,
        "client_claim_blocked": "client_facing_claim" in BLOCKED,
        "real_claims_false": contract["claim_boundary"]["can_claim_real_world_token_savings"] is False,
        "memory_mutation_false": contract["claim_boundary"]["can_mutate_real_memory_without_review"] is False
    }

    if checks["record_count"] < 8:
        errors.append("record_count below 8")
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
        "decision": decision if status == "PASS" else "MEMORY_GOVERNOR_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "readiness_summary": contract["readiness_summary"],
        "claim_boundary": contract["claim_boundary"],
        "recommended_next_phase": contract["recommended_next_phase"],
        "checks": checks,
        "errors": errors
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2541..2580 Memory Governor Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Records: `{records}`",
        f"- Metrics: `{metrics}`",
        f"- Improved synthetic metrics: `{improved}`",
        f"- Next: `{contract['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Approved only for internal research and controlled benchmark.",
        "- No real-world token savings claim.",
        "- No validated performance claim.",
        "- No automatic memory deletion.",
        "- No GPT memory API execution.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("records:", records)
    print("metrics:", metrics)
    print("improved_metrics:", improved)
    print("next:", contract["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
