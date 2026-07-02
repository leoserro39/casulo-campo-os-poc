#!/usr/bin/env python3
"""
CASULO PROD-8061A - Exocortex Foundation Statement Addendum

Purpose:
  - explicitly register Exocortex as an ACTIVE pillar of the current POC;
  - define memory as mesh and GPT memory as a family of domains;
  - separate what is already proven from what is still missing;
  - keep micrographs, Delta Matrix, state family and multi-LLM braid OUT of the current POC;
  - prepare the next phase: PROD-8101..8140 Agent Instruction Pack + Runtime Context Packet.

This addendum should be run AFTER PROD-8061..8100 has been applied locally
and BEFORE committing, so both 8061 and 8061A can be committed together.

This patcher does NOT:
  - connect to Neo4j;
  - run Cypher;
  - write to Neo4j;
  - implement micrographs;
  - implement Delta Matrix;
  - call GPT;
  - dispatch GitHub Actions;
  - activate production;
  - allow client/commercial/production claims.

Usage:
  python3 apply_prod8061a_exocortex_foundation_statement_addendum.py --check
  python3 apply_prod8061a_exocortex_foundation_statement_addendum.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8061A"

REQUIRED = [
    "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json",
]

OPTIONAL_BUT_EXPECTED = [
    "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
    "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json",
    "product/release_boundaries/prod8061_8100_scope_boundary_review.json",
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
    "micrograph_runtime_claim",
    "delta_matrix_runtime_claim",
    "state_family_runtime_claim",
    "multi_llm_braid_runtime_claim",
]

MEMORY_DOMAINS = [
    {
        "domain": "GPT_MEMORY_MESH_DOMAIN",
        "type": "ROOT_DOMAIN",
        "purpose": "Root domain for GPT/Codex/agent memory as governed operational mesh.",
    },
    {
        "domain": "SESSION_CONTEXT_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Current session context; useful but not canonical unless triaged.",
    },
    {
        "domain": "PROJECT_CANONICAL_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Frozen definitions, accepted decisions and current project state.",
    },
    {
        "domain": "USER_OPERATIONAL_PREFERENCE_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Operator workflow preferences and execution style.",
    },
    {
        "domain": "EVIDENCE_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Memory backed by artifacts, outputs, commits, tags and reports.",
    },
    {
        "domain": "CLAIM_BOUNDARY_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Allowed and blocked claims, especially client/production/commercial limits.",
    },
    {
        "domain": "ROADMAP_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Current phase, next phase, roadmap dependencies and allowed progression.",
    },
    {
        "domain": "CODE_EXECUTION_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Commands, patchers, checks, apply results, commits, tags and validation outputs.",
    },
    {
        "domain": "GRAPH_STATE_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Neo4j-backed live operational state: cases, domains, evidence, gates, outputs and relationships.",
    },
    {
        "domain": "CONCEPT_ONTOLOGY_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Canonical definitions: Exocortex, state, memory, evidence, cache, gate, delta, point zero.",
    },
    {
        "domain": "CACHE_TRANSIENT_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Temporary context useful for execution but not canonical source of truth.",
    },
    {
        "domain": "STALE_OR_SUPERSEDED_MEMORY_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Outdated, corrected or superseded memory retained for audit but not injected as current truth.",
    },
    {
        "domain": "RUNTIME_CONTEXT_PACKET_DOMAIN",
        "type": "SUBDOMAIN",
        "purpose": "Clean minimum context packet delivered to GPT/Codex/agent for a specific task.",
    },
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
    optional_missing = [p for p in OPTIONAL_BUT_EXPECTED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": PHASE,
        "missing_required_count": len(missing),
        "missing_required": missing,
        "optional_expected_missing_count": len(optional_missing),
        "optional_expected_missing": optional_missing,
        "note": "Optional 8061 files are expected when running after PROD-8061 apply, but this addendum can still document Exocortex Foundation from PROD-8021.",
        "will_create": [
            "product/exocortex/prod8061a_exocortex_foundation_statement.json",
            "product/exocortex/prod8061a_exocortex_foundation_statement.md",
            "product/contracts/exocortex_memory_mesh_foundation.contract.json",
            "outputs/prod8061a_exocortex_foundation_statement_addendum.json",
            "docs/product/806A_EXOCORTEX_FOUNDATION_STATEMENT.md",
        ],
        "will_implement_micrographs": False,
        "will_implement_delta_matrix": False,
        "will_implement_state_family": False,
        "will_implement_multi_llm_braid": False,
        "will_connect_to_neo4j": False,
        "will_run_cypher": False,
        "will_write_neo4j": False,
        "will_call_gpt": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
    }

def evaluate() -> Dict[str, Any]:
    result8021 = read_json("outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json", {})
    result8061 = read_json("outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json", {})

    cal8021 = result8021.get("calibration_decision", {})
    cal8061 = result8061.get("calibration_decision", {})

    checks = {
        "prior_8021_status_pass": result8021.get("status") == "PASS",
        "prior_8021_phase_ok": result8021.get("phase") == "PROD-8021..8060",
        "exp50_retrieval_confirmed": cal8021.get("exp50_read_only_retrieval_result_confirmed") is True,
        "live_neo4j_sandbox_confirmed": cal8021.get("live_neo4j_sandbox_confirmed") is True,
        "actual_graph_family_exp50": cal8021.get("actual_graph_family_confirmed") == "EXP50",
        "observed_nodes_8": cal8021.get("observed_nodes_in_path") == 8,
        "observed_relationships_7": cal8021.get("observed_relationships_in_path") == 7,
        "client_claim_blocked": cal8021.get("ready_for_client_claim") is False,
        "production_blocked": cal8021.get("ready_for_production") is False,
        "commercial_claim_blocked": cal8021.get("commercial_claim_allowed") is False,
    }

    optional_8061_present = bool(result8061)
    if optional_8061_present:
        checks.update({
            "local_8061_operator_packet_ready_if_present": cal8061.get("operator_evidence_packet_ready") is True,
            "local_8061_client_claim_blocked_if_present": cal8061.get("ready_for_client_claim") is False,
            "local_8061_production_blocked_if_present": cal8061.get("ready_for_production") is False,
            "local_8061_commercial_blocked_if_present": cal8061.get("commercial_claim_allowed") is False,
        })

    ready = all(checks.values())

    return {
        "checks": checks,
        "exocortex_foundation_active": ready,
        "memory_as_mesh": True,
        "gpt_memory_mode": "FAMILY_OF_DOMAINS_UNDER_GPT_MEMORY_MESH_DOMAIN",
        "state_as_live_graph": cal8021.get("live_neo4j_sandbox_confirmed") is True,
        "graph_memory_required": True,
        "context_reconstruction_required": True,
        "evidence_bound_to_state": cal8021.get("exp50_read_only_retrieval_result_confirmed") is True,
        "claim_boundary_active": (
            cal8021.get("ready_for_client_claim") is False and
            cal8021.get("ready_for_production") is False and
            cal8021.get("commercial_claim_allowed") is False
        ),
        "operator_packet_local_8061_present": optional_8061_present,
        "runtime_exocortex_module_complete": False,
        "micrographs_implemented": False,
        "delta_matrix_implemented": False,
        "state_family_implemented": False,
        "multi_llm_braid_implemented": False,
        "solution_factory_implemented": False,
        "dashboard_multi_area_implemented": False,
        "inference_gate_runtime_implemented": False,
        "inference_gate_next_phase_candidate": True,
        "next_phase": "PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    ev = evaluate()
    status = "PASS" if ev["exocortex_foundation_active"] else "FAIL"
    decision = (
        "EXOCORTEX_FOUNDATION_ACTIVE_MEMORY_MESH_DOMAIN_MODEL_READY_FOR_AGENT_INSTRUCTION_PACK"
        if status == "PASS"
        else
        "EXOCORTEX_FOUNDATION_NOT_READY_REVIEW_REQUIRED"
    )

    foundation = {
        "version": "exocortex_foundation_statement.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "status": status,
        "decision": decision,
        "definition": {
            "canonical": "Exocortex CASULO is the live operational memory and state governance layer that stores decisions, evidence, limits, concepts, gates, deltas and trajectory in the graph and reconstructs the minimum correct context for GPT/Codex/agents.",
            "short": "The Exocortex is the living mesh that prevents the agent from forgetting, inventing, or acting above supported state.",
        },
        "what_is_already_present_in_current_poc": {
            "memory_as_versioned_artifacts": True,
            "state_as_live_graph": ev["state_as_live_graph"],
            "exp50_read_only_retrieval_confirmed": ev["evidence_bound_to_state"],
            "evidence_bound_to_state": ev["evidence_bound_to_state"],
            "claim_boundary_active": ev["claim_boundary_active"],
            "operator_packet_local_8061_present": ev["operator_packet_local_8061_present"],
        },
        "what_is_not_implemented_yet": {
            "runtime_exocortex_module_complete": False,
            "automatic_memory_governor": False,
            "runtime_context_packet_builder": False,
            "graph_memory_ingestion_policy": False,
            "graph_memory_retrieval_policy": False,
            "stale_memory_blocking_runtime": False,
            "micrographs_implemented": False,
            "delta_matrix_implemented": False,
            "state_family_implemented": False,
            "multi_llm_braid_implemented": False,
            "solution_factory_implemented": False,
            "dashboard_multi_area_implemented": False,
        },
        "memory_domain_model": {
            "mode": ev["gpt_memory_mode"],
            "root_domain": "GPT_MEMORY_MESH_DOMAIN",
            "domains": MEMORY_DOMAINS,
        },
        "boundaries": {
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "micrograph_runtime_claim_allowed": False,
            "delta_matrix_runtime_claim_allowed": False,
            "state_family_runtime_claim_allowed": False,
            "multi_llm_braid_runtime_claim_allowed": False,
        },
        "next": ev["next_phase"],
    }

    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "evaluation": ev,
        "exocortex_foundation_statement": foundation,
        "calibration_decision": {
            "exocortex_foundation_active": ev["exocortex_foundation_active"],
            "memory_as_mesh": ev["memory_as_mesh"],
            "gpt_memory_as_family_of_domains": True,
            "state_as_live_graph": ev["state_as_live_graph"],
            "graph_memory_required": ev["graph_memory_required"],
            "context_reconstruction_required": ev["context_reconstruction_required"],
            "evidence_bound_to_state": ev["evidence_bound_to_state"],
            "claim_boundary_active": ev["claim_boundary_active"],
            "runtime_exocortex_module_complete": False,
            "micrographs_implemented": False,
            "delta_matrix_implemented": False,
            "ready_for_agent_instruction_pack": status == "PASS",
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
        },
        "next": ev["next_phase"],
    }

    write_json("product/exocortex/prod8061a_exocortex_foundation_statement.json", foundation, wrote)

    md = f"""# PROD-8061A - Exocortex Foundation Statement Addendum

Status: {status}  
Decision: `{decision}`

## Canonical definition

Exocortex CASULO is the live operational memory and state governance layer that stores decisions, evidence, limits, concepts, gates, deltas and trajectory in the graph and reconstructs the minimum correct context for GPT/Codex/agents.

Short form:

```text
The Exocortex is the living mesh that prevents the agent from forgetting, inventing, or acting above supported state.
```

## What is already present in the current POC

- Memory as versioned artifacts: true
- State as live graph: {ev['state_as_live_graph']}
- EXP50 read-only retrieval confirmed: {ev['evidence_bound_to_state']}
- Evidence bound to state: {ev['evidence_bound_to_state']}
- Claim boundary active: {ev['claim_boundary_active']}
- Local 8061 operator packet present: {ev['operator_packet_local_8061_present']}

## What is not implemented yet

- Runtime Exocortex module complete: false
- Automatic memory governor: false
- Runtime Context Packet Builder: false
- Graph memory ingestion/retrieval policy: false
- Stale memory blocking runtime: false
- Micrographs: false
- Delta Matrix: false
- State Family: false
- Multi-LLM braid: false
- Solution Factory: false
- Multi-area dashboard: false

## GPT memory model

Memory is not a single flat domain. GPT memory is modeled as a family of domains under:

```text
GPT_MEMORY_MESH_DOMAIN
```

Domains:

{chr(10).join('- `' + d['domain'] + '` - ' + d['purpose'] for d in MEMORY_DOMAINS)}

## Boundary

This addendum does not authorize client-facing claims, production activation, commercial claims, micrograph runtime claims, Delta Matrix runtime claims, state-family runtime claims or multi-LLM braid runtime claims.

## Next

PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack
"""
    write_text("product/exocortex/prod8061a_exocortex_foundation_statement.md", md, wrote)

    contract = {
        "contract": "exocortex_memory_mesh_foundation.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "optional_expected": OPTIONAL_BUT_EXPECTED,
        "status": status,
        "decision": decision,
        "exocortex_foundation_active": ev["exocortex_foundation_active"],
        "memory_as_mesh": ev["memory_as_mesh"],
        "gpt_memory_as_family_of_domains": True,
        "runtime_exocortex_module_complete": False,
        "micrographs_implemented": False,
        "delta_matrix_implemented": False,
        "state_family_implemented": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/exocortex_memory_mesh_foundation.contract.json", contract, wrote)
    write_json("outputs/prod8061a_exocortex_foundation_statement_addendum.json", result, wrote)

    docs = """# 806A - Exocortex Foundation Statement Addendum

This addendum explicitly registers Exocortex as an active pillar of the current CASULO POC.

The current POC tests Exocortex Foundation:
- memory as mesh;
- state as live graph;
- evidence bound to state;
- claim boundary active;
- context reconstruction required.

It does not implement micrographs, Delta Matrix, State Family, multi-LLM braid, Solution Factory or multi-area dashboard.

The next recommended phase is `PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack`.
"""
    write_text("docs/product/806A_EXOCORTEX_FOUNDATION_STATEMENT.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.py",
        "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json",
        "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.md",
        "product/release_boundaries/prod8061_8100_scope_boundary_review.json",
        "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
        "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.md",
        "product/contracts/exp50_operator_evidence_packet_scope_boundary_review.contract.json",
        "docs/product/806_EXP50_OPERATOR_EVIDENCE_PACKET_SCOPE_BOUNDARY_REVIEW.md",
        "apply_prod8061a_exocortex_foundation_statement_addendum.py",
        "product/exocortex/prod8061a_exocortex_foundation_statement.json",
        "product/exocortex/prod8061a_exocortex_foundation_statement.md",
        "product/contracts/exocortex_memory_mesh_foundation.contract.json",
        "outputs/prod8061a_exocortex_foundation_statement_addendum.json",
        "docs/product/806A_EXOCORTEX_FOUNDATION_STATEMENT.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add EXP50 operator packet and Exocortex foundation statement"',
        'git tag -a product-casulo-exp50-operator-evidence-exocortex-foundation-v0.1 HEAD -m "CASULO EXP50 operator evidence and Exocortex foundation v0.1"',
        "git push origin main",
        "git push origin product-casulo-exp50-operator-evidence-exocortex-foundation-v0.1",
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
