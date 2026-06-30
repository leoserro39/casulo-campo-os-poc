#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2661..2700"
REQ_TAG = "product-exocortex-snapshot-contract-validator-v0.1"

POLICY = ROOT / "product/memory/casulo_exocortex_manual_context_snapshot_policy_v0_1.json"
VALIDATOR_OUT = ROOT / "outputs/prod2621_2660_exocortex_snapshot_contract_validator.json"

DOC = ROOT / "docs/product/568_EXOCORTEX_SNAPSHOT_RUNTIME_FIXTURE_PACK.md"
CONTRACT = ROOT / "product/contracts/exocortex_snapshot_runtime_fixture_pack.contract.json"
SCHEMA = ROOT / "product/schemas/exocortex_snapshot_runtime_fixture_pack.schema.json"
PACK = ROOT / "product/memory/snapshots/exocortex_snapshot_runtime_fixture_pack_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2661_2700_exocortex_snapshot_runtime_fixture_pack.json"
OUT_MD = ROOT / "outputs/prod2661_2700_exocortex_snapshot_runtime_fixture_pack.md"

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "validated_performance_claim",
    "real_world_token_savings_claim",
    "client_facing_claim",
    "production_activation",
    "gpt_memory_api_execution"
]

SCENARIOS = [
    {
        "id": "EXO-RUNTIME-001",
        "title": "recent_pass_checkpoint",
        "gate": "READINESS_GATE",
        "response_mode": "SNAPSHOT",
        "lifecycle_action": "COMPRESS_TO_SNAPSHOT",
        "risk": "low",
        "summary": "Recent phase closed with PASS, commit, tag and next phase preserved."
    },
    {
        "id": "EXO-RUNTIME-002",
        "title": "resolved_terminal_error",
        "gate": "STATE_REVIEW_REQUIRED",
        "response_mode": "STATE_ANSWER",
        "lifecycle_action": "DISCARD_EPHEMERAL",
        "risk": "medium",
        "summary": "Broken command was fixed and should not contaminate next responses."
    },
    {
        "id": "EXO-RUNTIME-003",
        "title": "client_claim_blocked",
        "gate": "CLIENT_CLAIM_REVIEW_REQUIRED",
        "response_mode": "BLOCKED_ACTION_NOTICE",
        "lifecycle_action": "PROTECT_DO_NOT_DELETE",
        "risk": "critical",
        "summary": "Synthetic/demo evidence must not become client-facing validated claim."
    },
    {
        "id": "EXO-RUNTIME-004",
        "title": "stale_context_detected",
        "gate": "HOLD_HUMAN_REVIEW",
        "response_mode": "REVIEW_PACKET",
        "lifecycle_action": "ARCHIVE_TO_REPO",
        "risk": "high",
        "summary": "Old context conflicts with current state and needs review."
    },
    {
        "id": "EXO-RUNTIME-005",
        "title": "contradiction_hold",
        "gate": "CONTRADICTION_HOLD",
        "response_mode": "REVIEW_PACKET",
        "lifecycle_action": "HOLD_HUMAN_REVIEW",
        "risk": "high",
        "summary": "Conflicting PASS/FAIL or gate state must stop progression."
    },
    {
        "id": "EXO-RUNTIME-006",
        "title": "protected_canonical_decision",
        "gate": "PROTECT_CANONICAL_DECISION",
        "response_mode": "SNAPSHOT",
        "lifecycle_action": "PROTECT_DO_NOT_DELETE",
        "risk": "critical",
        "summary": "Canonical decision, gate or product rule must not be deleted automatically."
    }
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

def make_snapshot(scenario, policy):
    return {
        "snapshot_id": scenario["id"],
        "phase": PHASE,
        "title": scenario["title"],
        "summary": scenario["summary"],
        "risk": scenario["risk"],
        "state_checksum": {
            "commit": "c2521ad",
            "tag": REQ_TAG,
            "decision": "EXOCORTEX_SNAPSHOT_CONTRACT_VALIDATOR_READY",
            "gate": scenario["gate"],
            "source_artifacts": [
                "product/memory/exocortex_snapshot_contract_validator_v0_1.json",
                "outputs/prod2621_2660_exocortex_snapshot_contract_validator.json"
            ]
        },
        "evidence_pointers": [
            "product/memory/exocortex_snapshot_contract_validator_v0_1.json",
            "outputs/prod2621_2660_exocortex_snapshot_contract_validator.json"
        ],
        "claim_boundary": {
            "client_facing_claim_allowed": False,
            "production_activation_allowed": False,
            "validated_performance_claim_allowed": False,
            "real_world_token_savings_claim_allowed": False
        },
        "gate": scenario["gate"],
        "response_mode": scenario["response_mode"],
        "lifecycle_action": scenario["lifecycle_action"],
        "exocortex_signals": {
            signal: "tracked"
            for signal in policy.get("exocortex_signals", [])
        },
        "blocked_actions": BLOCKED
    }

def validate(snapshot, policy):
    errors = []
    for field in ["snapshot_id","phase","state_checksum","evidence_pointers","claim_boundary","gate","response_mode","lifecycle_action","exocortex_signals","blocked_actions"]:
        if field not in snapshot:
            errors.append("missing field: " + field)

    checksum = snapshot.get("state_checksum", {})
    for field in ["commit","tag","decision","gate","source_artifacts"]:
        if field not in checksum:
            errors.append("missing state_checksum." + field)

    if not snapshot.get("evidence_pointers"):
        errors.append("evidence_pointers empty")

    boundary = snapshot.get("claim_boundary", {})
    for key in ["client_facing_claim_allowed","production_activation_allowed","validated_performance_claim_allowed"]:
        if boundary.get(key) is not False:
            errors.append(key + " must be false")

    allowed_actions = set(policy.get("lifecycle_actions", []))
    if snapshot.get("lifecycle_action") not in allowed_actions:
        errors.append("invalid lifecycle_action")

    expected_signals = set(policy.get("exocortex_signals", []))
    got_signals = set(snapshot.get("exocortex_signals", {}).keys())
    missing = sorted(expected_signals - got_signals)
    if missing:
        errors.append("missing signals: " + ",".join(missing))

    for action in BLOCKED:
        if action not in snapshot.get("blocked_actions", []):
            errors.append("missing blocked action: " + action)

    return {"status": "PASS" if not errors else "FAIL", "errors": errors}

def main():
    errors = []
    policy = read_json(POLICY) if POLICY.exists() else {}
    validator = read_json(VALIDATOR_OUT) if VALIDATOR_OUT.exists() else {}

    snapshots = [make_snapshot(s, policy) for s in SCENARIOS]
    validations = [
        {
            "snapshot_id": s["snapshot_id"],
            "title": s["title"],
            "result": validate(s, policy)
        }
        for s in snapshots
    ]

    pack = {
        "version": "exocortex_snapshot_runtime_fixture_pack.v0.1",
        "phase": PHASE,
        "fixture_type": "runtime_simulated_snapshots",
        "important_boundary": "Simulated runtime fixtures only. No real memory mutation.",
        "snapshots": snapshots,
        "validations": validations,
        "recommended_next_phase": "PROD-2701..2740 - Exocortex Runtime Snapshot Evaluator"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "runtime_fixture_pack_only",
        "snapshot_count": len(snapshots),
        "blocked_actions": BLOCKED,
        "recommended_next_phase": pack["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Snapshot Runtime Fixture Pack",
        "type": "object",
        "required": ["version", "phase", "fixture_type", "snapshots", "validations"]
    }

    doc = """# PROD-2661..2700 - Exocortex Snapshot Runtime Fixture Pack

Creates simulated runtime snapshots for the CASULO Exocortex.

The pack covers recent PASS checkpoints, resolved terminal errors, blocked client claims, stale context, contradiction holds and protected canonical decisions.

Boundary: simulated runtime fixtures only. No real memory mutation, no GPT memory API execution and no production/client claims.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(PACK, pack)

    titles = {s["title"] for s in snapshots}
    validation_statuses = [v["result"]["status"] for v in validations]

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "policy_exists": POLICY.exists(),
        "validator_output_exists": VALIDATOR_OUT.exists(),
        "validator_pass": validator.get("status") == "PASS",
        "snapshot_count": len(snapshots),
        "validation_count": len(validations),
        "all_snapshots_pass": all(s == "PASS" for s in validation_statuses),
        "has_recent_pass": "recent_pass_checkpoint" in titles,
        "has_resolved_error": "resolved_terminal_error" in titles,
        "has_client_claim_blocked": "client_claim_blocked" in titles,
        "has_stale_context": "stale_context_detected" in titles,
        "has_contradiction_hold": "contradiction_hold" in titles,
        "has_protected_decision": "protected_canonical_decision" in titles,
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "unreviewed_mutation_blocked": "unreviewed_memory_mutation" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED,
        "client_claim_blocked": "client_facing_claim" in BLOCKED,
        "production_blocked": "production_activation" in BLOCKED
    }

    if checks["snapshot_count"] < 6:
        errors.append("snapshot_count below 6")
    if checks["validation_count"] != checks["snapshot_count"]:
        errors.append("validation_count mismatch")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXOCORTEX_SNAPSHOT_RUNTIME_FIXTURE_PACK_READY" if status == "PASS" else "EXOCORTEX_SNAPSHOT_RUNTIME_FIXTURE_PACK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pack": "product/memory/snapshots/exocortex_snapshot_runtime_fixture_pack_v0_1.json",
        "snapshot_count": len(snapshots),
        "validation_count": len(validations),
        "recommended_next_phase": pack["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2661..2700 Exocortex Snapshot Runtime Fixture Pack",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Snapshots: `{len(snapshots)}`",
        f"- Validations: `{len(validations)}`",
        f"- Next: `{pack['recommended_next_phase']}`",
        "",
        "## Runtime Fixtures"
    ]
    for s in snapshots:
        report.append(f"- `{s['snapshot_id']}` `{s['title']}` gate `{s['gate']}` action `{s['lifecycle_action']}`")
    report += ["", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("snapshots:", len(snapshots))
    print("validations:", len(validations))
    print("next:", pack["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
