#!/usr/bin/env python3
"""
CASULO PROD-7901..7940 - Live Graph Evidence Follow-up and Controlled Sandbox Retrieval Run

Continues after:
  PROD-7861..7900 - Client/Production Claim Boundary Reassessment

Purpose:
  - prepare the controlled sandbox/read-only live graph retrieval evidence follow-up;
  - create an evidence template and local validator for a future Neo4j sandbox retrieval;
  - preserve claim boundaries while live evidence is still pending.

This patcher does NOT:
  - call GPT;
  - connect to Neo4j;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.py --check
  python3 apply_prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

REQUIRED = [
    "outputs/prod7861_7900_client_production_claim_boundary_reassessment.json",
    "product/claim_boundaries/prod7861_7900_client_production_claim_boundary_reassessment.json",
    "product/release_boundaries/prod7861_7900_client_production_release_boundary.json",
    "product/contracts/client_production_claim_boundary_reassessment.contract.json",
    "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
    "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_plan.cypher",
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
    "threshold_scope_expansion_without_future_human_review",
]

REQUIRED_NODES = ["REAL-CASE-001", "GITHUB-AGENT-FOUNDATION-v0.1", "P0-MATRIX-BATCH01"]
REQUIRED_RELS = ["RUNS_CASE", "MEASURED_BY"]

def read_json(path: str | Path, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
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
        "phase": "PROD-7901..7940",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/graph/live_retrieval/prod7901_7940_read_only_query.cypher",
            "product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json",
            "product/graph/live_retrieval/prod7901_7940_controlled_sandbox_retrieval_runbook.md",
            "product/scripts/validate_live_graph_retrieval_evidence.py",
            "outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.json",
            "outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.md",
            "product/contracts/live_graph_evidence_followup_controlled_sandbox_retrieval.contract.json",
            "docs/product/790_LIVE_GRAPH_EVIDENCE_FOLLOWUP_CONTROLLED_SANDBOX_RETRIEVAL.md",
        ],
        "will_call_gpt": False,
        "will_connect_to_neo4j": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def evidence_template() -> Dict[str, Any]:
    return {
        "version": "live_graph_retrieval_evidence.v0.1",
        "phase": "PROD-7901..7940",
        "case_id": "REAL-CASE-001",
        "captured_at": None,
        "captured_by": None,
        "neo4j_environment": "sandbox",
        "query_mode": "READ_ONLY",
        "production_write_executed": False,
        "live_query_executed": False,
        "query_file": "product/graph/live_retrieval/prod7901_7940_read_only_query.cypher",
        "expected": {
            "node_count": 3,
            "relationship_count": 2,
            "node_ids": REQUIRED_NODES,
            "relationship_types": REQUIRED_RELS,
            "graph_path": "GITHUB-AGENT-FOUNDATION-v0.1 -> RUNS_CASE -> REAL-CASE-001 -> MEASURED_BY -> P0-MATRIX-BATCH01",
        },
        "observed": {
            "node_count": None,
            "relationship_count": None,
            "node_ids": [],
            "relationship_types": [],
            "rows_returned": None,
            "graph_path_confirmed": False,
        },
        "validation": {
            "live_evidence_validated": False,
            "validator": "product/scripts/validate_live_graph_retrieval_evidence.py",
            "notes": "Fill observed values after executing the read-only sandbox query.",
        },
        "boundary": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
        },
    }

def validator_script() -> str:
    return """#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_NODES = ["REAL-CASE-001", "GITHUB-AGENT-FOUNDATION-v0.1", "P0-MATRIX-BATCH01"]
REQUIRED_RELS = ["RUNS_CASE", "MEASURED_BY"]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence")
    args = ap.parse_args()

    p = Path(args.evidence)
    data = json.loads(p.read_text(encoding="utf-8"))

    observed = data.get("observed", {})
    node_ids = [str(x) for x in observed.get("node_ids", [])]
    rels = [str(x) for x in observed.get("relationship_types", [])]

    checks = {
        "neo4j_environment_sandbox": data.get("neo4j_environment") == "sandbox",
        "query_mode_read_only": data.get("query_mode") == "READ_ONLY",
        "production_write_not_executed": data.get("production_write_executed") is False,
        "live_query_executed": data.get("live_query_executed") is True,
        "node_count_matches": observed.get("node_count") == 3,
        "relationship_count_matches": observed.get("relationship_count") == 2,
        "required_nodes_present": all(any(req in n for n in node_ids) for req in REQUIRED_NODES),
        "required_relationships_present": all(any(req in r for r in rels) for req in REQUIRED_RELS),
        "graph_path_confirmed": observed.get("graph_path_confirmed") is True,
    }

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "live_graph_retrieval_confirmed": all(checks.values()),
        "client_claim_allowed": False,
        "production_allowed": False,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
"""

def apply() -> List[str]:
    wrote: List[str] = []

    claim = read_json("outputs/prod7861_7900_client_production_claim_boundary_reassessment.json", {})
    live_gate = read_json("outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json", {})

    read_only_query = """// PROD-7901..7940 - Controlled Sandbox Live Graph Retrieval Query
// READ ONLY. Do not run against production Neo4j.
// Expected path:
// GITHUB-AGENT-FOUNDATION-v0.1 -> RUNS_CASE -> REAL-CASE-001 -> MEASURED_BY -> P0-MATRIX-BATCH01

MATCH (agent {id: 'GITHUB-AGENT-FOUNDATION-v0.1'})-[r1:RUNS_CASE]->(case_node {id: 'REAL-CASE-001'})-[r2:MEASURED_BY]->(matrix {id: 'P0-MATRIX-BATCH01'})
RETURN agent.id AS agent_id,
       type(r1) AS relationship_1,
       case_node.id AS case_id,
       type(r2) AS relationship_2,
       matrix.id AS matrix_id;
"""

    runbook = """# PROD-7901..7940 - Controlled Sandbox Retrieval Runbook

## Scope

Read-only sandbox Neo4j retrieval evidence capture.

## Do not do

- Do not run against production Neo4j.
- Do not write to Neo4j.
- Do not make client-facing validation claims.
- Do not activate production.
- Do not claim validated hallucination reduction.

## Steps

1. Use `product/graph/live_retrieval/prod7901_7940_read_only_query.cypher`.
2. Run it only in a sandbox/read-only Neo4j environment.
3. Copy observed node IDs, relationship types, row count and graph path result into:
   `product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json`
4. Set:
   - `live_query_executed=true`
   - `production_write_executed=false`
   - `observed.graph_path_confirmed=true` only if the returned path matches.
5. Validate locally:

```bash
python3 product/scripts/validate_live_graph_retrieval_evidence.py \\
  product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json
```

## Boundary

This runbook prepares evidence only. It does not allow client, production or commercial claims.
"""

    live_gate_decision = live_gate.get("calibration_decision", {})
    claim_decision = claim.get("calibration_decision", {})

    followup = {
        "version": "live_graph_evidence_followup_controlled_sandbox_retrieval.v0.1",
        "phase": "PROD-7901..7940",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "source_claim_boundary_reassessment": "outputs/prod7861_7900_client_production_claim_boundary_reassessment.json",
        "source_live_graph_gate": "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
        "prior_state": {
            "claim_boundary_reassessment_complete": claim_decision.get("claim_boundary_reassessment_complete"),
            "internal_status_reporting_allowed": claim_decision.get("internal_status_reporting_allowed"),
            "ready_for_live_graph_evidence_followup": claim_decision.get("ready_for_live_graph_evidence_followup"),
            "prior_live_graph_retrieval_confirmed": live_gate_decision.get("live_graph_retrieval_confirmed"),
            "offline_graph_payload_complete": live_gate_decision.get("offline_graph_payload_complete"),
            "ready_for_client_claim": False,
            "ready_for_production": False,
        },
        "controlled_sandbox_retrieval": {
            "prepared": True,
            "executed_by_this_patcher": False,
            "requires_external_sandbox_neo4j_read_only_run": True,
            "query_file": "product/graph/live_retrieval/prod7901_7940_read_only_query.cypher",
            "evidence_template": "product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json",
            "validator": "product/scripts/validate_live_graph_retrieval_evidence.py",
            "runbook": "product/graph/live_retrieval/prod7901_7940_controlled_sandbox_retrieval_runbook.md",
        },
        "expected_confirmation": {
            "node_count": 3,
            "relationship_count": 2,
            "required_nodes": REQUIRED_NODES,
            "required_relationships": REQUIRED_RELS,
            "production_write_executed": False,
            "query_mode": "READ_ONLY",
        },
        "boundary": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "validated_hallucination_reduction_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS",
        "phase": "PROD-7901..7940",
        "decision": "LIVE_GRAPH_EVIDENCE_FOLLOWUP_PACK_READY_CONTROLLED_SANDBOX_RETRIEVAL_PENDING",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "live_graph_evidence_followup": followup,
        "calibration_decision": {
            "live_graph_evidence_followup_pack_ready": True,
            "controlled_sandbox_retrieval_executed": False,
            "ready_for_live_graph_evidence_capture": True,
            "live_graph_retrieval_confirmed": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-7941..7980 - Live Graph Evidence Capture Ingestion and Confirmation Evaluation",
    }

    write_text("product/graph/live_retrieval/prod7901_7940_read_only_query.cypher", read_only_query, wrote)
    write_json("product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json", evidence_template(), wrote)
    write_text("product/graph/live_retrieval/prod7901_7940_controlled_sandbox_retrieval_runbook.md", runbook, wrote)
    write_text("product/scripts/validate_live_graph_retrieval_evidence.py", validator_script(), wrote)
    (ROOT / "product/scripts/validate_live_graph_retrieval_evidence.py").chmod(0o755)
    write_json("outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.json", result, wrote)

    md = [
        "# PROD-7901..7940 - Live Graph Evidence Follow-up and Controlled Sandbox Retrieval Run",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Prepared",
        "",
        "- Read-only Cypher query: prepared",
        "- Evidence template: prepared",
        "- Local validator: prepared",
        "- Sandbox retrieval executed by this patcher: False",
        "- Ready for live graph evidence capture: True",
        "",
        "## Boundary",
        "",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Scope expansion requires future human review: True",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.md", "\n".join(md), wrote)

    contract = {
        "contract": "live_graph_evidence_followup_controlled_sandbox_retrieval.contract.v0.1",
        "phase": "PROD-7901..7940",
        "requires": REQUIRED,
        "live_graph_evidence_followup_pack_ready": True,
        "controlled_sandbox_retrieval_executed": False,
        "ready_for_live_graph_evidence_capture": True,
        "live_graph_retrieval_confirmed": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/live_graph_evidence_followup_controlled_sandbox_retrieval.contract.json", contract, wrote)

    docs = """# 790 - Live Graph Evidence Follow-up and Controlled Sandbox Retrieval Run

This phase prepares a controlled sandbox/read-only retrieval evidence package.

It creates:
- a read-only Cypher query;
- a live graph evidence template;
- a local validator;
- a runbook.

This patcher does not connect to Neo4j and does not confirm live retrieval.

Client-facing claims, production activation and commercial claims remain blocked.
"""
    write_text("docs/product/790_LIVE_GRAPH_EVIDENCE_FOLLOWUP_CONTROLLED_SANDBOX_RETRIEVAL.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.py",
        "product/graph/live_retrieval/prod7901_7940_read_only_query.cypher",
        "product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json",
        "product/graph/live_retrieval/prod7901_7940_controlled_sandbox_retrieval_runbook.md",
        "product/scripts/validate_live_graph_retrieval_evidence.py",
        "outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.json",
        "outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.md",
        "product/contracts/live_graph_evidence_followup_controlled_sandbox_retrieval.contract.json",
        "docs/product/790_LIVE_GRAPH_EVIDENCE_FOLLOWUP_CONTROLLED_SANDBOX_RETRIEVAL.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add live graph evidence follow-up pack"',
        'git tag -a product-casulo-live-graph-evidence-followup-pack-v0.1 HEAD -m "CASULO live graph evidence followup pack v0.1"',
        "git push origin main",
        "git push origin product-casulo-live-graph-evidence-followup-pack-v0.1",
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
