#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"

ARTIFACTS = [
    "docs/product/539_CONTROLLED_CUSTOM_GPT_CONNECTION_RUNBOOK.md",
    "product/contracts/controlled_custom_gpt_connection_runbook.contract.json",
    "product/schemas/controlled_custom_gpt_connection_runbook.schema.json",
    "product/gpt/controlled_custom_gpt_connection_runbook.md",
    "product/gpt/controlled_custom_gpt_connection_test_prompts.md",
    "product/gpt/controlled_custom_gpt_connection_human_gate.md",
    "product/gpt/custom_gpt_instructions_draft.md",
    "product/gpt/custom_gpt_action_setup_checklist.md",
    "product/gpt/custom_gpt_action_safety_boundary.md",
    "product/api/openapi/graph_context_actions.openapi.json"
]

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
    "custom_gpt_connection_without_human_approval"
]

def read(path):
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""

def main():
    checks = {}
    errors = []

    for artifact in ARTIFACTS:
        exists = (ROOT / artifact).exists()
        checks[f"exists:{artifact}"] = exists
        if not exists:
            errors.append(f"Missing artifact: {artifact}")

    runbook = read("product/gpt/controlled_custom_gpt_connection_runbook.md").lower()
    gate = read("product/gpt/controlled_custom_gpt_connection_human_gate.md").lower()
    prompts = read("product/gpt/controlled_custom_gpt_connection_test_prompts.md").lower()
    contract = read("product/contracts/controlled_custom_gpt_connection_runbook.contract.json").lower()
    openapi = read("product/api/openapi/graph_context_actions.openapi.json")

    checks["runbook_has_stop_conditions"] = "stop conditions" in runbook
    checks["runbook_has_no_production_boundary"] = "no production endpoint is used" in runbook
    checks["runbook_has_no_credentials_boundary"] = "no credentials are stored" in runbook
    checks["runbook_requires_blocked_actions"] = "blocked actions" in runbook
    checks["runbook_does_not_authorize_connection"] = "does not authorize connection" in runbook
    checks["human_gate_has_connect_do_not_connect"] = "connect" in gate and "do not connect" in gate
    checks["human_gate_is_non_delegable"] = "cannot be made by gpt" in gate
    checks["test_prompts_include_codex_refusal"] = "refuses execution" in prompts and "codex" in prompts
    checks["test_prompts_include_client_boundary"] = "client" in prompts and "says no" in prompts
    checks["contract_blocks_connection"] = '"custom_gpt_connection_allowed": false' in contract
    checks["contract_blocks_gpt_call"] = '"gpt_call_allowed": false' in contract
    checks["openapi_still_placeholder"] = "REPLACE_WITH_CONTROLLED_GRAPH_CONTEXT_API_HOST" in openapi

    for key, ok in checks.items():
        if not ok:
            errors.append(f"Check failed: {key}")

    status = "PASS" if not errors else "FAIL"
    decision = (
        "READY_FOR_CONTROLLED_CONNECTION_REVIEW"
        if status == "PASS"
        else "NOT_READY_FOR_CONTROLLED_CONNECTION_REVIEW"
    )

    result = {
        "status": status,
        "phase": "PROD-1501..1540",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": ARTIFACTS,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1501_1540_controlled_custom_gpt_connection_runbook.json"
    md_path = OUT / "prod1501_1540_controlled_custom_gpt_connection_runbook.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1501..1540 Controlled Custom GPT Connection Runbook",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        "",
        "## Artifacts"
    ]
    for artifact in ARTIFACTS:
        md.append(f"- {artifact}")

    md += ["", "## Checks"]
    for key, ok in checks.items():
        md.append(f"- {key}: `{ok}`")

    md += ["", "## Errors"]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Boundary",
        "- Runbook only.",
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
