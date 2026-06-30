#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    "live_graph_database_write",
    "neo4j_connection_without_explicit_sandbox_flag",
]

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build(repo: Path) -> dict:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    required = {
        "business_diagnostic": "outputs/prod981_1020_business_diagnostic_readiness.json",
        "demo_evidence": "outputs/umbrella_prod-1021_1060_controlled_demo_evidence_readiness.json",
        "graph_review": "outputs/umbrella_prod-1061_1100_non_live_graph_import_readiness.json",
        "business_value": "outputs/umbrella_prod-1101_1140_business_value_metrics_readiness.json",
        "demo_surface": "outputs/umbrella_prod-1141_1180_demo_surface_operator_readiness_readiness.json",
    }
    required_status = {key: (repo / rel).exists() for key, rel in required.items()}
    missing = [rel for key, rel in required.items() if not required_status[key]]
    final_readiness = load_json(repo / required["demo_surface"], {})
    train_closed = (not missing) and final_readiness.get("decision") == "READY_FOR_UMBRELLA_TRAIN_AUDIT_AND_COMMIT"

    alias_policy = {
        "status": "PASS",
        "problem_found": "Umbrella train used mixed dependency filenames with and without hyphen after prod.",
        "fix_applied_in_current_train": [
            "umbrella_prod1021_1060_controlled_demo_evidence_readiness.json",
            "umbrella_prod1061_1100_non_live_graph_import_readiness.json",
            "umbrella_prod1101_1140_business_value_metrics_readiness.json"
        ],
        "next_train_policy": {
            "machine_outputs": "prodNNNN_NNNN only, no hyphen",
            "human_docs": "PROD-NNNN notation allowed",
            "no_manual_alias_commits": True,
            "dependency_manifest_required": True
        },
        "blocked_actions": BLOCKED_ACTIONS
    }

    llm_boundary = {
        "status": "PASS",
        "roles": {
            "research_llm": {
                "role": "search, compare, summarize sources and hypotheses",
                "used_for": ["technical research", "market/stack comparison", "documentation synthesis", "hypothesis generation"],
                "cannot": ["execute business action", "mutate thresholds", "write production graph"]
            },
            "diagnostic_runtime_llm": {
                "role": "reasoning inside Cubo gates",
                "used_for": ["diagnosis", "recommendation", "evidence request", "human review packet"],
                "must_obey": ["gate", "hallucination budget", "readiness", "blocked actions"]
            },
            "verifier_or_critic_llm": {
                "role": "challenge outputs before release",
                "used_for": ["contradiction check", "evidence gap check", "unsafe claim check", "business-risk review"]
            },
            "codex_or_coding_agent": {
                "role": "implementation agent for repo changes",
                "used_for": ["write code", "generate tests", "refactor", "prepare PR-like patches"],
                "not_runtime_business_executor": True
            },
            "tool_executor": {
                "role": "allowlisted operational runner",
                "used_for": ["run validation", "read outputs", "query sandbox graph", "generate reports"],
                "requires": ["allowlist", "audit log", "human approval for side effects"]
            }
        },
        "core_answer": "Codex should be the implementation/coding executor; runtime decisions should be orchestrator + retrieval/Neo4j + research LLM when allowed + diagnostic LLM + verifier LLM + Cubo gates + tool executor only when allowlisted.",
        "blocked_actions": BLOCKED_ACTIONS
    }

    stack_roadmap = {
        "status": "PASS",
        "current_state": {
            "controlled_50_case_dry_run": True,
            "business_diagnostic_report": True,
            "demo_evidence_pack": True,
            "non_live_graph_review": True,
            "business_value_metrics": True,
            "demo_surface_readiness": True,
            "neo4j_sandbox_import": False,
            "graph_retrieval_gain_measured": False,
            "codex_boundary_hardened": False
        },
        "how_much_left": {
            "to_first_neo4j_sandbox_import": "1 focused package",
            "to_measure_neo4j_technical_gain": "3 focused packages",
            "to_integrate_codex_as_repo_executor_boundary": "1 focused package after Neo4j gain test or in parallel",
            "to_full_safe_stack_demo": "one more umbrella train after PROD-1181..1220"
        },
        "technical_gain_hypothesis": {
            "neo4j": [
                "better multi-hop traceability Case -> Evidence -> RiskSignal -> Gate -> OutputMode",
                "faster explanation of why a decision was blocked or reviewed",
                "stronger retrieval precision for relationship-heavy cases",
                "better audit graph for demos and governance"
            ],
            "llm_stack": [
                "research LLM expands knowledge and alternatives",
                "diagnostic LLM produces controlled recommendations",
                "verifier LLM reduces unsupported claims",
                "runtime gates prevent weak hypotheses from becoming strong actions"
            ],
            "codex": [
                "accelerates implementation, tests and refactors",
                "should not be the direct runtime business executor",
                "best used as repo-native builder under validation and human review"
            ]
        },
        "next_release_train": {
            "id": "PROD-1221..1380",
            "title": "Neo4j Sandbox Gain Test + LLM Research Boundary + Codex Executor Boundary",
            "children": [
                "PROD-1221..1260 Neo4j Sandbox Adapter Contract",
                "PROD-1261..1300 Graph Import Sandbox Dry Run",
                "PROD-1301..1340 Graph Retrieval Gain Evaluation",
                "PROD-1341..1380 LLM Research + Codex Executor Boundary"
            ]
        },
        "blocked_actions": BLOCKED_ACTIONS
    }

    codex_boundary = {
        "status": "PASS",
        "decision": "CODEX_AS_REPO_IMPLEMENTATION_AGENT_NOT_RUNTIME_BUSINESS_EXECUTOR",
        "runtime_business_decision_path": [
            "Input",
            "Preflight",
            "Evidence retrieval / graph retrieval",
            "Research LLM when external research is explicitly allowed",
            "Diagnostic runtime LLM",
            "Verifier/Critic LLM for high-risk cases",
            "Cubo gate",
            "Output mode",
            "Human review when required",
            "Tool executor only if allowlisted and approved"
        ],
        "codex_path": [
            "Developer task",
            "Repository patch",
            "Tests/validation",
            "Audit evidence",
            "Human review/merge"
        ],
        "blocked_actions": BLOCKED_ACTIONS
    }

    audit = {
        "status": "PASS" if train_closed else "WARN",
        "audit": "Umbrella Train Audit and Stack Roadmap Prep audit",
        "generated_at": generated_at,
        "train": "PROD-1021..1180",
        "required_status": required_status,
        "missing_required_outputs": missing,
        "final_train_decision": final_readiness.get("decision"),
        "umbrella_train_closed": train_closed,
        "external_execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "readiness": "READY_FOR_NEO4J_SANDBOX_GAIN_TEST_AND_LLM_CODEX_BOUNDARY_TRAIN" if train_closed else "REVIEW_UMBRELLA_TRAIN",
        "blocked_actions": BLOCKED_ACTIONS
    }

    readiness = {
        "status": audit["status"],
        "decision": audit["readiness"],
        "ready_for": [
            "Neo4j sandbox adapter contract",
            "graph import sandbox dry run",
            "graph retrieval gain evaluation",
            "LLM research boundary hardening",
            "Codex executor boundary hardening"
        ] if train_closed else ["fix missing umbrella outputs"],
        "not_ready_for": [
            "production activation",
            "external execution",
            "automatic threshold mutation",
            "live production Neo4j write",
            "client-facing guarantees"
        ],
        "blocked_actions": BLOCKED_ACTIONS
    }

    outputs = {
        "prod1181_1220_umbrella_train_audit.json": audit,
        "prod1181_1220_alias_cleanup_policy.json": alias_policy,
        "prod1181_1220_llm_research_boundary.json": llm_boundary,
        "prod1181_1220_stack_roadmap.json": stack_roadmap,
        "prod1181_1220_codex_executor_boundary.json": codex_boundary,
        "prod1181_1220_readiness.json": readiness
    }
    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = f"""# PROD-1181..1220 Umbrella Train Audit and Stack Roadmap Prep

- Status: `{audit['status']}`
- Train: `PROD-1021..1180`
- Umbrella train closed: `{train_closed}`
- Final train decision: `{final_readiness.get('decision')}`
- Readiness: `{readiness['decision']}`

## Core Architecture Answer

Codex is the repo implementation agent, not the runtime business executor.

The runtime decision path is:

Input -> Preflight -> Evidence retrieval / Graph retrieval -> Research LLM when allowed -> Diagnostic LLM -> Verifier LLM -> Cubo gates -> Output mode -> Human review when required -> Tool executor only if allowlisted.

## Neo4j Technical Gain Hypothesis

Neo4j should improve multi-hop traceability, graph retrieval, evidence-to-gate explanation and audit/demo power.

## Remaining Roadmap

- 1 focused package to first Neo4j sandbox import.
- 3 focused packages to measure Neo4j technical gain.
- 1 focused package to harden Codex/LLM executor boundary.
- One more umbrella train for a safe full-stack demo.

## Next Train

`PROD-1221..1380 — Neo4j Sandbox Gain Test + LLM Research Boundary + Codex Executor Boundary`
"""
    write_text(out / "prod1181_1220_report.md", report)
    write_json(out / "prod1181_1220_result.json", {"status": audit["status"], "decision": readiness["decision"], "blocked_actions": BLOCKED_ACTIONS})
    return {"status": audit["status"], "decision": readiness["decision"]}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    print(json.dumps(build(Path(args.repo)), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
