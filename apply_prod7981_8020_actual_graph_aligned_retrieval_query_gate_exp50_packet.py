#!/usr/bin/env python3
"""
CASULO PROD-7981..8020 - Actual Graph Aligned Retrieval Query Gate and EXP50 Evidence Packet

Continues after:
  PROD-7941..7980 - Live Neo4j Actual Graph Evidence Ingestion and Alignment Evaluation

Purpose:
  - create a read-only retrieval query aligned to the actual persisted EXP50 graph;
  - create an EXP50 evidence packet based on the confirmed live Neo4j state;
  - prepare the next controlled sandbox read-only execution step;
  - preserve all claim/production/commercial boundaries.

This patcher does NOT:
  - connect to Neo4j;
  - run Cypher;
  - write to Neo4j;
  - delete Docker volumes;
  - reimport graph data;
  - call GPT;
  - dispatch GitHub Actions;
  - allow client or production claims.

Usage:
  python3 apply_prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.py --check
  python3 apply_prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

PHASE = "PROD-7981..8020"

REQUIRED = [
    "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
    "outputs/prod7901_correction_live_neo4j_actual_graph_state.json",
    "product/graph/live_retrieval/prod7901_7940_real_live_graph_probe.txt",
    "product/graph/live_retrieval/safety/prod7901_correction_live_neo4j_preservation_evidence.txt",
]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_neo4j_write",
    "neo4j_delete",
    "neo4j_reimport",
    "docker_volume_delete",
    "threshold_scope_expansion_without_future_human_review",
]

def read_json(path: str, default: Any = None) -> Any:
    p = ROOT / path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    wrote.append(path)

def write_text(path: str, text: str, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    wrote.append(path)

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": PHASE,
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher",
            "product/graph/live_retrieval/prod7981_8020_exp50_evidence_packet.json",
            "product/graph/live_retrieval/prod7981_8020_controlled_read_only_execution_runbook.md",
            "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json",
            "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.md",
            "product/contracts/actual_graph_aligned_retrieval_query_gate_exp50_packet.contract.json",
            "docs/product/798_ACTUAL_GRAPH_ALIGNED_RETRIEVAL_QUERY_GATE_EXP50_PACKET.md",
        ],
        "will_connect_to_neo4j": False,
        "will_run_cypher": False,
        "will_write_neo4j": False,
        "will_delete_volume": False,
        "will_reimport_graph": False,
        "will_call_gpt": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def aligned_query() -> str:
    return """// PROD-7981..8020 - EXP50 actual graph aligned retrieval query
// READ ONLY. Sandbox only.
// Do not run against production Neo4j.
// This query is aligned to the confirmed persisted graph:
// node_count=313, relationship_count=350, case_id_pattern=case:EXP50-*
//
// Expected core path for sample case EXP50-001:
// case:EXP50-001
//   -[:BELONGS_TO]-> domain:restaurant_inventory
//   -[:HAS_EVIDENCE]-> evidence:EXP50-001:complete_minimum_evidence
//   -[:TRIGGERS]-> risk:EXP50-001:clean_controlled_answer
//   -[:HAS_BUDGET]-> budget:EXP50-001
//   -[:REQUIRES]-> readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY
// risk:EXP50-001:clean_controlled_answer
//   -[:CONTRIBUTES_TO]-> gate:EXP50-001:ANSWER_ALLOWED
// gate:EXP50-001:ANSWER_ALLOWED
//   -[:ALLOWS]-> output:EXP50-001:ANSWER

MATCH (case_node {id: 'case:EXP50-001'})
OPTIONAL MATCH (case_node)-[belongs:BELONGS_TO]->(domain)
OPTIONAL MATCH (case_node)-[evidence_rel:HAS_EVIDENCE]->(evidence)
OPTIONAL MATCH (case_node)-[budget_rel:HAS_BUDGET]->(budget)
OPTIONAL MATCH (case_node)-[requires_rel:REQUIRES]->(readiness)
OPTIONAL MATCH (case_node)-[triggers_rel:TRIGGERS]->(risk)
OPTIONAL MATCH (risk)-[contributes_rel:CONTRIBUTES_TO]->(gate)
OPTIONAL MATCH (gate)-[allows_rel:ALLOWS]->(output)
RETURN
  case_node.id AS case_id,
  domain.id AS domain_id,
  evidence.id AS evidence_id,
  budget.id AS budget_id,
  readiness.id AS readiness_id,
  risk.id AS risk_id,
  gate.id AS gate_id,
  output.id AS output_id,
  [x IN [type(belongs), type(evidence_rel), type(budget_rel), type(requires_rel), type(triggers_rel), type(contributes_rel), type(allows_rel)] WHERE x IS NOT NULL] AS relationship_types,
  size([x IN [domain, evidence, budget, readiness, risk, gate, output] WHERE x IS NOT NULL]) + 1 AS nodes_observed,
  size([x IN [belongs, evidence_rel, budget_rel, requires_rel, triggers_rel, contributes_rel, allows_rel] WHERE x IS NOT NULL]) AS relationships_observed;
"""

def runbook() -> str:
    return """# PROD-7981..8020 - Controlled Read-Only EXP50 Retrieval Runbook

## Scope

Run the EXP50 aligned retrieval query only against the existing Neo4j sandbox container.

## Must not do

- Do not run against production Neo4j.
- Do not write to Neo4j.
- Do not delete Docker volumes.
- Do not reimport graph data.
- Do not make client-facing claims.
- Do not activate production.

## Confirmed current sandbox

- Container: `casulo-neo4j-sandbox`
- Browser: `7474`
- Bolt: `7687`
- Data volume: `config_casulo_neo4j_data`
- Confirmed graph family: `EXP50`
- Confirmed counts: 313 nodes, 350 relationships

## Execute manually

```bash
cd /workspaces/casulo-campo-os-poc || return 1

NEO4J_PASS="$(grep -E 'NEO4J_AUTH:' product/config/neo4j_sandbox_docker_compose.example.yml | sed -E 's/.*neo4j\\/([^"]+)".*/\\1/')"

docker exec -i casulo-neo4j-sandbox \\
  cypher-shell \\
  -u neo4j \\
  -p "$NEO4J_PASS" \\
  < product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher \\
  | tee product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt
```

## Expected result

The result should return one row for `case:EXP50-001` and should include the available operational path elements for:
domain, evidence, budget, readiness, risk, gate and output.

The next phase must ingest the result file. Do not mark confirmed before the result file exists.
"""

def evaluate_inputs() -> Dict[str, Any]:
    alignment = read_json("outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json", {})
    correction = read_json("outputs/prod7901_correction_live_neo4j_actual_graph_state.json", {})

    cal = alignment.get("calibration_decision", {})
    observed = correction.get("observed_live_graph", {})

    checks = {
        "prior_7941_status_pass": alignment.get("status") == "PASS",
        "prior_7941_phase_ok": alignment.get("phase") == "PROD-7941..7980",
        "live_neo4j_sandbox_confirmed": cal.get("live_neo4j_sandbox_confirmed") is True,
        "actual_graph_family_exp50": cal.get("actual_graph_family_confirmed") == "EXP50",
        "node_count_313": cal.get("actual_node_count") == 313,
        "relationship_count_350": cal.get("actual_relationship_count") == 350,
        "stale_7901_superseded": cal.get("prod7901_stale_target_query_superseded") is True,
        "ready_for_actual_graph_aligned_retrieval_gate": cal.get("ready_for_actual_graph_aligned_retrieval_gate") is True,
        "client_claim_blocked": cal.get("ready_for_client_claim") is False,
        "production_blocked": cal.get("ready_for_production") is False,
        "commercial_claim_blocked": cal.get("commercial_claim_allowed") is False,
        "case_pattern_exp50": observed.get("case_id_pattern") == "case:EXP50-*",
    }

    ready = all(checks.values())

    return {
        "checks": checks,
        "ready_to_prepare_exp50_retrieval_gate": ready,
        "graph_family": "EXP50",
        "sample_case_id": "case:EXP50-001",
        "node_count": 313,
        "relationship_count": 350,
        "query_execution_done_by_this_patcher": False,
        "read_only_query_ready": ready,
        "ready_for_controlled_read_only_execution": ready,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "human_review_required_for_scope_expansion": True,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    ev = evaluate_inputs()

    decision = (
        "EXP50_ALIGNED_READ_ONLY_RETRIEVAL_QUERY_GATE_READY_EXECUTION_PENDING"
        if ev["ready_to_prepare_exp50_retrieval_gate"]
        else
        "EXP50_ALIGNED_RETRIEVAL_QUERY_GATE_NOT_READY_REVIEW_REQUIRED"
    )

    packet = {
        "version": "exp50_aligned_retrieval_query_gate_packet.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "decision": decision,
        "source_alignment": "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
        "source_correction": "outputs/prod7901_correction_live_neo4j_actual_graph_state.json",
        "neo4j_sandbox": {
            "container": "casulo-neo4j-sandbox",
            "browser_port": 7474,
            "bolt_port": 7687,
            "data_volume": "config_casulo_neo4j_data",
            "graph_family": "EXP50",
            "node_count": 313,
            "relationship_count": 350,
        },
        "retrieval_gate": {
            "query_file": "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher",
            "runbook": "product/graph/live_retrieval/prod7981_8020_controlled_read_only_execution_runbook.md",
            "expected_result_file": "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt",
            "sample_case_id": "case:EXP50-001",
            "query_mode": "READ_ONLY",
            "execution_done_by_this_patcher": False,
            "execution_pending": True,
        },
        "evaluation": ev,
        "boundary": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "validated_hallucination_reduction_claim_allowed": False,
            "validated_model_gain_claim_allowed": False,
            "production_write_executed": False,
            "delete_executed": False,
            "reimport_executed": False,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS" if ev["ready_to_prepare_exp50_retrieval_gate"] else "FAIL",
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "EXP50_GRAPH_SET",
        "exp50_aligned_retrieval_query_gate_packet": packet,
        "calibration_decision": {
            "exp50_aligned_query_gate_ready": ev["read_only_query_ready"],
            "controlled_read_only_execution_pending": True,
            "query_execution_done_by_this_patcher": False,
            "ready_for_controlled_read_only_execution": ev["ready_for_controlled_read_only_execution"],
            "ready_for_exp50_result_ingestion": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-8021..8060 - EXP50 Read-Only Retrieval Result Ingestion and Confirmation Gate",
    }

    write_text("product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher", aligned_query(), wrote)
    write_json("product/graph/live_retrieval/prod7981_8020_exp50_evidence_packet.json", packet, wrote)
    write_text("product/graph/live_retrieval/prod7981_8020_controlled_read_only_execution_runbook.md", runbook(), wrote)
    write_json("outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json", result, wrote)

    md = [
        "# PROD-7981..8020 - Actual Graph Aligned Retrieval Query Gate and EXP50 Evidence Packet",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Confirmed basis",
        "",
        "- Live Neo4j sandbox: confirmed by PROD-7941",
        "- Actual graph family: EXP50",
        "- Node count: 313",
        "- Relationship count: 350",
        "- PROD-7901 stale target: superseded",
        "",
        "## Created",
        "",
        "- EXP50 aligned read-only query",
        "- EXP50 evidence packet",
        "- Controlled read-only execution runbook",
        "",
        "## Boundary",
        "",
        "- No Neo4j connection by this patcher",
        "- No Cypher execution by this patcher",
        "- No write/delete/reimport",
        "- Client/production/commercial claims remain blocked",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.md", "\n".join(md), wrote)

    contract = {
        "contract": "actual_graph_aligned_retrieval_query_gate_exp50_packet.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": result["status"],
        "decision": decision,
        "graph_family": "EXP50",
        "sample_case_id": "case:EXP50-001",
        "read_only_query_file": "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher",
        "ready_for_controlled_read_only_execution": ev["ready_for_controlled_read_only_execution"],
        "execution_done_by_this_patcher": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/actual_graph_aligned_retrieval_query_gate_exp50_packet.contract.json", contract, wrote)

    docs = """# 798 - Actual Graph Aligned Retrieval Query Gate and EXP50 Evidence Packet

This phase supersedes the stale PROD-7901 target query and prepares the actual EXP50-aligned read-only retrieval query.

It does not connect to Neo4j and does not run Cypher.

The next phase must ingest the result of the controlled read-only execution.

Boundaries remain:
- no production activation;
- no production Neo4j write;
- no delete or reimport;
- no client-facing validated claim;
- no commercial claim;
- no validated hallucination-reduction claim.
"""
    write_text("docs/product/798_ACTUAL_GRAPH_ALIGNED_RETRIEVAL_QUERY_GATE_EXP50_PACKET.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.py",
        "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher",
        "product/graph/live_retrieval/prod7981_8020_exp50_evidence_packet.json",
        "product/graph/live_retrieval/prod7981_8020_controlled_read_only_execution_runbook.md",
        "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json",
        "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.md",
        "product/contracts/actual_graph_aligned_retrieval_query_gate_exp50_packet.contract.json",
        "docs/product/798_ACTUAL_GRAPH_ALIGNED_RETRIEVAL_QUERY_GATE_EXP50_PACKET.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add EXP50 aligned retrieval query gate"',
        'git tag -a product-casulo-exp50-aligned-retrieval-query-gate-v0.1 HEAD -m "CASULO EXP50 aligned retrieval query gate v0.1"',
        "git push origin main",
        "git push origin product-casulo-exp50-aligned-retrieval-query-gate-v0.1",
    ])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    args = ap.parse_args()

    if not any(vars(args).values()):
        args.check = True

    if args.check:
        print(json.dumps(check(), indent=2, ensure_ascii=False))

    if args.apply:
        c = check()
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        wrote = apply()
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
