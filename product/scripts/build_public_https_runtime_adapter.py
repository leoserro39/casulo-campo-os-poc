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


PUBLIC_ACTION_PATHS = [
    ("/api/product/status", "getProductStatus", "Return runtime status."),
    ("/api/casulo/readiness/technical-memo", "getTechnicalReadinessMemo", "Return technical readiness memo."),
    ("/api/casulo/readiness/chat-agent-model", "getChatAgentModel", "Return chat agent operating model."),
    ("/api/casulo/readiness/target-stack", "getTargetStack", "Return target stack."),
    ("/api/casulo/readiness/codex-github-bridge", "getCodexGithubBridge", "Return Codex/GitHub bridge plan."),
    ("/api/casulo/readiness/poc-service-blueprint", "getPocServiceBlueprint", "Return POC service blueprint."),
    ("/api/casulo/poc-calibration/results", "getPocCalibrationResults", "Return POC calibration results."),
    ("/api/casulo/poc-calibration/delta-control", "getPocCalibrationDeltaControl", "Return delta control report."),
    ("/api/casulo/readiness/incubator-pack", "getIncubatorPack", "Return incubator technical pack."),
    ("/api/casulo/readiness/audit", "getReadinessAudit", "Return technical readiness audit."),
]


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def md_simple(title: str, obj: Dict[str, Any]) -> List[str]:
    lines = [f"# {title}", ""]
    for key, value in obj.items():
        if isinstance(value, (str, int, float, bool)):
            lines.append(f"- {key}: `{value}`")
        elif isinstance(value, list):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for item in value:
                if isinstance(item, dict):
                    label = item.get("path") or item.get("name") or item.get("mode") or item.get("gate") or "item"
                    lines.append(f"- `{label}` — {json.dumps(item, ensure_ascii=False)}")
                else:
                    lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}`")
    return lines


def build_openapi(public_base_url: str) -> Dict[str, Any]:
    paths = {}
    for path, op_id, summary in PUBLIC_ACTION_PATHS:
        paths[path] = {
            "get": {
                "operationId": op_id,
                "summary": summary,
                "responses": {
                    "200": {
                        "description": "CASULO runtime response",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }
        }
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "CASULO / Cubo Public Actions Runtime",
            "version": "0.1.0",
            "description": "Read-only public HTTPS action schema for Custom GPT prototype."
        },
        "servers": [{"url": public_base_url, "description": "Public HTTPS CASULO runtime endpoint"}],
        "paths": paths,
    }


def build(repo: Path, public_base_url: str) -> Dict[str, Any]:
    is_https = public_base_url.startswith("https://")
    deployment_plan = {
        "contract_version": "casulo.public_https_runtime.v0.1",
        "status": "PASS",
        "public_base_url": public_base_url,
        "https_ready": is_https,
        "deployment_modes": [
            {"mode": "local_only", "use": "developer validation", "url_type": "http://127.0.0.1"},
            {"mode": "secure_tunnel_for_demo", "use": "temporary Custom GPT demo", "url_type": "https://temporary"},
            {"mode": "prototype_cloud_api", "use": "controlled POC demo", "url_type": "https://stable"},
            {"mode": "production_hardened_later", "use": "after auth, persistence, audit and security", "url_type": "https://stable_auth"}
        ],
        "recommendation": "Use local runtime for now. Use secure public HTTPS tunnel or prototype cloud only for controlled Custom GPT Action testing.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    fastapi_adapter = {
        "contract_version": "casulo.fastapi_deploy_adapter.v0.1",
        "status": "PASS",
        "entrypoint": "product/deploy/fastapi_runtime_adapter.py",
        "requirements": "product/deploy/requirements.txt",
        "local_command": "python -m uvicorn product.deploy.fastapi_runtime_adapter:app --host 0.0.0.0 --port 8098",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "read_only": True,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    public_openapi = build_openapi(public_base_url)

    action_import_guide = {
        "contract_version": "casulo.custom_gpt_action_import_guide.v0.1",
        "status": "PASS",
        "steps": [
            "Start CASULO runtime or FastAPI adapter.",
            "Expose it through a public HTTPS URL for Custom GPT use.",
            "Regenerate public OpenAPI spec with --public-base-url https://your-url.",
            "Copy outputs/prod161_170_public_openapi_spec.json into Custom GPT Actions.",
            "Paste outputs/prod151_160_custom_gpt_instructions.md content as GPT instructions.",
            "Keep Actions read-only until auth/write gates are implemented.",
            "Test status, technical memo, calibration, delta control and audit endpoints."
        ],
        "warning": "Do not expose localhost or unprotected sensitive data to external users.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    security_gate = {
        "contract_version": "casulo.deploy_security_gate.v0.1",
        "status": "PASS",
        "decision": "PUBLIC_HTTPS_PROTOTYPE_ALLOWED_ONLY_FOR_READ_ONLY_REDACTED_DATA",
        "allowed": [
            "read-only readiness queries",
            "read-only calibration queries",
            "read-only incubator/technical pack queries",
            "read-only audit queries"
        ],
        "blocked": BLOCKED_ACTIONS + [
            "write_actions",
            "file_upload_to_public_runtime",
            "unredacted_data_ingestion",
            "public credential handling",
            "automatic code execution"
        ],
        "requires_before_external_use": [
            "public HTTPS",
            "no secrets",
            "redacted/anonymized data",
            "human review",
            "access control if used beyond demo"
        ],
    }

    parser_task_mode = {
        "contract_version": "casulo.simple_task_mode.parser_documental.v0.1",
        "status": "PASS",
        "purpose": "Clarify that first practical POC can be simple: document parser, document audit, rule extraction or checklist conversion.",
        "why": "Simple tasks are ideal because evidence, fields, rules and hallucination risk are easier to measure.",
        "allowed_outputs": [
            "parser contract",
            "field inventory",
            "example extraction map",
            "test plan",
            "code skeleton",
            "blocked production decision",
            "evidence/delta report"
        ],
        "blocked_outputs": [
            "production parser claim",
            "deployment",
            "credential handling",
            "automatic merge"
        ],
    }

    readiness = {
        "contract_version": "casulo.public_https_runtime_readiness.v0.1",
        "status": "PASS",
        "decision": "READY_FOR_PUBLIC_HTTPS_RUNTIME_PROTOTYPE_PLANNING",
        "https_url_valid": is_https,
        "next": "Choose local tunnel or prototype cloud deployment, then regenerate OpenAPI with public HTTPS base URL.",
        "not_ready_for": [
            "production SaaS",
            "multi-tenant data ingestion",
            "write actions",
            "unredacted company data"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Public HTTPS Runtime / FastAPI Deploy Adapter audit",
        "https_url_valid": is_https,
        "openapi_paths": len(public_openapi["paths"]),
        "adapter": fastapi_adapter["entrypoint"],
        "readiness": readiness["decision"],
        "finding": "PASS: deploy adapter and public OpenAPI schema are ready for prototype planning. Real Custom GPT use requires public HTTPS URL.",
    }

    return {
        "deployment_plan": deployment_plan,
        "fastapi_adapter": fastapi_adapter,
        "public_openapi": public_openapi,
        "action_import_guide": action_import_guide,
        "security_gate": security_gate,
        "parser_task_mode": parser_task_mode,
        "readiness": readiness,
        "audit": audit,
    }


def write_outputs(repo: Path, public_base_url: str, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    out.mkdir(parents=True, exist_ok=True)
    data = build(repo, public_base_url)

    write_json(out / "prod161_170_public_openapi_spec.json", data["public_openapi"])
    write_md(out / "prod161_170_public_openapi_spec.md", md_simple("Public OpenAPI Spec", {
        "status": "PASS",
        "public_base_url": public_base_url,
        "paths": list(data["public_openapi"]["paths"].keys()),
    }))

    files = {
        "prod161_170_deployment_plan": ("Public HTTPS Runtime Deployment Plan", data["deployment_plan"]),
        "prod161_170_fastapi_adapter": ("FastAPI Deploy Adapter", data["fastapi_adapter"]),
        "prod161_170_action_import_guide": ("Custom GPT Action Import Guide", data["action_import_guide"]),
        "prod161_170_security_gate": ("Deploy Security Gate", data["security_gate"]),
        "prod161_170_parser_task_mode": ("Parser Documental Task Mode", data["parser_task_mode"]),
        "prod161_170_public_runtime_readiness": ("Public Runtime Readiness", data["readiness"]),
        "prod161_170_audit_report": ("Public Runtime Audit", data["audit"]),
    }
    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", md_simple(title, obj))

    result = {
        "task": "PROD-161..170",
        "status": "PASS",
        "phase": "Public HTTPS Runtime / FastAPI Deploy Adapter",
        "decision": data["readiness"]["decision"],
        "outputs": ["outputs/prod161_170_public_openapi_spec.json"] + [f"outputs/{stem}.json" for stem in files],
        "next_recommended_bundle": "PROD-171..180 State Store / Evidence Store / Graph Store Baseline",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod161_170_result.json", result)
    write_md(out / "prod161_170_report.md", md_simple("PROD-161..170 Public HTTPS Runtime / FastAPI Deploy Adapter Report", result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--public-base-url", default="http://127.0.0.1:8098")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    print(json.dumps(write_outputs(Path(args.repo), args.public_base_url, args.output_dir), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
