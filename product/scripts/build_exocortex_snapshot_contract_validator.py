#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2621..2660"
REQ_TAG = "product-casulo-exocortex-manual-context-snapshot-policy-contract-v0.1"

POLICY = ROOT / "product/memory/casulo_exocortex_manual_context_snapshot_policy_v0_1.json"

DOC = ROOT / "docs/product/567_EXOCORTEX_SNAPSHOT_CONTRACT_VALIDATOR.md"
CONTRACT = ROOT / "product/contracts/exocortex_snapshot_contract_validator.contract.json"
SCHEMA = ROOT / "product/schemas/exocortex_snapshot_contract.schema.json"
VALIDATOR = ROOT / "product/memory/exocortex_snapshot_contract_validator_v0_1.json"
VALID_FIXTURE = ROOT / "product/memory/snapshots/exocortex_snapshot_valid_fixture_v0_1.json"
INVALID_FIXTURE = ROOT / "product/memory/snapshots/exocortex_snapshot_invalid_missing_checksum_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2621_2660_exocortex_snapshot_contract_validator.json"
OUT_MD = ROOT / "outputs/prod2621_2660_exocortex_snapshot_contract_validator.md"

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "validated_performance_claim",
    "real_world_token_savings_claim",
    "client_facing_claim",
    "production_activation",
    "gpt_memory_api_execution"
]

REQUIRED_FIELDS = [
    "snapshot_id",
    "phase",
    "state_checksum",
    "evidence_pointers",
    "claim_boundary",
    "gate",
    "response_mode",
    "lifecycle_action",
    "exocortex_signals",
    "blocked_actions"
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

def validate_snapshot(snapshot, policy):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append("missing field: " + field)

    state_checksum = snapshot.get("state_checksum", {})
    for key in ["commit", "tag", "decision", "gate", "source_artifacts"]:
        if key not in state_checksum:
            errors.append("missing state_checksum." + key)

    if not snapshot.get("evidence_pointers"):
        errors.append("evidence_pointers empty")

    claim_boundary = snapshot.get("claim_boundary", {})
    if claim_boundary.get("client_facing_claim_allowed") is not False:
        errors.append("client_facing_claim_allowed must be false")
    if claim_boundary.get("production_activation_allowed") is not False:
        errors.append("production_activation_allowed must be false")
    if claim_boundary.get("validated_performance_claim_allowed") is not False:
        errors.append("validated_performance_claim_allowed must be false")

    allowed_modes = set(policy.get("response_modes", []))
    if snapshot.get("response_mode") not in allowed_modes:
        errors.append("invalid response_mode")

    allowed_actions = set(policy.get("lifecycle_actions", []))
    if snapshot.get("lifecycle_action") not in allowed_actions:
        errors.append("invalid lifecycle_action")

    expected_signals = set(policy.get("exocortex_signals", []))
    got_signals = set(snapshot.get("exocortex_signals", {}).keys())
    missing_signals = sorted(expected_signals - got_signals)
    if missing_signals:
        errors.append("missing exocortex_signals: " + ",".join(missing_signals))

    blocked = set(snapshot.get("blocked_actions", []))
    for action in BLOCKED:
        if action not in blocked:
            errors.append("blocked action not present: " + action)

    status = "PASS" if not errors else "FAIL"
    return {"status": status, "errors": errors}

def main():
    errors = []
    policy = read_json(POLICY) if POLICY.exists() else {}

    valid_snapshot = {
        "snapshot_id": "EXO-SNAPSHOT-FIXTURE-001",
        "phase": PHASE,
        "state_checksum": {
            "commit": "1cbaa00",
            "tag": REQ_TAG,
            "decision": "CASULO_EXOCORTEX_MANUAL_CONTEXT_SNAPSHOT_POLICY_READY",
            "gate": "MANUAL_CONTEXT_SNAPSHOT_POLICY_CONTRACT",
            "source_artifacts": [
                "product/memory/casulo_exocortex_manual_context_snapshot_policy_v0_1.json",
                "outputs/prod2581_2620_casulo_exocortex_manual_context_snapshot_policy.json"
            ]
        },
        "evidence_pointers": [
            "product/memory/casulo_exocortex_manual_context_snapshot_policy_v0_1.json",
            "outputs/prod2581_2620_casulo_exocortex_manual_context_snapshot_policy.json"
        ],
        "claim_boundary": {
            "client_facing_claim_allowed": False,
            "production_activation_allowed": False,
            "validated_performance_claim_allowed": False,
            "real_world_token_savings_claim_allowed": False
        },
        "gate": "HOLD_HUMAN_REVIEW",
        "response_mode": "SNAPSHOT",
        "lifecycle_action": "COMPRESS_TO_SNAPSHOT",
        "exocortex_signals": {signal: "tracked" for signal in policy.get("exocortex_signals", [])},
        "blocked_actions": BLOCKED
    }

    invalid_snapshot = dict(valid_snapshot)
    invalid_snapshot.pop("state_checksum", None)
    invalid_snapshot["snapshot_id"] = "EXO-SNAPSHOT-INVALID-001"

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Snapshot Contract",
        "type": "object",
        "required": REQUIRED_FIELDS
    }

    validator = {
        "version": "exocortex_snapshot_contract_validator.v0.1",
        "phase": PHASE,
        "required_fields": REQUIRED_FIELDS,
        "required_state_checksum_fields": ["commit", "tag", "decision", "gate", "source_artifacts"],
        "required_claim_boundary_false": [
            "client_facing_claim_allowed",
            "production_activation_allowed",
            "validated_performance_claim_allowed"
        ],
        "required_blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-2661..2700 - Exocortex Snapshot Runtime Fixture Pack"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "snapshot_contract_validator",
        "validator": validator,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": validator["recommended_next_phase"]
    }

    doc = """# PROD-2621..2660 - Exocortex Snapshot Contract Validator

Defines and validates the minimum contract for CASULO Exocortex snapshots.

A valid snapshot must contain state checksum, evidence pointers, claim boundary, gate, response mode, lifecycle action, Exocortex signals and blocked actions.

Boundary: validator only. No automatic memory deletion, no real memory mutation and no GPT memory API execution.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(VALIDATOR, validator)
    write_json(VALID_FIXTURE, valid_snapshot)
    write_json(INVALID_FIXTURE, invalid_snapshot)

    valid_result = validate_snapshot(valid_snapshot, policy)
    invalid_result = validate_snapshot(invalid_snapshot, policy)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "policy_exists": POLICY.exists(),
        "policy_has_exocortex_signals": len(policy.get("exocortex_signals", [])) >= 9,
        "policy_has_lifecycle_actions": len(policy.get("lifecycle_actions", [])) >= 6,
        "policy_has_response_modes": len(policy.get("response_modes", [])) >= 8,
        "required_field_count": len(REQUIRED_FIELDS),
        "valid_fixture_passes": valid_result["status"] == "PASS",
        "invalid_fixture_fails": invalid_result["status"] == "FAIL",
        "invalid_detects_missing_checksum": any("state_checksum" in e for e in invalid_result["errors"]),
        "schema_exists": SCHEMA.exists(),
        "validator_exists": VALIDATOR.exists(),
        "valid_fixture_exists": VALID_FIXTURE.exists(),
        "invalid_fixture_exists": INVALID_FIXTURE.exists(),
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "unreviewed_mutation_blocked": "unreviewed_memory_mutation" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED,
        "performance_claim_blocked": "validated_performance_claim" in BLOCKED
    }

    if checks["required_field_count"] < 9:
        errors.append("required_field_count below 9")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXOCORTEX_SNAPSHOT_CONTRACT_VALIDATOR_READY" if status == "PASS" else "EXOCORTEX_SNAPSHOT_CONTRACT_VALIDATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validator": "product/memory/exocortex_snapshot_contract_validator_v0_1.json",
        "valid_fixture": "product/memory/snapshots/exocortex_snapshot_valid_fixture_v0_1.json",
        "invalid_fixture": "product/memory/snapshots/exocortex_snapshot_invalid_missing_checksum_v0_1.json",
        "valid_result": valid_result,
        "invalid_result": invalid_result,
        "recommended_next_phase": validator["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2621..2660 Exocortex Snapshot Contract Validator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Required fields: `{len(REQUIRED_FIELDS)}`",
        f"- Valid fixture: `{valid_result['status']}`",
        f"- Invalid fixture: `{invalid_result['status']}`",
        f"- Next: `{validator['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Validator only.",
        "- No automatic memory deletion.",
        "- No unreviewed memory mutation.",
        "- No GPT memory API execution.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("valid_fixture:", valid_result["status"])
    print("invalid_fixture:", invalid_result["status"])
    print("next:", validator["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
