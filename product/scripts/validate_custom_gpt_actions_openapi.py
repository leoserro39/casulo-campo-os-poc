#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "product" / "api" / "openapi" / "graph_context_actions.openapi.json"
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
    "public_api_publication"
]

def main():
    errors = []

    if not OPENAPI.exists():
        errors.append("OpenAPI file missing")
        spec = {}
    else:
        spec = json.loads(OPENAPI.read_text(encoding="utf-8"))

    paths = spec.get("paths", {})
    servers = spec.get("servers", [])

    checks = {
        "openapi_version_present": bool(spec.get("openapi")),
        "info_present": bool(spec.get("info")),
        "placeholder_server_present": any(
            "REPLACE_WITH_CONTROLLED_GRAPH_CONTEXT_API_HOST" in server.get("url", "")
            for server in servers
        ),
        "health_endpoint_present": "/api/health" in paths,
        "context_endpoint_present": "/api/graph/context" in paths,
        "context_get_operation_present": "get" in paths.get("/api/graph/context", {}),
        "operation_id_present": bool(paths.get("/api/graph/context", {}).get("get", {}).get("operationId")),
        "no_live_production_url": not any(
            "prod" in server.get("url", "").lower() or "production" in server.get("url", "").lower()
            for server in servers
        ),
        "safety_language_present": "does not generate final answers" in json.dumps(spec).lower()
    }

    for name, ok in checks.items():
        if not ok:
            errors.append(f"Check failed: {name}")

    status = "PASS" if not errors else "FAIL"

    result = {
        "status": status,
        "phase": "PROD-1421..1460",
        "openapi_file": str(OPENAPI.relative_to(ROOT)),
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    (OUT / "prod1421_1460_custom_gpt_actions_openapi_review.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    md = [
        "# PROD-1421..1460 Custom GPT Actions OpenAPI Review",
        "",
        f"- Status: `{status}`",
        f"- OpenAPI file: `{result['openapi_file']}`",
        "",
        "## Checks"
    ]
    for k, v in checks.items():
        md.append(f"- {k}: `{v}`")

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
        "- Contract only.",
        "- No publication.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No production connection.",
        "",
        "## Blocked Actions"
    ]

    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    (OUT / "prod1421_1460_custom_gpt_actions_openapi_review.md").write_text(
        "\n".join(md) + "\n",
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()
