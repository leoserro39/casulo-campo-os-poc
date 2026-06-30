#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2701..2740"
REQ_TAG = "product-exocortex-snapshot-runtime-fixture-pack-v0.1"

PACK = ROOT / "product/memory/snapshots/exocortex_snapshot_runtime_fixture_pack_v0_1.json"
PACK_OUT = ROOT / "outputs/prod2661_2700_exocortex_snapshot_runtime_fixture_pack.json"

DOC = ROOT / "docs/product/569_EXOCORTEX_RUNTIME_SNAPSHOT_EVALUATOR.md"
CONTRACT = ROOT / "product/contracts/exocortex_runtime_snapshot_evaluator.contract.json"
SCHEMA = ROOT / "product/schemas/exocortex_runtime_snapshot_evaluator.schema.json"
EVALUATOR = ROOT / "product/memory/exocortex_runtime_snapshot_evaluator_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2701_2740_exocortex_runtime_snapshot_evaluator.json"
OUT_MD = ROOT / "outputs/prod2701_2740_exocortex_runtime_snapshot_evaluator.md"

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "validated_performance_claim",
    "real_world_token_savings_claim",
    "client_facing_claim",
    "production_activation",
    "gpt_memory_api_execution"
]

RISK_WEIGHT = {
    "low": 10,
    "medium": 30,
    "high": 60,
    "critical": 85
}

ACTION_SCORE = {
    "COMPRESS_TO_SNAPSHOT": 90,
    "DISCARD_EPHEMERAL": 75,
    "ARCHIVE_TO_REPO": 80,
    "HOLD_HUMAN_REVIEW": 95,
    "PROTECT_DO_NOT_DELETE": 100,
    "PROMOTE_TO_MEMORY": 85
}

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

def evaluate_snapshot(snapshot):
    risk = snapshot.get("risk", "medium")
    action = snapshot.get("lifecycle_action")
    gate = snapshot.get("gate", "")
    boundary = snapshot.get("claim_boundary", {})
    blocked = set(snapshot.get("blocked_actions", []))
    signals = snapshot.get("exocortex_signals", {})

    integrity = 0
    integrity += 20 if snapshot.get("state_checksum") else 0
    integrity += 20 if snapshot.get("evidence_pointers") else 0
    integrity += 20 if boundary else 0
    integrity += 20 if len(signals) >= 9 else 0
    integrity += 20 if all(x in blocked for x in BLOCKED) else 0

    boundary_score = 100
    if boundary.get("client_facing_claim_allowed") is not False:
        boundary_score -= 25
    if boundary.get("production_activation_allowed") is not False:
        boundary_score -= 25
    if boundary.get("validated_performance_claim_allowed") is not False:
        boundary_score -= 25
    if boundary.get("real_world_token_savings_claim_allowed") is not False:
        boundary_score -= 25

    action_readiness = ACTION_SCORE.get(action, 50)
    risk_pressure = RISK_WEIGHT.get(risk, 30)

    priority = round(
        (risk_pressure * 0.35)
        + (action_readiness * 0.35)
        + (integrity * 0.20)
        + (boundary_score * 0.10),
        2
    )

    if "CONTRADICTION" in gate:
        verdict = "HOLD_REVIEW_REQUIRED"
    elif action == "PROTECT_DO_NOT_DELETE":
        verdict = "PROTECTED_STATE"
    elif action == "DISCARD_EPHEMERAL":
        verdict = "DISCARD_ALLOWED_AFTER_REVIEW"
    elif action == "COMPRESS_TO_SNAPSHOT":
        verdict = "SNAPSHOT_READY"
    elif action == "ARCHIVE_TO_REPO":
        verdict = "ARCHIVE_READY"
    else:
        verdict = "REVIEW_REQUIRED"

    return {
        "snapshot_id": snapshot.get("snapshot_id"),
        "title": snapshot.get("title"),
        "risk": risk,
        "gate": gate,
        "lifecycle_action": action,
        "response_mode": snapshot.get("response_mode"),
        "integrity_score": integrity,
        "boundary_score": boundary_score,
        "risk_pressure": risk_pressure,
        "action_readiness": action_readiness,
        "priority_score": priority,
        "verdict": verdict
    }

def main():
    errors = []
    pack = read_json(PACK) if PACK.exists() else {}
    pack_out = read_json(PACK_OUT) if PACK_OUT.exists() else {}
    snapshots = pack.get("snapshots", [])

    evaluations = [evaluate_snapshot(s) for s in snapshots]
    verdicts = {e["verdict"] for e in evaluations}

    evaluator = {
        "version": "exocortex_runtime_snapshot_evaluator.v0.1",
        "phase": PHASE,
        "input_pack": "product/memory/snapshots/exocortex_snapshot_runtime_fixture_pack_v0_1.json",
        "scoring": {
            "integrity_score": "state checksum, evidence, claim boundary, signals and blocked actions",
            "boundary_score": "claim and production restrictions",
            "risk_pressure": "risk level weight",
            "action_readiness": "lifecycle action readiness",
            "priority_score": "weighted operational priority"
        },
        "evaluations": evaluations,
        "recommended_next_phase": "PROD-2741..2780 - Exocortex Decision Policy Matrix",
        "future_phases": [
            "PROD-2781..2820 - Prompt and Input Data Quality Gate",
            "PROD-2821..2860 - Exocortex Value Delta Engine Contract"
        ]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "runtime_snapshot_evaluator_only",
        "blocked_actions": BLOCKED,
        "recommended_next_phase": evaluator["recommended_next_phase"],
        "future_phases": evaluator["future_phases"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Runtime Snapshot Evaluator",
        "type": "object",
        "required": ["version", "phase", "evaluations"]
    }

    doc = """# PROD-2701..2740 - Exocortex Runtime Snapshot Evaluator

Evaluates simulated runtime snapshots for CASULO Exocortex.

The evaluator scores integrity, claim boundary, risk pressure, lifecycle action readiness and priority.

Boundary: evaluator over simulated fixtures only. No memory mutation, no GPT memory API execution, no production and no client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(EVALUATOR, evaluator)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "pack_exists": PACK.exists(),
        "pack_output_exists": PACK_OUT.exists(),
        "pack_output_pass": pack_out.get("status") == "PASS",
        "snapshot_count": len(snapshots),
        "evaluation_count": len(evaluations),
        "has_snapshot_ready": "SNAPSHOT_READY" in verdicts,
        "has_discard_allowed": "DISCARD_ALLOWED_AFTER_REVIEW" in verdicts,
        "has_protected_state": "PROTECTED_STATE" in verdicts,
        "has_hold_review": "HOLD_REVIEW_REQUIRED" in verdicts or "REVIEW_REQUIRED" in verdicts,
        "all_integrity_high": all(e["integrity_score"] >= 80 for e in evaluations),
        "all_boundary_perfect": all(e["boundary_score"] == 100 for e in evaluations),
        "all_priority_positive": all(e["priority_score"] > 0 for e in evaluations),
        "future_input_quality_gate_registered": "PROD-2781..2820 - Prompt and Input Data Quality Gate" in evaluator["future_phases"],
        "future_value_delta_registered": "PROD-2821..2860 - Exocortex Value Delta Engine Contract" in evaluator["future_phases"],
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "unreviewed_mutation_blocked": "unreviewed_memory_mutation" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED,
        "client_claim_blocked": "client_facing_claim" in BLOCKED,
        "production_blocked": "production_activation" in BLOCKED
    }

    if checks["snapshot_count"] < 6:
        errors.append("snapshot_count below 6")
    if checks["evaluation_count"] != checks["snapshot_count"]:
        errors.append("evaluation_count mismatch")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXOCORTEX_RUNTIME_SNAPSHOT_EVALUATOR_READY" if status == "PASS" else "EXOCORTEX_RUNTIME_SNAPSHOT_EVALUATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluator": "product/memory/exocortex_runtime_snapshot_evaluator_v0_1.json",
        "snapshot_count": len(snapshots),
        "evaluation_count": len(evaluations),
        "verdicts": sorted(verdicts),
        "recommended_next_phase": evaluator["recommended_next_phase"],
        "future_phases": evaluator["future_phases"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2701..2740 Exocortex Runtime Snapshot Evaluator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Snapshots: `{len(snapshots)}`",
        f"- Evaluations: `{len(evaluations)}`",
        f"- Next: `{evaluator['recommended_next_phase']}`",
        "",
        "## Future propagation",
        "- PROD-2781..2820 - Prompt and Input Data Quality Gate",
        "- PROD-2821..2860 - Exocortex Value Delta Engine Contract",
        "",
        "## Evaluations"
    ]
    for e in evaluations:
        report.append(f"- `{e['snapshot_id']}` `{e['title']}` verdict `{e['verdict']}` priority `{e['priority_score']}`")
    report += ["", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("snapshots:", len(snapshots))
    print("evaluations:", len(evaluations))
    print("verdicts:", sorted(verdicts))
    print("next:", evaluator["recommended_next_phase"])
    print("future:", evaluator["future_phases"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
