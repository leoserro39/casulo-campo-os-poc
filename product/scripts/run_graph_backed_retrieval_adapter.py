#!/usr/bin/env python3
import argparse
import csv
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"

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
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation",
    "codex_execution"
]

def run_cypher(query):
    cmd = [
        "docker", "exec", "casulo-neo4j-sandbox",
        "cypher-shell", "-u", "neo4j", "-p", "casulo_sandbox_1234",
        "--format", "plain",
        query
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()

def parse_plain_csv(text):
    if not text.strip():
        return []
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        clean = {}
        for k, v in row.items():
            key = (k or "").strip().strip('"')
            value = (v or "").strip().strip('"')
            clean[key] = value
        rows.append(clean)
    return rows

def contains_terms(row, terms):
    if not terms:
        return True
    haystack = json.dumps(row, ensure_ascii=False).lower()
    return all(term.lower() in haystack for term in terms)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="missing evidence", help="Human query or operational intent.")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    query = args.query.strip()
    terms = [t for t in query.replace("_", " ").replace("-", " ").split() if len(t) > 2]

    cypher = """
MATCH (c:Case)
OPTIONAL MATCH (c)-[:BELONGS_TO]-(d:Domain)
OPTIONAL MATCH (c)-[:HAS_EVIDENCE]-(e:Evidence)
OPTIONAL MATCH (c)-[:TRIGGERS]-(r:RiskSignal)
OPTIONAL MATCH (c)-[:HAS_BUDGET]-(b:HallucinationBudget)
OPTIONAL MATCH (c)-[:TRIGGERS]-(r2:RiskSignal)-[:CONTRIBUTES_TO]-(g:Gate)-[:ALLOWS]-(o:OutputMode)
OPTIONAL MATCH (c)-[:REQUIRES]-(ready:ReadinessState)
RETURN
  c.id AS case_id,
  c.business_domain AS business_domain,
  c.risk_theme AS risk_theme,
  c.evidence_profile AS evidence_profile,
  d.id AS domain_id,
  e.id AS evidence_id,
  r.id AS risk_id,
  r.risk_band AS risk_band,
  r.adjusted_risk AS adjusted_risk,
  g.id AS gate_id,
  g.gate AS gate,
  o.id AS output_id,
  o.output_mode AS output_mode,
  b.id AS budget_id,
  b.hallucination_budget AS hallucination_budget,
  b.reasoning_mode AS reasoning_mode,
  ready.id AS readiness_id
ORDER BY c.id
LIMIT 500;
"""

    rows = parse_plain_csv(run_cypher(cypher))
    matched = [row for row in rows if contains_terms(row, terms)]
    if not matched:
        matched = rows[:args.limit]
        match_mode = "fallback_first_cases_no_exact_term_match"
    else:
        matched = matched[:args.limit]
        match_mode = "term_filtered"

    packet = {
        "status": "PASS",
        "query": query,
        "mode": "neo4j_sandbox_read_only_context_packet",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "context_packet": {
            "match_mode": match_mode,
            "terms": terms,
            "result_count": len(matched),
            "cases": matched,
            "retrieval_boundary": {
                "source": "Neo4j sandbox",
                "read_only": True,
                "final_answer_generation_allowed": False,
                "codex_execution_allowed": False,
                "production_connection_allowed": False
            }
        },
        "blocked_actions": BLOCKED_ACTIONS
    }

    json_path = OUT / "prod1341_1380_graph_context_packet.json"
    md_path = OUT / "prod1341_1380_graph_context_packet.md"

    json_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1341..1380 Graph-Backed Retrieval Context Packet",
        "",
        "- Status: `PASS`",
        f"- Query: `{query}`",
        "- Mode: `neo4j_sandbox_read_only_context_packet`",
        f"- Match mode: `{match_mode}`",
        f"- Result count: `{len(matched)}`",
        "",
        "## Retrieved Cases"
    ]

    for row in matched:
        md.extend([
            "",
            f"### {row.get('case_id')}",
            f"- business_domain: `{row.get('business_domain')}`",
            f"- risk_theme: `{row.get('risk_theme')}`",
            f"- evidence_profile: `{row.get('evidence_profile')}`",
            f"- risk_band: `{row.get('risk_band')}`",
            f"- adjusted_risk: `{row.get('adjusted_risk')}`",
            f"- gate: `{row.get('gate')}`",
            f"- output_mode: `{row.get('output_mode')}`",
            f"- hallucination_budget: `{row.get('hallucination_budget')}`",
            f"- reasoning_mode: `{row.get('reasoning_mode')}`"
        ])

    md.extend([
        "",
        "## Boundary",
        "- Read-only Neo4j sandbox retrieval.",
        "- No final answer generation.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No production connection.",
        "- No client-facing claim.",
        "",
        "## Blocked Actions"
    ])

    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "query": query,
        "match_mode": match_mode,
        "result_count": len(matched),
        "json_path": str(json_path),
        "md_path": str(md_path)
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
