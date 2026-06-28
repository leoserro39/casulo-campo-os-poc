#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
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


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


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
                    label = item.get("state_id") or item.get("evidence_id") or item.get("graph_id") or item.get("name") or item.get("stage") or "item"
                    lines.append(f"- `{label}` — {json.dumps(item, ensure_ascii=False)}")
                else:
                    lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}`")
    return lines


def build_records() -> Dict[str, List[Dict[str, Any]]]:
    ts = now_iso()
    state_records = [
        {
            "state_id": "STATE-ENTERPRISE-CHAT-001",
            "state_type": "chat_surface",
            "status": "READY_FOR_MANUAL_AND_ACTIONS_PROTOTYPE",
            "source_ref": "prod151_160_connector_readiness",
            "evidence_refs": ["EV-CUSTOM-GPT-ACTIONS-001", "EV-PUBLIC-RUNTIME-001"],
            "gate_status": "READ_ONLY_ACTIONS_ALLOWED",
            "version": "v0.1",
            "created_at": ts,
        },
        {
            "state_id": "STATE-PUBLIC-RUNTIME-001",
            "state_type": "runtime_endpoint",
            "status": "PLANNING_READY_NOT_HTTPS_YET",
            "source_ref": "prod161_170_public_runtime_readiness",
            "evidence_refs": ["EV-FASTAPI-ADAPTER-001", "EV-OPENAPI-PUBLIC-001"],
            "gate_status": "HTTPS_REQUIRED_FOR_CUSTOM_GPT",
            "version": "v0.1",
            "created_at": ts,
        },
        {
            "state_id": "STATE-PARSER-DOCUMENTAL-001",
            "state_type": "simple_task_mode",
            "status": "READY_FOR_CONTROLLED_POC",
            "source_ref": "prod161_170_parser_task_mode",
            "evidence_refs": ["EV-PARSER-MODE-001"],
            "gate_status": "PRODUCTION_BLOCKED",
            "version": "v0.1",
            "created_at": ts,
        },
    ]

    evidence_records = [
        {
            "evidence_id": "EV-CUSTOM-GPT-ACTIONS-001",
            "source_type": "runtime_output",
            "source_ref": "outputs/prod151_160_audit_report.json",
            "support_status": "SUPPORTED",
            "redaction_status": "NO_RAW_COMPANY_DATA",
            "traceability": "custom GPT actions connector passed with 10 actions",
            "created_at": ts,
        },
        {
            "evidence_id": "EV-PUBLIC-RUNTIME-001",
            "source_type": "runtime_output",
            "source_ref": "outputs/prod161_170_audit_report.json",
            "support_status": "SUPPORTED_WITH_WARNING",
            "redaction_status": "NO_RAW_COMPANY_DATA",
            "traceability": "public runtime planning passed; HTTPS still required",
            "created_at": ts,
        },
        {
            "evidence_id": "EV-PARSER-MODE-001",
            "source_type": "runtime_output",
            "source_ref": "outputs/prod161_170_parser_task_mode.json",
            "support_status": "SUPPORTED",
            "redaction_status": "NO_RAW_COMPANY_DATA",
            "traceability": "parser documental mode allowed for controlled POC",
            "created_at": ts,
        },
        {
            "evidence_id": "EV-FASTAPI-ADAPTER-001",
            "source_type": "code_artifact",
            "source_ref": "product/deploy/fastapi_runtime_adapter.py",
            "support_status": "SUPPORTED",
            "redaction_status": "NO_RAW_COMPANY_DATA",
            "traceability": "read-only FastAPI adapter exists",
            "created_at": ts,
        },
        {
            "evidence_id": "EV-OPENAPI-PUBLIC-001",
            "source_type": "openapi_schema",
            "source_ref": "outputs/prod161_170_public_openapi_spec.json",
            "support_status": "SUPPORTED_WITH_WARNING",
            "redaction_status": "NO_RAW_COMPANY_DATA",
            "traceability": "OpenAPI schema generated; server URL must become HTTPS for real Custom GPT",
            "created_at": ts,
        },
    ]

    graph_records = [
        {
            "graph_id": "GRAPH-ENTERPRISE-ACTIONS-001",
            "domain_candidates": ["chat_surface", "runtime_api", "actions_schema", "security_gate", "readiness"],
            "entity_candidates": ["Enterprise workspace", "Custom GPT", "CASULO runtime", "OpenAPI schema", "public HTTPS endpoint"],
            "relation_candidates": [
                {"from": "Custom GPT", "to": "CASULO runtime", "relation": "calls_actions"},
                {"from": "Enterprise workspace", "to": "Custom GPT", "relation": "hosts_and_controls"},
                {"from": "OpenAPI schema", "to": "CASULO runtime", "relation": "describes"},
                {"from": "security_gate", "to": "actions", "relation": "restricts_to_read_only"},
            ],
            "review_status": "HUMAN_REVIEW_REQUIRED_BEFORE_EXTERNAL_USE",
            "created_at": ts,
        },
        {
            "graph_id": "GRAPH-PARSER-POC-001",
            "domain_candidates": ["document_processing", "rules", "evidence", "parser_contract", "tests"],
            "entity_candidates": ["document", "field", "rule", "example", "parser skeleton", "test case"],
            "relation_candidates": [
                {"from": "document", "to": "field", "relation": "contains_or_implies"},
                {"from": "rule", "to": "field", "relation": "constrains"},
                {"from": "test case", "to": "parser skeleton", "relation": "validates"},
            ],
            "review_status": "READY_FOR_CONTROLLED_POC",
            "created_at": ts,
        },
    ]

    audit_records = [
        {
            "audit_id": "AUDIT-STORE-BASELINE-001",
            "status": "PASS",
            "finding": "State/evidence/graph baseline store created as repo-native JSONL, not production database.",
            "created_at": ts,
        }
    ]
    return {
        "state_records": state_records,
        "evidence_records": evidence_records,
        "graph_records": graph_records,
        "audit_records": audit_records,
    }


def build_outputs(repo: Path) -> Dict[str, Any]:
    records = build_records()

    store_status = {
        "contract_version": "casulo.store_baseline_status.v0.1",
        "status": "PASS",
        "mode": "repo_native_jsonl_store",
        "not_production_database": True,
        "records": {
            "state_records": len(records["state_records"]),
            "evidence_records": len(records["evidence_records"]),
            "graph_records": len(records["graph_records"]),
            "audit_records": len(records["audit_records"]),
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    state_store_index = {
        "contract_version": "casulo.state_store_baseline.v0.1",
        "status": "PASS",
        "path": "product/store/state_records.jsonl",
        "purpose": "Reuse computed operational states across chat sessions, POCs, recommendations and development tasks.",
        "records": records["state_records"],
        "migration_target": "PostgreSQL state store",
    }

    evidence_store_index = {
        "contract_version": "casulo.evidence_store_baseline.v0.1",
        "status": "PASS",
        "path": "product/store/evidence_records.jsonl",
        "purpose": "Track sources, redaction, support status and traceability without storing raw sensitive data.",
        "records": records["evidence_records"],
        "migration_target": "object store + metadata database",
    }

    graph_store_index = {
        "contract_version": "casulo.graph_store_baseline.v0.1",
        "status": "PASS",
        "path": "product/store/graph_records.jsonl",
        "purpose": "Track candidate domains, entities and relations before graph database.",
        "records": records["graph_records"],
        "migration_target": "Neo4j or PostgreSQL graph model",
    }

    write_policy = {
        "contract_version": "casulo.store_write_policy.v0.1",
        "status": "PASS",
        "allowed_writes": [
            "append local JSONL state metadata",
            "append evidence metadata",
            "append graph candidate metadata",
            "append audit records"
        ],
        "blocked_writes": BLOCKED_ACTIONS + [
            "raw_secret_storage",
            "unredacted_sensitive_storage",
            "production_db_mutation",
            "external_write_actions"
        ],
        "rule": "Enterprise chat/actions may read store summaries. Writes remain local/internal until auth and audit are hardened.",
    }

    enterprise_integration = {
        "contract_version": "casulo.enterprise_workspace_integration.v0.1",
        "status": "PASS",
        "procedure": [
            "Use the Enterprise workspace as the chat surface and permission boundary.",
            "Create or edit a GPT in the workspace with permission from the workspace admin.",
            "Deploy or expose CASULO runtime through a public HTTPS endpoint.",
            "Allowlist the CASULO action domain in workspace GPT action settings if restricted.",
            "Import the OpenAPI schema generated by CASULO.",
            "Paste CASULO GPT instructions into the GPT configuration.",
            "Keep Actions read-only during prototype.",
            "Test with redacted/anonymous parser/document cases first.",
            "Move to auth/write/persistence only after successful controlled POC."
        ],
        "enterprise_account_role": "Enterprise account does not replace CASULO runtime; it hosts the Custom GPT/agent that calls CASULO through Actions.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    migration_path = {
        "contract_version": "casulo.store_migration_path.v0.1",
        "status": "PASS",
        "stages": [
            {"stage": "repo_jsonl_baseline", "status": "CURRENT"},
            {"stage": "sqlite_dev", "status": "NEXT_OPTIONAL"},
            {"stage": "postgres_state_store", "status": "PLANNED"},
            {"stage": "object_evidence_store", "status": "PLANNED"},
            {"stage": "graph_db_or_postgres_graph", "status": "PLANNED"},
            {"stage": "append_only_audit_ledger", "status": "PLANNED"},
        ],
        "decision": "KEEP_REPO_NATIVE_UNTIL_FIRST_ENTERPRISE_CHAT_POC",
    }

    readiness = {
        "contract_version": "casulo.store_baseline_readiness.v0.1",
        "status": "PASS",
        "decision": "READY_FOR_ENTERPRISE_CHAT_POC_WITH_REPO_NATIVE_STORE",
        "ready_for": [
            "Enterprise Custom GPT planning",
            "read-only Actions prototype",
            "parser documental POC",
            "state/evidence/graph reuse across sessions",
            "manual audit and calibration"
        ],
        "not_ready_for": [
            "multi-tenant SaaS",
            "production database",
            "unredacted evidence ingestion",
            "external write actions",
            "production automation"
        ],
        "next": "Build Enterprise Custom GPT Import Kit and run first parser/document POC.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "State/Evidence/Graph Store Baseline audit",
        "state_records": len(records["state_records"]),
        "evidence_records": len(records["evidence_records"]),
        "graph_records": len(records["graph_records"]),
        "readiness": readiness["decision"],
        "finding": "PASS: repo-native store is enough for Enterprise chat POC and parser/document tests; production DB remains blocked until later.",
    }

    return {
        "records": records,
        "store_status": store_status,
        "state_store_index": state_store_index,
        "evidence_store_index": evidence_store_index,
        "graph_store_index": graph_store_index,
        "write_policy": write_policy,
        "enterprise_integration": enterprise_integration,
        "migration_path": migration_path,
        "readiness": readiness,
        "audit": audit,
    }


def write_outputs(repo: Path, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    store = repo / "product" / "store"
    out.mkdir(parents=True, exist_ok=True)
    store.mkdir(parents=True, exist_ok=True)
    data = build_outputs(repo)

    write_jsonl(store / "state_records.jsonl", data["records"]["state_records"])
    write_jsonl(store / "evidence_records.jsonl", data["records"]["evidence_records"])
    write_jsonl(store / "graph_records.jsonl", data["records"]["graph_records"])
    write_jsonl(store / "audit_records.jsonl", data["records"]["audit_records"])

    files = {
        "prod171_180_store_status": ("Store Baseline Status", data["store_status"]),
        "prod171_180_state_store_index": ("State Store Baseline Index", data["state_store_index"]),
        "prod171_180_evidence_store_index": ("Evidence Store Baseline Index", data["evidence_store_index"]),
        "prod171_180_graph_store_index": ("Graph Store Baseline Index", data["graph_store_index"]),
        "prod171_180_store_write_policy": ("Store Write Policy", data["write_policy"]),
        "prod171_180_enterprise_workspace_integration": ("Enterprise Workspace Integration", data["enterprise_integration"]),
        "prod171_180_store_migration_path": ("Store Migration Path", data["migration_path"]),
        "prod171_180_store_readiness": ("Store Baseline Readiness", data["readiness"]),
        "prod171_180_audit_report": ("State/Evidence/Graph Store Audit", data["audit"]),
    }

    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", md_simple(title, obj))

    result = {
        "task": "PROD-171..180",
        "status": "PASS",
        "phase": "State Store / Evidence Store / Graph Store Baseline",
        "decision": data["readiness"]["decision"],
        "outputs": [f"outputs/{stem}.json" for stem in files],
        "store_files": [
            "product/store/state_records.jsonl",
            "product/store/evidence_records.jsonl",
            "product/store/graph_records.jsonl",
            "product/store/audit_records.jsonl",
        ],
        "next_recommended_bundle": "PROD-181..190 Enterprise Custom GPT Import Kit / Parser POC Runbook",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod171_180_result.json", result)
    write_md(out / "prod171_180_report.md", md_simple("PROD-171..180 State/Evidence/Graph Store Baseline Report", result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    print(json.dumps(write_outputs(Path(args.repo), args.output_dir), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
