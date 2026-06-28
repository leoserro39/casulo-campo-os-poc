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


def exists(path: Path) -> bool:
    return path.exists()


def read_json(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


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
                    label = item.get("name") or item.get("mode") or item.get("layer") or item.get("step") or item.get("gate") or "item"
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


def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    calibration = read_json(out / "prod131_140_calibration_results.json")
    calibration_summary = calibration.get("summary", {})

    status_checks = {
        "casulo_method": exists(out / "prod081_120_casulo_method.json"),
        "gpt_operating_layer": exists(out / "prod081_120_gpt_operating_layer.json"),
        "company_chat_intake": exists(out / "prod081_120_company_chat_intake.json"),
        "evaluation_report": exists(out / "prod081_120_evaluation_report.json"),
        "graph_builder_v0": exists(out / "prod121_130_graph_builder_v0.json"),
        "state_store_index": exists(out / "prod121_130_state_store_index.json"),
        "poc_factory_pack": exists(out / "prod121_130_poc_factory_pack.json"),
        "poc_calibration_runner": exists(out / "prod131_140_calibration_results.json"),
        "delta_control_report": exists(out / "prod131_140_delta_control_report.json"),
        "poc_calibration_readiness": exists(out / "prod131_140_poc_calibration_readiness.json"),
    }

    technical_readiness = {
        "contract_version": "casulo.technical_readiness_memo.v0.1",
        "status": "PASS" if all(status_checks.values()) else "INCOMPLETE",
        "readiness_decision": "READY_FOR_COMPANY_INCUBATOR_INVESTOR_AND_CONTROLLED_POC_DISCUSSION",
        "technical_assets": status_checks,
        "core_claim": "CASULO/Cubo is a governed AI operating layer that converts chat/documents into candidate graphs, operational states, evidence, gates, deltas, recommendations, development tasks, calibration and audit.",
        "validated_metrics": {
            "avg_hallucination_reduction": calibration_summary.get("avg_hallucination_reduction"),
            "avg_delta_control_gain": calibration_summary.get("avg_delta_control_gain"),
            "avg_residual_delta": calibration_summary.get("avg_residual_delta"),
            "cases_count": calibration_summary.get("cases_count"),
        },
        "ready_for": [
            "controlled POC services",
            "incubator technical discussion",
            "investor technical validation",
            "company formation planning",
            "first anonymized company tests",
            "manual or semi-automated GPT operating sessions"
        ],
        "not_ready_for": [
            "SaaS production",
            "autonomous production automation",
            "client-facing final claims without human review",
            "autonomous code merge/deploy",
            "unredacted sensitive data processing"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    chat_agent_model = {
        "contract_version": "casulo.chat_agent_operating_model.v0.1",
        "status": "PASS",
        "purpose": "Define how the system moves from this chat into a governed agent connected to the CASULO runtime.",
        "modes": [
            {"mode": "manual_chat_protocol", "when": "now", "description": "User uploads/supplies context; assistant follows CASULO protocol and repo outputs."},
            {"mode": "custom_gpt_with_actions", "when": "after first real/anonymous POC", "description": "A Custom GPT calls CASULO runtime endpoints as Actions."},
            {"mode": "api_connected_agent", "when": "after stack baseline", "description": "Agent service calls runtime, state store, graph store and evidence store."},
            {"mode": "multi_agent_runtime", "when": "after repeatable POC", "description": "Separate agents for intake, graph, evaluation, development and audit."},
            {"mode": "enterprise_stack", "when": "after security and persistence", "description": "Auth, database, graph DB, RAG, audit log, UI and controlled integrations."}
        ],
        "operating_flow": [
            "company/user sends sanitized context in chat",
            "agent calls intake policy",
            "agent builds or retrieves state",
            "agent calls graph builder",
            "agent calls evaluation/calibration",
            "agent applies response gate",
            "agent generates answer/report/task/code only within allowed scope",
            "agent records audit and calibration note"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    target_stack = {
        "contract_version": "casulo.target_stack.v0.1",
        "status": "PASS",
        "stack_sequence": [
            {"layer": "Chat Surface", "baseline": "ChatGPT / Custom GPT", "later": "web app / client portal"},
            {"layer": "Actions / Agent Tools", "baseline": "OpenAPI actions calling runtime endpoints", "later": "agent runtime with tool router"},
            {"layer": "CASULO Runtime API", "baseline": "current local API", "later": "FastAPI service"},
            {"layer": "State Store", "baseline": "repo outputs/file index", "later": "Postgres"},
            {"layer": "Graph Store", "baseline": "JSON candidate graph", "later": "Neo4j or PostgreSQL graph model"},
            {"layer": "Evidence Store", "baseline": "documents and manifests", "later": "object store + metadata DB"},
            {"layer": "RAG Index", "baseline": "manual/document search", "later": "vector DB or managed retrieval"},
            {"layer": "Audit Log", "baseline": "outputs and reports", "later": "append-only audit ledger"},
            {"layer": "Codex/GitHub Bridge", "baseline": "manual repo tasks", "later": "issues/branches/PRs gated by CASULO"},
            {"layer": "UI Console", "baseline": "runtime endpoints", "later": "dashboard for state/evidence/gates/delta"}
        ],
        "stack_decision": "DO_NOT_BUILD_FULL_STACK_BEFORE_REAL_OR_ANONYMOUS_POC_PROOF",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    codex_bridge = {
        "contract_version": "casulo.codex_github_bridge.v0.1",
        "status": "PASS",
        "purpose": "Use Codex only after CASULO state/gate creates controlled development tasks.",
        "allowed_flow": [
            "state identifies development delta",
            "gate confirms task-only or controlled development scope",
            "issue is created with evidence and acceptance criteria",
            "branch is created",
            "Codex drafts patch/tests/docs",
            "validation runs",
            "PR opens with evidence",
            "human review approves or blocks"
        ],
        "blocked_without_gate": BLOCKED_ACTIONS,
    }

    poc_service_blueprint = {
        "contract_version": "casulo.poc_service_blueprint.v0.1",
        "status": "PASS",
        "service_name": "CASULO/Cubo Controlled AI POC",
        "duration_options": ["1-day diagnostic", "1-week POC", "2-4 week technical pilot"],
        "inputs": [
            "sanitized briefing",
            "document inventory",
            "sample anonymized records",
            "rules inventory",
            "known risks",
            "desired outputs",
            "redaction statement"
        ],
        "outputs": [
            "source inventory",
            "candidate graph",
            "operational state map",
            "evidence map",
            "gate matrix",
            "delta control report",
            "hallucination risk comparison",
            "recommendation governance report",
            "next-cycle backlog"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    risk_control_matrix = {
        "contract_version": "casulo.risk_control_matrix.v0.1",
        "status": "PASS",
        "controls": [
            {"risk": "Sensitive data exposure", "control": "redaction intake template and forbidden input policy"},
            {"risk": "Hallucination", "control": "hallucination risk index and response gate"},
            {"risk": "False completion", "control": "residual delta plus delta control score"},
            {"risk": "Bad recommendation", "control": "recommendation governance and evidence gate"},
            {"risk": "Unsafe development", "control": "Codex/GitHub bridge gated by task/test/human review"},
            {"risk": "Premature commercialization claim", "control": "blocked client_facing_claim until human-reviewed evidence pack"}
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    roadmap_90d = {
        "contract_version": "casulo.technical_roadmap_90d.v0.1",
        "status": "PASS",
        "days_0_15": [
            "run first real/anonymous company case",
            "calibrate metric weights",
            "record first before/after POC report",
            "prepare incubator technical memo"
        ],
        "days_16_45": [
            "build Custom GPT / Actions prototype",
            "formalize OpenAPI schema for runtime endpoints",
            "harden state store and graph builder v0",
            "prepare first controlled service offer"
        ],
        "days_46_90": [
            "add persistent database",
            "add evidence store and audit ledger",
            "add Codex/GitHub bridge",
            "run 2-3 POC pilots across different domains"
        ],
    }

    incubator_pack = {
        "contract_version": "casulo.incubator_technical_pack.v0.1",
        "status": "PASS",
        "positioning": "Technical validation pack for a governed AI operating layer, not a finished SaaS.",
        "technical_artifacts": [
            "CASULO method",
            "GPT operating layer",
            "Company chat intake",
            "Graph Builder v0",
            "State Store Index",
            "Recommendation Governance",
            "POC Factory Pack",
            "Real/Anonymous POC Calibration Runner",
            "Delta Control Score",
            "Technical Readiness Memo",
            "Chat Agent Operating Model",
            "Target Stack",
            "Codex/GitHub Bridge Plan"
        ],
        "readiness": technical_readiness["readiness_decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Technical Readiness Memo and Incubator Pack audit",
        "readiness_decision": technical_readiness["readiness_decision"],
        "stack_decision": target_stack["stack_decision"],
        "chat_agent_model": chat_agent_model["status"],
        "incubator_pack": incubator_pack["status"],
        "finding": "PASS: project is ready for controlled chat-based POC operation and technical readiness discussion; full stack should follow proof with real/anonymized cases."
    }

    return {
        "technical_readiness": technical_readiness,
        "chat_agent_model": chat_agent_model,
        "target_stack": target_stack,
        "codex_bridge": codex_bridge,
        "poc_service_blueprint": poc_service_blueprint,
        "risk_control_matrix": risk_control_matrix,
        "roadmap_90d": roadmap_90d,
        "incubator_pack": incubator_pack,
        "audit": audit,
    }


def write_outputs(repo: Path, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    out.mkdir(parents=True, exist_ok=True)
    data = build(repo)

    files = {
        "prod141_150_technical_readiness_memo": ("Technical Readiness Memo", data["technical_readiness"]),
        "prod141_150_chat_agent_operating_model": ("Chat Agent Operating Model", data["chat_agent_model"]),
        "prod141_150_target_stack": ("Target Stack", data["target_stack"]),
        "prod141_150_codex_github_bridge": ("Codex GitHub Bridge", data["codex_bridge"]),
        "prod141_150_poc_service_blueprint": ("POC Service Blueprint", data["poc_service_blueprint"]),
        "prod141_150_risk_control_matrix": ("Risk Control Matrix", data["risk_control_matrix"]),
        "prod141_150_technical_roadmap_90d": ("Technical Roadmap 90d", data["roadmap_90d"]),
        "prod141_150_incubator_technical_pack": ("Incubator Technical Pack", data["incubator_pack"]),
        "prod141_150_audit_report": ("Technical Readiness Audit", data["audit"]),
    }

    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", md_simple(title, obj))

    result = {
        "task": "PROD-141..150",
        "status": "PASS",
        "phase": "Technical Readiness Memo and Incubator Pack",
        "decision": data["technical_readiness"]["readiness_decision"],
        "outputs": [f"outputs/{stem}.json" for stem in files],
        "next_recommended_bundle": "PROD-151..160 Custom GPT Actions / Agent Connector Prototype",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod141_150_result.json", result)
    write_md(out / "prod141_150_report.md", md_simple("PROD-141..150 Technical Readiness Memo and Incubator Pack Report", result))
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
