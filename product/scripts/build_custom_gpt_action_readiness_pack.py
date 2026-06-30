#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation",
    "gpt_call",
    "codex_execution",
    "public_api_publication",
    "custom_gpt_connection"
]

ARTIFACTS = [
    "docs/product/538_CUSTOM_GPT_ACTION_READINESS_PACK.md",
    "product/contracts/custom_gpt_action_readiness_pack.contract.json",
    "product/schemas/custom_gpt_action_readiness_pack.schema.json",
    "product/gpt/custom_gpt_instructions_draft.md",
    "product/gpt/custom_gpt_action_setup_checklist.md",
    "product/gpt/custom_gpt_action_safety_boundary.md",
    "product/api/openapi/graph_context_actions.openapi.json",
    "product/api/graph_context_api.py",
    "product/scripts/run_graph_backed_retrieval_adapter.py"
]

def main():
    checks = {}
    errors = []

    for artifact in ARTIFACTS:
        exists = (ROOT / artifact).exists()
        checks[f"exists:{artifact}"] = exists
        if not exists:
            errors.append(f"Missing artifact: {artifact}")

    openapi = ROOT / "product/api/openapi/graph_context_actions.openapi.json"
    if openapi.exists():
        spec_text = openapi.read_text(encoding="utf-8")
        checks["openapi_has_placeholder_server"] = "REPLACE_WITH_CONTROLLED_GRAPH_CONTEXT_API_HOST" in spec_text
        checks["openapi_has_graph_context_endpoint"] = "/api/graph/context" in spec_text
        checks["openapi_has_safety_language"] = "does not generate final answers" in spec_text.lower()
    else:
        checks["openapi_has_placeholder_server"] = False
        checks["openapi_has_graph_context_endpoint"] = False
        checks["openapi_has_safety_language"] = False

    instructions = ROOT / "product/gpt/custom_gpt_instructions_draft.md"
    if instructions.exists():
        inst = instructions.read_text(encoding="utf-8").lower()
        checks["instructions_block_codex"] = "execute codex" in inst or "run codex" in inst
        checks["instructions_require_context_not_truth"] = "context, not final authorization" in inst
        checks["instructions_block_client_claims"] = "client-facing claims" in inst
    else:
        checks["instructions_block_codex"] = False
        checks["instructions_require_context_not_truth"] = False
        checks["instructions_block_client_claims"] = False

    for key, ok in checks.items():
        if not ok:
            errors.append(f"Check failed: {key}")

    status = "PASS" if not errors else "FAIL"
    decision = (
        "READY_FOR_HUMAN_REVIEW_BEFORE_CUSTOM_GPT_CONNECTION"
        if status == "PASS"
        else "NOT_READY_FOR_CUSTOM_GPT_CONNECTION"
    )

    result = {
        "status": status,
        "phase": "PROD-1461..1500",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": ARTIFACTS,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    json_path = OUT / "prod1461_1500_custom_gpt_action_readiness_pack.json"
    md_path = OUT / "prod1461_1500_custom_gpt_action_readiness_pack.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1461..1500 Custom GPT Action Readiness Pack",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        "",
        "## Artifacts"
    ]
    for artifact in ARTIFACTS:
        md.append(f"- {artifact}")

    md += [
        "",
        "## Checks"
    ]
    for key, ok in checks.items():
        md.append(f"- {key}: `{ok}`")

    md += [
        "",
        "## Errors"
    ]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Boundary",
        "- Readiness pack only.",
        "- No Custom GPT connection.",
        "- No API publication.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No production connection.",
        "",
        "## Blocked Actions"
    ]
    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
