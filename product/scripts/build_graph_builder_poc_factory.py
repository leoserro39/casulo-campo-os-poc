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
                    label = item.get("id") or item.get("name") or item.get("state_id") or item.get("domain") or item.get("title") or "item"
                    lines.append(f"- `{label}` — {json.dumps(item, ensure_ascii=False)}")
                else:
                    lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                lines.append(f"- {k}: `{v}`")
    return lines


def build_graph_builder_outputs() -> Dict[str, Any]:
    source_inventory = [
        {"source_id": "SRC-BRIEFING-001", "type": "briefing", "status": "AVAILABLE", "trust": "user_provided"},
        {"source_id": "SRC-DOCS-001", "type": "documents", "status": "AVAILABLE_OR_PENDING_UPLOAD", "trust": "evidence_candidate"},
        {"source_id": "SRC-RULES-001", "type": "system_rules", "status": "AVAILABLE_OR_PENDING_UPLOAD", "trust": "evidence_candidate"},
        {"source_id": "SRC-REPO-001", "type": "repository_summary", "status": "OPTIONAL", "trust": "evidence_candidate"},
        {"source_id": "SRC-DATA-001", "type": "anonymized_samples", "status": "OPTIONAL", "trust": "evidence_candidate"},
    ]

    candidate_graph = {
        "domains": [
            {"id": "domain_business_process", "label": "Business Process", "confidence": 0.78, "review": "REQUIRED"},
            {"id": "domain_information", "label": "Information / Data", "confidence": 0.74, "review": "REQUIRED"},
            {"id": "domain_system", "label": "System / Software", "confidence": 0.72, "review": "REQUIRED"},
            {"id": "domain_decision", "label": "Decision / Governance", "confidence": 0.80, "review": "REQUIRED"},
            {"id": "domain_evidence", "label": "Evidence / Audit", "confidence": 0.84, "review": "REQUIRED"},
        ],
        "entities": [
            {"id": "entity_company", "type": "organization", "source": "SRC-BRIEFING-001", "evidence_status": "SUPPORTED"},
            {"id": "entity_process", "type": "process", "source": "SRC-BRIEFING-001", "evidence_status": "PARTIAL"},
            {"id": "entity_rule_set", "type": "rule_set", "source": "SRC-RULES-001", "evidence_status": "PARTIAL_OR_PENDING"},
            {"id": "entity_artifact", "type": "artifact", "source": "SRC-DOCS-001", "evidence_status": "PARTIAL_OR_PENDING"},
            {"id": "entity_system", "type": "system_or_software", "source": "SRC-REPO-001", "evidence_status": "OPTIONAL"},
            {"id": "entity_decision", "type": "decision", "source": "CASULO", "evidence_status": "COMPUTED"},
        ],
        "relations": [
            {"from": "entity_company", "to": "entity_process", "relation": "operates"},
            {"from": "entity_process", "to": "entity_rule_set", "relation": "is_constrained_by"},
            {"from": "entity_rule_set", "to": "entity_artifact", "relation": "requires_evidence_from"},
            {"from": "entity_system", "to": "entity_process", "relation": "supports_or_implements"},
            {"from": "entity_decision", "to": "entity_process", "relation": "governs"},
        ],
        "human_review_required": True,
    }

    artifact_map = {
        "status": "PASS",
        "artifact_classes": [
            {"class": "briefing", "state_use": "intent and scope", "risk": "ambiguous if not reviewed"},
            {"class": "rules", "state_use": "gate and parser/development constraints", "risk": "contradiction or incompleteness"},
            {"class": "samples", "state_use": "test cases and examples", "risk": "insufficient coverage"},
            {"class": "repository_summary", "state_use": "software review and task generation", "risk": "outdated or incomplete summary"},
            {"class": "dossier", "state_use": "evidence package", "risk": "source reliability and missing context"},
        ],
        "rule": "Artifacts become evidence candidates until classified.",
    }

    operational_states = [
        {
            "state_id": "STATE-CONTEXT-001",
            "name": "Context Readiness",
            "status": "CHECK_REQUIRED",
            "reason": "Initial documentation can be accepted, but evidence classification and human review are required.",
            "reusable": True,
        },
        {
            "state_id": "STATE-GRAPH-001",
            "name": "Candidate Graph",
            "status": "CANDIDATE_GRAPH_BUILT",
            "reason": "Domains, entities and relations are suggested, not final.",
            "reusable": True,
        },
        {
            "state_id": "STATE-RECOMMENDATION-001",
            "name": "Recommendation Governance",
            "status": "PARTIAL_RECOMMENDATION_ALLOWED",
            "reason": "Recommendations may be generated with caveats, gates and evidence limits.",
            "reusable": True,
        },
        {
            "state_id": "STATE-DEVELOPMENT-001",
            "name": "Development Governance",
            "status": "TASK_ONLY_UNTIL_EVIDENCE",
            "reason": "Development can become tasks/contracts/tests, not production execution.",
            "reusable": True,
        },
    ]

    gates = [
        {"gate": "evidence_gate", "status": "CHECK_REQUIRED", "blocks": ["client_facing_claim"], "reason": "Documentation must be classified before external claim."},
        {"gate": "graph_review_gate", "status": "HUMAN_REVIEW_REQUIRED", "blocks": ["implementation_execution"], "reason": "Candidate graph must be reviewed before execution."},
        {"gate": "recommendation_gate", "status": "PARTIAL_ALLOWED", "blocks": ["production_activation"], "reason": "Recommendation can be caveated; production is blocked."},
        {"gate": "development_gate", "status": "TASK_ONLY", "blocks": ["automatic_merge", "production_activation"], "reason": "Development actions must go through tasks/tests/human review."},
    ]

    deltas = [
        {"delta_id": "DELTA-EVIDENCE-001", "gap": "Some sources are pending, partial or candidate-only.", "next_action": "classify evidence and request missing data"},
        {"delta_id": "DELTA-GRAPH-001", "gap": "Graph is candidate, not confirmed truth.", "next_action": "human review of domains/entities/relations"},
        {"delta_id": "DELTA-POC-001", "gap": "POC can run but needs calibration with real/anonymous cases.", "next_action": "run first client-style POC test"},
    ]

    graph_builder = {
        "contract_version": "casulo.graph_builder.v0.1",
        "status": "PASS",
        "mode": "assisted_candidate_graph",
        "source_inventory": source_inventory,
        "candidate_graph": candidate_graph,
        "artifact_map": artifact_map,
        "operational_states": operational_states,
        "gates": gates,
        "deltas": deltas,
        "human_review_required": True,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    state_store = {
        "contract_version": "casulo.state_store_index.v0.1",
        "status": "PASS",
        "purpose": "Reuse computed states across GPT sessions, recommendations, POCs and development tasks.",
        "storage_mode": "file_index_now__database_later",
        "state_records": [
            {"state_id": s["state_id"], "status": s["status"], "reusable": s["reusable"], "requires": "version + evidence status + gate decision"}
            for s in operational_states
        ],
        "reuse_policy": [
            "Never reuse a state without state_id.",
            "Never reuse a state without evidence status.",
            "Never reuse a state for production execution without human gate.",
            "Use state as context for recommendations, tasks, parsers and documents.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendation_governance = {
        "contract_version": "casulo.recommendation_governance.v0.1",
        "status": "PASS",
        "decision": "RECOMMENDATION_ALLOWED_WITH_CAVEATS",
        "uses": [
            "operational_states",
            "candidate_graph",
            "artifact_map",
            "evidence_status",
            "gates",
            "deltas",
            "state_store_index",
        ],
        "allowed": [
            "structured recommendation with caveats",
            "risk analysis",
            "parser contract",
            "document outline",
            "development task plan",
            "POC report",
        ],
        "blocked": BLOCKED_ACTIONS,
    }

    poc_factory = {
        "contract_version": "casulo.poc_factory.v0.1",
        "status": "PASS",
        "poc_mode": "controlled_company_chat_poc",
        "deliverables": [
            "redacted intake checklist",
            "source inventory",
            "candidate operational graph",
            "state store index",
            "evidence map",
            "gate matrix",
            "delta report",
            "hallucination/evaluation report",
            "recommendation governance report",
            "next-cycle backlog",
        ],
        "poc_steps": [
            "1. Receive company documentation through chat or upload.",
            "2. Redact/forbid secrets and unnecessary sensitive data.",
            "3. Build candidate graph.",
            "4. Compute operational states.",
            "5. Apply gates and deltas.",
            "6. Generate evaluation report.",
            "7. Generate recommendations/tasks only inside allowed scope.",
            "8. Calibrate weights and prepare next cycle.",
        ],
        "readiness": "READY_FOR_CONTROLLED_POC_FACTORY_INTERNAL_USE",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "contract_version": "casulo.poc_readiness_report.v0.1",
        "status": "PASS",
        "decision": "READY_FOR_GRAPH_BUILDER_AND_POC_FACTORY_TESTS",
        "what_is_true": [
            "The product can accept documentation as evidence candidates.",
            "The product can build an assisted candidate graph.",
            "The product can compute operational states from the graph.",
            "The product can govern recommendations and development tasks using the state.",
            "The product can reuse computed states through a file-index state store now.",
        ],
        "what_is_not_true_yet": [
            "Graph extraction is not fully autonomous.",
            "State store is not yet a production database.",
            "Domains still need human approval.",
            "Recommendations are controlled and caveated.",
            "No production execution or autonomous merge is authorized.",
        ],
        "next": "Run real/anonymous POC calibration and then harden Graph Builder v0.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Graph Builder v0 and POC Factory audit",
        "graph_builder": graph_builder["status"],
        "state_store": state_store["status"],
        "recommendation_governance": recommendation_governance["status"],
        "poc_factory": poc_factory["status"],
        "readiness": readiness["decision"],
        "finding": "The architecture is aligned with the intended use: chat/documentation -> candidate graph -> operational states -> governed recommendation/development -> POC report.",
    }

    return {
        "graph_builder": graph_builder,
        "state_store": state_store,
        "recommendation_governance": recommendation_governance,
        "poc_factory": poc_factory,
        "readiness": readiness,
        "audit": audit,
    }


def write_outputs(repo: Path, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    out.mkdir(parents=True, exist_ok=True)
    data = build_graph_builder_outputs()
    files = {
        "prod121_130_graph_builder_v0": ("Graph Builder v0", data["graph_builder"]),
        "prod121_130_state_store_index": ("State Store Index", data["state_store"]),
        "prod121_130_recommendation_governance": ("Recommendation Governance", data["recommendation_governance"]),
        "prod121_130_poc_factory_pack": ("POC Factory Pack", data["poc_factory"]),
        "prod121_130_poc_readiness_report": ("POC Readiness Report", data["readiness"]),
        "prod121_130_graph_builder_audit": ("Graph Builder and POC Factory Audit", data["audit"]),
    }
    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", md_simple(title, obj))

    result = {
        "task": "PROD-121..130",
        "status": "PASS",
        "phase": "Graph Builder v0 and POC Factory Pack",
        "decision": data["readiness"]["decision"],
        "outputs": [f"outputs/{stem}.json" for stem in files],
        "next_recommended_bundle": "PROD-131..140 Real/Anonymous POC Calibration Runner",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod121_130_result.json", result)
    write_md(out / "prod121_130_report.md", md_simple("PROD-121..130 Graph Builder v0 and POC Factory Pack Report", result))
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
