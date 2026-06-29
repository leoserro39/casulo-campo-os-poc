#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

PROVIDER_CONTRACTS = [
    {"provider": "mock", "mode": "local_fixture", "network_call_allowed": False, "credential_required": False, "role": "safe deterministic adapter validation"},
    {"provider": "tavily", "mode": "contract_only", "network_call_allowed": False, "credential_required": True, "role": "search/extract/crawl candidate provider when credentials are explicitly configured"},
    {"provider": "exa", "mode": "contract_only", "network_call_allowed": False, "credential_required": True, "role": "semantic/web/research candidate provider when credentials are explicitly configured"},
    {"provider": "perplexity", "mode": "contract_only", "network_call_allowed": False, "credential_required": True, "role": "research synthesis provider; never trusted as committed evidence without source verification"},
]

TRUST_RULES = [
    {"level": "A", "source_types": ["official_doc", "regulator", "standard", "source_repo", "original_paper"]},
    {"level": "B", "source_types": ["vendor_doc", "api_reference", "release_note", "technical_doc"]},
    {"level": "C", "source_types": ["aggregator", "news", "secondary_article", "research_synthesis"]},
    {"level": "D", "source_types": ["forum", "blog", "unknown", "stale"]},
]

MOCK_EVIDENCE = [
    {
        "source_provider": "mock",
        "source_url": "https://example.org/official/casulo-evidence-policy",
        "source_type": "official_doc",
        "claim": "External evidence must be treated as candidate evidence until validated by trust and citation gates.",
        "supporting_excerpt": "External evidence requires source URL, retrieval timestamp, claim mapping, excerpt and gate decision.",
        "primary_source": True,
        "citation_support": "supported",
        "freshness_status": "current",
    },
    {
        "source_provider": "mock",
        "source_url": "https://example.org/research/agent-search-summary",
        "source_type": "research_synthesis",
        "claim": "Search or research providers can help discover sources but should not automatically become committed evidence.",
        "supporting_excerpt": "Aggregated answers are useful for discovery, while primary sources remain required for committed evidence.",
        "primary_source": False,
        "citation_support": "partial",
        "freshness_status": "possibly_stale",
    },
    {
        "source_provider": "mock",
        "source_url": "https://example.org/forum/unsourced-advice",
        "source_type": "forum",
        "claim": "Forum content without citation is sufficient for operational decisions.",
        "supporting_excerpt": "",
        "primary_source": False,
        "citation_support": "unsupported",
        "freshness_status": "unknown",
    },
]

COMMON_WORKLOADS = [
    "parser",
    "document_field_extraction",
    "email_triage",
    "receipt_invoice_extraction",
    "contract_checklist",
    "policy_rule_extraction",
    "summary",
    "classification",
    "technical_review",
    "task_generation",
    "delta_detection",
    "evidence_gap_detection",
]

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def trust_level(source_type: str) -> str:
    for rule in TRUST_RULES:
        if source_type in rule["source_types"]:
            return rule["level"]
    return "D"

def gate_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    level = trust_level(candidate.get("source_type", "unknown"))
    has_url = bool(candidate.get("source_url"))
    has_excerpt = bool(candidate.get("supporting_excerpt"))
    citation_support = candidate.get("citation_support")
    primary = bool(candidate.get("primary_source"))

    if not has_url or citation_support == "unsupported":
        gate = "REJECTED"
        reason = "missing_url_or_unsupported_citation"
    elif level == "A" and primary and has_excerpt and citation_support == "supported":
        gate = "COMMITTED_EVIDENCE"
        reason = "primary_supported_source"
    elif level in ["A", "B"] and has_excerpt and citation_support in ["supported", "partial"]:
        gate = "EVIDENCE_CANDIDATE"
        reason = "trusted_source_candidate_requires_review"
    elif level == "C":
        gate = "HUMAN_REVIEW_REQUIRED"
        reason = "aggregator_or_secondary_source_requires_review"
    else:
        gate = "REJECTED"
        reason = "low_trust_or_insufficient_support"

    return {
        **candidate,
        "trust_level": level,
        "gate": gate,
        "gate_reason": reason,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def build(repo: Path, query: str) -> Dict[str, Any]:
    out = repo / "outputs"
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    candidates = []
    for idx, raw in enumerate(MOCK_EVIDENCE, 1):
        enriched = {"evidence_id": f"EXT-EVID-521-{idx:03d}", "query": query, "retrieved_at": retrieved_at, **raw}
        candidates.append(gate_candidate(enriched))

    counts = {
        "candidate_count": len(candidates),
        "committed_count": sum(1 for c in candidates if c["gate"] == "COMMITTED_EVIDENCE"),
        "evidence_candidate_count": sum(1 for c in candidates if c["gate"] == "EVIDENCE_CANDIDATE"),
        "human_review_count": sum(1 for c in candidates if c["gate"] == "HUMAN_REVIEW_REQUIRED"),
        "rejected_count": sum(1 for c in candidates if c["gate"] == "REJECTED"),
    }

    provider_registry = {
        "status": "PASS",
        "provider_count": len(PROVIDER_CONTRACTS),
        "providers": PROVIDER_CONTRACTS,
        "network_call_allowed_by_default": False,
        "credential_handling": "blocked_until_explicit_secure_configuration",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    adapter_result = {
        "status": "PASS",
        "phase": "External Evidence Adapter and Trust Gate",
        "query": query,
        "retrieved_at": retrieved_at,
        "provider_mode": "mock_only",
        "network_call_performed": False,
        "candidates": candidates,
        "counts": counts,
        "policy": [
            "External providers discover candidate evidence only.",
            "Aggregators are not truth sources by default.",
            "Primary source is preferred for committed evidence.",
            "Citation support and supporting excerpt are required.",
            "Human review is required for secondary/aggregated sources.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    citation_gate = {
        "status": "PASS",
        **counts,
        "gate_policy": "candidate_to_committed_requires_trust_and_citation_support",
        "gate_distribution": {
            "COMMITTED_EVIDENCE": counts["committed_count"],
            "EVIDENCE_CANDIDATE": counts["evidence_candidate_count"],
            "HUMAN_REVIEW_REQUIRED": counts["human_review_count"],
            "REJECTED": counts["rejected_count"],
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    common_register = {
        "status": "PASS",
        "future_phase": "PROD-601..620 Common Workload Mass Test Lab",
        "workload_families": COMMON_WORKLOADS,
        "solver_api_target": {
            "POST /api/casulo/solver/input": "single input routed through Cubo solver",
            "POST /api/casulo/solver/batch": "batch/mass testing for common workloads",
            "GET /api/casulo/solver/run/{run_id}": "run state",
            "GET /api/casulo/solver/evidence/{run_id}": "evidence trace",
            "GET /api/casulo/solver/gates/{run_id}": "gate decisions",
            "GET /api/casulo/solver/report/{run_id}": "final report",
        },
        "mass_test_goal": "test routine workloads before and alongside business-domain mass tests",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod521_560_provider_registry.json", provider_registry)
    write_json(out / "prod521_560_external_evidence_candidates.json", adapter_result)
    write_json(out / "prod521_560_citation_gate_result.json", citation_gate)
    write_json(out / "prod521_560_common_workload_mass_test_register.json", common_register)

    report = [
        "# PROD-521..560 External Evidence Adapter and Trust Gate",
        "",
        f"- Status: `{adapter_result['status']}`",
        f"- Provider mode: `{adapter_result['provider_mode']}`",
        f"- Network call performed: `{adapter_result['network_call_performed']}`",
        f"- Candidate count: `{counts['candidate_count']}`",
        f"- Committed evidence: `{counts['committed_count']}`",
        f"- Evidence candidates: `{counts['evidence_candidate_count']}`",
        f"- Human review required: `{counts['human_review_count']}`",
        f"- Rejected: `{counts['rejected_count']}`",
        "",
        "## Candidates",
    ]
    for c in candidates:
        report.append(f"- `{c['evidence_id']}` `{c['source_type']}` trust `{c['trust_level']}` -> `{c['gate']}` / `{c['gate_reason']}`")
    report += ["", "## Common Workload Mass Test Register", "Future phase: `PROD-601..620 Common Workload Mass Test Lab`"]
    for workload in COMMON_WORKLOADS:
        report.append(f"- `{workload}`")
    write_text(out / "prod521_560_external_evidence_adapter_report.md", "\n".join(report) + "\n")
    return adapter_result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--query", default="CASULO external evidence adapter trust gate")
    args = parser.parse_args()
    result = build(Path(args.repo), args.query)
    print(json.dumps({
        "status": result["status"],
        "provider_mode": result["provider_mode"],
        "network_call_performed": result["network_call_performed"],
        "counts": result["counts"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
