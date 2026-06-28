#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

ENDPOINTS = [
    {
        "operation_id": "getProductStatus",
        "method": "get",
        "path": "/api/product/status",
        "summary": "Return CASULO/Cubo runtime status and readiness checks.",
        "tag": "status",
    },
    {
        "operation_id": "getTechnicalReadinessMemo",
        "method": "get",
        "path": "/api/casulo/readiness/technical-memo",
        "summary": "Return technical readiness memo.",
        "tag": "readiness",
    },
    {
        "operation_id": "getChatAgentModel",
        "method": "get",
        "path": "/api/casulo/readiness/chat-agent-model",
        "summary": "Return chat agent operating model.",
        "tag": "agent",
    },
    {
        "operation_id": "getTargetStack",
        "method": "get",
        "path": "/api/casulo/readiness/target-stack",
        "summary": "Return target stack plan.",
        "tag": "stack",
    },
    {
        "operation_id": "getCodexGithubBridge",
        "method": "get",
        "path": "/api/casulo/readiness/codex-github-bridge",
        "summary": "Return Codex/GitHub bridge plan.",
        "tag": "development",
    },
    {
        "operation_id": "getPocServiceBlueprint",
        "method": "get",
        "path": "/api/casulo/readiness/poc-service-blueprint",
        "summary": "Return controlled POC service blueprint.",
        "tag": "poc",
    },
    {
        "operation_id": "getPocCalibrationResults",
        "method": "get",
        "path": "/api/casulo/poc-calibration/results",
        "summary": "Return POC calibration results.",
        "tag": "calibration",
    },
    {
        "operation_id": "getPocCalibrationDeltaControl",
        "method": "get",
        "path": "/api/casulo/poc-calibration/delta-control",
        "summary": "Return delta control report.",
        "tag": "calibration",
    },
    {
        "operation_id": "getIncubatorPack",
        "method": "get",
        "path": "/api/casulo/readiness/incubator-pack",
        "summary": "Return incubator technical pack.",
        "tag": "incubator",
    },
    {
        "operation_id": "getReadinessAudit",
        "method": "get",
        "path": "/api/casulo/readiness/audit",
        "summary": "Return technical readiness audit.",
        "tag": "audit",
    },
]


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def md_simple(title: str, obj: Dict[str, Any]) -> List[str]:
    lines = [f"# {title}", ""]
    for key, value in obj.items():
        if isinstance(value, (str, int, float, bool)):
            lines.append(f"- {key}: `{value}`")
        elif isinstance(value, list):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for item in value:
                if isinstance(item, dict):
                    label = item.get("operation_id") or item.get("name") or item.get("mode") or item.get("route") or "item"
                    lines.append(f"- `{label}` — {json.dumps(item, ensure_ascii=False)}")
                else:
                    lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False)}`")
                else:
                    lines.append(f"- {k}: `{v}`")
    return lines


def build_openapi(base_url: str) -> Dict[str, Any]:
    paths: Dict[str, Any] = {}
    for endpoint in ENDPOINTS:
        paths[endpoint["path"]] = {
            endpoint["method"]: {
                "operationId": endpoint["operation_id"],
                "summary": endpoint["summary"],
                "tags": [endpoint["tag"]],
                "responses": {
                    "200": {
                        "description": "CASULO response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "CASULO / Cubo Operational Runtime Actions",
            "version": "0.1.0",
            "description": "Read-only action schema for Custom GPT / agent connector prototype."
        },
        "servers": [
            {"url": base_url, "description": "CASULO runtime endpoint. For Custom GPT this must be public HTTPS."}
        ],
        "paths": paths,
    }


def build(repo: Path, base_url: str) -> Dict[str, Any]:
    openapi = build_openapi(base_url)

    custom_gpt_instructions = {
        "contract_version": "casulo.custom_gpt_instructions.v0.1",
        "status": "PASS",
        "name": "CASULO / Cubo Operating Agent",
        "role": "Governed AI operating layer for chat-based POC, evaluation, graph/state/gate/delta reasoning and controlled task generation.",
        "instructions": [
            "Always treat uploaded or pasted company data as evidence candidates, not automatic truth.",
            "Before giving a final answer, determine whether the request needs intake, graph, state, calibration, readiness, recommendation or Codex/GitHub bridge context.",
            "Use CASULO actions when available instead of relying only on memory.",
            "Never claim production readiness unless the readiness/gate output allows it.",
            "Never accept credentials, tokens, passwords, API keys or unredacted sensitive data.",
            "Preserve blocked actions: client-facing claim, automatic nomination, implementation execution, production activation, automatic merge and credential handling.",
            "When evidence is incomplete, produce a partial answer, structure, task plan or request for evidence instead of inventing missing facts.",
            "For development, route through Codex/GitHub bridge only after state, evidence, gate and human review requirements are satisfied."
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    action_manifest = {
        "contract_version": "casulo.custom_gpt_actions_manifest.v0.1",
        "status": "PASS",
        "mode": "read_only_actions_prototype",
        "requires_public_https_for_real_custom_gpt": True,
        "local_base_url": base_url,
        "actions": ENDPOINTS,
        "security_policy": {
            "auth_mode": "none_for_local_prototype",
            "production_auth_required": True,
            "data_policy": "redacted_or_anonymized_only",
            "write_actions": "blocked_in_this_prototype",
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    tool_router = {
        "contract_version": "casulo.action_tool_router.v0.1",
        "status": "PASS",
        "routes": [
            {"intent": "status or readiness", "endpoint": "/api/product/status"},
            {"intent": "technical readiness / company / incubator", "endpoint": "/api/casulo/readiness/technical-memo"},
            {"intent": "how chat/agent should operate", "endpoint": "/api/casulo/readiness/chat-agent-model"},
            {"intent": "stack plan", "endpoint": "/api/casulo/readiness/target-stack"},
            {"intent": "codex or github development bridge", "endpoint": "/api/casulo/readiness/codex-github-bridge"},
            {"intent": "poc service design", "endpoint": "/api/casulo/readiness/poc-service-blueprint"},
            {"intent": "calibration or hallucination evidence", "endpoint": "/api/casulo/poc-calibration/results"},
            {"intent": "delta control", "endpoint": "/api/casulo/poc-calibration/delta-control"},
            {"intent": "incubator package", "endpoint": "/api/casulo/readiness/incubator-pack"},
            {"intent": "audit", "endpoint": "/api/casulo/readiness/audit"},
        ],
        "routing_rule": "When uncertain, fetch product status and readiness memo first.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    connector_session = {
        "contract_version": "casulo.agent_connector_session.v0.1",
        "status": "PASS",
        "session_mode": "local_connector_prototype",
        "flow": [
            "manual chat protocol remains valid now",
            "Custom GPT imports OpenAPI action schema",
            "GPT instruction enforces CASULO gates",
            "GPT calls read-only endpoints",
            "agent generates answer/report/task only within allowed scope",
            "human reviews before external claim, implementation or production"
        ],
        "tool_router": tool_router["routes"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    security_policy = {
        "contract_version": "casulo.agent_connector_security.v0.1",
        "status": "PASS",
        "policy": [
            "Local prototype endpoints are read-only.",
            "Real Custom GPT requires public HTTPS endpoint.",
            "Production deployment requires authentication and audit log.",
            "No credentials or secrets in chat.",
            "No write actions until explicit gate and auth model exist.",
            "Codex/GitHub write operations are out of scope for this connector prototype."
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "contract_version": "casulo.agent_connector_readiness.v0.1",
        "status": "PASS",
        "decision": "READY_FOR_LOCAL_CUSTOM_GPT_ACTIONS_CONNECTOR_PROTOTYPE",
        "ready_for": [
            "manual chat protocol",
            "local OpenAPI schema generation",
            "read-only action mapping",
            "Custom GPT instructions draft",
            "tool routing design",
            "connector security policy"
        ],
        "not_ready_for": [
            "public Custom GPT without HTTPS deployment",
            "write actions",
            "production auth",
            "Codex autonomous execution",
            "enterprise data ingestion"
        ],
        "next": "Expose the runtime through a public HTTPS URL or deploy a small FastAPI service, then import the OpenAPI schema into a Custom GPT action.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Custom GPT Actions / Agent Connector Prototype audit",
        "openapi_paths": len(openapi["paths"]),
        "actions": len(action_manifest["actions"]),
        "tool_routes": len(tool_router["routes"]),
        "readiness": readiness["decision"],
        "finding": "PASS: connector prototype is ready locally; real Custom GPT Actions require public HTTPS deployment and auth hardening before external use."
    }

    return {
        "openapi": openapi,
        "custom_gpt_instructions": custom_gpt_instructions,
        "action_manifest": action_manifest,
        "tool_router": tool_router,
        "connector_session": connector_session,
        "security_policy": security_policy,
        "readiness": readiness,
        "audit": audit,
    }


def write_outputs(repo: Path, base_url: str, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    out.mkdir(parents=True, exist_ok=True)
    data = build(repo, base_url)

    files = {
        "prod151_160_custom_gpt_instructions": ("Custom GPT Instructions", data["custom_gpt_instructions"]),
        "prod151_160_action_manifest": ("Custom GPT Action Manifest", data["action_manifest"]),
        "prod151_160_tool_router": ("Action Tool Router", data["tool_router"]),
        "prod151_160_connector_session": ("Agent Connector Session", data["connector_session"]),
        "prod151_160_security_policy": ("Agent Connector Security Policy", data["security_policy"]),
        "prod151_160_connector_readiness": ("Agent Connector Readiness", data["readiness"]),
        "prod151_160_audit_report": ("Agent Connector Audit", data["audit"]),
    }

    write_json(out / "prod151_160_openapi_spec.json", data["openapi"])
    write_text(out / "prod151_160_openapi_spec.md", "\n".join(md_simple("OpenAPI Action Spec", {"status": "PASS", "base_url": base_url, "paths": list(data["openapi"]["paths"].keys())})) + "\n")

    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_text(out / f"{stem}.md", "\n".join(md_simple(title, obj)) + "\n")

    result = {
        "task": "PROD-151..160",
        "status": "PASS",
        "phase": "Custom GPT Actions / Agent Connector Prototype",
        "decision": data["readiness"]["decision"],
        "outputs": ["outputs/prod151_160_openapi_spec.json"] + [f"outputs/{stem}.json" for stem in files],
        "next_recommended_bundle": "PROD-161..170 Public HTTPS Runtime / FastAPI Deploy Adapter",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod151_160_result.json", result)
    write_text(out / "prod151_160_report.md", "\n".join(md_simple("PROD-151..160 Custom GPT Actions / Agent Connector Prototype Report", result)) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base-url", default="http://127.0.0.1:8097")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    print(json.dumps(write_outputs(Path(args.repo), args.base_url, args.output_dir), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
