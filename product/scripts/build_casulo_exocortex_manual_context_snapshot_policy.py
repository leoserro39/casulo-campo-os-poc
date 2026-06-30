#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2581..2620"
REQ_TAG = "product-memory-governor-readiness-gate-v0.1"

DOC = ROOT / "docs/product/566_CASULO_EXOCORTEX_MANUAL_CONTEXT_SNAPSHOT_POLICY_CONTRACT.md"
CONTRACT = ROOT / "product/contracts/casulo_exocortex_manual_context_snapshot_policy.contract.json"
SCHEMA = ROOT / "product/schemas/casulo_exocortex_manual_context_snapshot_policy.schema.json"
POLICY = ROOT / "product/memory/casulo_exocortex_manual_context_snapshot_policy_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2581_2620_casulo_exocortex_manual_context_snapshot_policy.json"
OUT_MD = ROOT / "outputs/prod2581_2620_casulo_exocortex_manual_context_snapshot_policy.md"

EXOCORTEX_SIGNALS = [
    "context_pressure",
    "stale_context_risk",
    "state_grounding_score",
    "evidence_coverage",
    "gate_compliance",
    "decision_recall_accuracy",
    "snapshot_recovery_score",
    "claim_leakage_risk",
    "token_waste_ratio"
]

CONTROL_LAYERS = [
    "state_checksum",
    "evidence_pointer_required",
    "claim_boundary_scanner",
    "stale_context_detector",
    "contradiction_gate",
    "response_mode_governor"
]

LIFECYCLE_ACTIONS = [
    "PROMOTE_TO_MEMORY",
    "COMPRESS_TO_SNAPSHOT",
    "ARCHIVE_TO_REPO",
    "DISCARD_EPHEMERAL",
    "HOLD_HUMAN_REVIEW",
    "PROTECT_DO_NOT_DELETE"
]

RESPONSE_MODES = [
    "STATE_ANSWER",
    "REVIEW_PACKET",
    "IMPLEMENTATION_PACKET",
    "RUNBOOK",
    "EVIDENCE_CAPTURE",
    "READINESS_GATE",
    "SNAPSHOT",
    "BLOCKED_ACTION_NOTICE"
]

BLOCKED = [
    "automatic_memory_delete",
    "unreviewed_memory_mutation",
    "validated_performance_claim",
    "client_facing_claim",
    "production_activation",
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

    definition = (
        "CASULO Exocortex is the operational exocortex of the chat/model. "
        "It preserves living state outside the active chat context, reduces context pressure, "
        "anchors answers in gates and evidence, and returns only the necessary state for allowed action."
    )

    policy = {
        "version": "casulo_exocortex_manual_context_snapshot_policy.v0.1",
        "phase": PHASE,
        "definition": definition,
        "metaphor_boundary": {
            "preferred_terms": ["exocortex", "operational symbiont", "state exoskeleton"],
            "avoid_terms": ["predatory parasite", "uncontrolled obedience"],
            "rule": "Maximize capability only for actions allowed by state, evidence and gates."
        },
        "exocortex_signals": EXOCORTEX_SIGNALS,
        "control_layers": CONTROL_LAYERS,
        "lifecycle_actions": LIFECYCLE_ACTIONS,
        "response_modes": RESPONSE_MODES,
        "snapshot_policy": {
            "chat_memory_should_keep": [
                "canonical_decisions",
                "current_phase",
                "commit_tag_decision_triplets",
                "active_gates",
                "next_allowed_action",
                "stable_user_preferences"
            ],
            "operational_cube_should_keep": [
                "living_state_graph",
                "phase_relations",
                "gate_history",
                "state_transitions",
                "evidence_pointers",
                "contradiction_records"
            ],
            "repo_should_keep": [
                "heavy_logs",
                "outputs",
                "reports",
                "contracts",
                "schemas",
                "audit_evidence"
            ],
            "discard_candidates": [
                "failed_commands_already_fixed",
                "duplicate_outputs",
                "obsolete_terminal_noise",
                "resolved_intermediate_errors"
            ],
            "manual_review_required_for": [
                "canonical_decision_deletion",
                "gate_policy_change",
                "conflicting_state",
                "client_or_production_claim",
                "memory_mutation"
            ]
        },
        "recommended_next_phase": "PROD-2621..2660 - Exocortex Snapshot Contract Validator"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "manual_context_snapshot_policy_contract",
        "exocortex_definition": definition,
        "anti_hallucination_role": True,
        "token_optimization_role": True,
        "control_layers": CONTROL_LAYERS,
        "signals": EXOCORTEX_SIGNALS,
        "lifecycle_actions": LIFECYCLE_ACTIONS,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": policy["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Manual Context Snapshot Policy",
        "type": "object",
        "required": ["version", "definition", "exocortex_signals", "control_layers", "lifecycle_actions", "snapshot_policy"]
    }

    doc = """# PROD-2581..2620 - CASULO Exocortex Manual Context Snapshot Policy Contract

Defines CASULO Exocortex as the operational exocortex of the chat/model.

It is not a blind memory cleaner. It is a governed context lifecycle layer.

It reduces hallucination risk by preserving state, evidence, gates and response modes outside the active chat context.

Boundary: manual policy contract only. No automatic memory deletion, no GPT memory API execution, no real performance claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(POLICY, policy)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "signal_count": len(EXOCORTEX_SIGNALS),
        "control_layer_count": len(CONTROL_LAYERS),
        "lifecycle_action_count": len(LIFECYCLE_ACTIONS),
        "response_mode_count": len(RESPONSE_MODES),
        "has_context_pressure": "context_pressure" in EXOCORTEX_SIGNALS,
        "has_stale_context": "stale_context_risk" in EXOCORTEX_SIGNALS,
        "has_state_grounding": "state_grounding_score" in EXOCORTEX_SIGNALS,
        "has_evidence_coverage": "evidence_coverage" in EXOCORTEX_SIGNALS,
        "has_gate_compliance": "gate_compliance" in EXOCORTEX_SIGNALS,
        "has_claim_leakage": "claim_leakage_risk" in EXOCORTEX_SIGNALS,
        "has_state_checksum": "state_checksum" in CONTROL_LAYERS,
        "has_evidence_pointer": "evidence_pointer_required" in CONTROL_LAYERS,
        "has_claim_scanner": "claim_boundary_scanner" in CONTROL_LAYERS,
        "has_contradiction_gate": "contradiction_gate" in CONTROL_LAYERS,
        "has_response_mode_governor": "response_mode_governor" in CONTROL_LAYERS,
        "has_protect": "PROTECT_DO_NOT_DELETE" in LIFECYCLE_ACTIONS,
        "automatic_delete_blocked": "automatic_memory_delete" in BLOCKED,
        "gpt_memory_api_blocked": "gpt_memory_api_execution" in BLOCKED,
        "performance_claim_blocked": "validated_performance_claim" in BLOCKED
    }

    if checks["signal_count"] < 9:
        errors.append("signal_count below 9")
    if checks["control_layer_count"] < 6:
        errors.append("control_layer_count below 6")
    if checks["lifecycle_action_count"] < 6:
        errors.append("lifecycle_action_count below 6")
    if checks["response_mode_count"] < 8:
        errors.append("response_mode_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CASULO_EXOCORTEX_MANUAL_CONTEXT_SNAPSHOT_POLICY_READY" if status == "PASS" else "CASULO_EXOCORTEX_MANUAL_CONTEXT_SNAPSHOT_POLICY_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "product/memory/casulo_exocortex_manual_context_snapshot_policy_v0_1.json",
        "signals": EXOCORTEX_SIGNALS,
        "control_layers": CONTROL_LAYERS,
        "lifecycle_actions": LIFECYCLE_ACTIONS,
        "response_modes": RESPONSE_MODES,
        "recommended_next_phase": policy["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2581..2620 CASULO Exocortex Manual Context Snapshot Policy",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Signals: `{len(EXOCORTEX_SIGNALS)}`",
        f"- Control layers: `{len(CONTROL_LAYERS)}`",
        f"- Lifecycle actions: `{len(LIFECYCLE_ACTIONS)}`",
        f"- Response modes: `{len(RESPONSE_MODES)}`",
        f"- Next: `{policy['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Manual policy only.",
        "- No automatic memory deletion.",
        "- No GPT memory API execution.",
        "- No validated performance claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("signals:", len(EXOCORTEX_SIGNALS))
    print("control_layers:", len(CONTROL_LAYERS))
    print("lifecycle_actions:", len(LIFECYCLE_ACTIONS))
    print("response_modes:", len(RESPONSE_MODES))
    print("next:", policy["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
