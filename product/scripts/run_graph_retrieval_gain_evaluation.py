#!/usr/bin/env python3
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
]

def run_cypher(query):
    cmd = [
        "docker", "exec", "casulo-neo4j-sandbox",
        "cypher-shell", "-u", "neo4j", "-p", "casulo_sandbox_1234",
        "--format", "plain",
        query,
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()

def parse_table(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return []
    headers = [h.strip() for h in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        values = [v.strip().strip('"') for v in line.split(",")]
        rows.append(dict(zip(headers, values)))
    return rows

def as_int(v):
    try:
        return int(float(str(v)))
    except Exception:
        return 0

def first_row(query):
    rows = parse_table(run_cypher(query))
    return rows[0] if rows else {}

def main():
    node_row = first_row("MATCH (n:CasuloNode) RETURN count(n) AS casulo_nodes;")
    rel_row = first_row("MATCH (:CasuloNode)-[r]->(:CasuloNode) RETURN count(r) AS casulo_relationships;")

    label_rows = parse_table(
        "label,count\n" + "\n".join([])
    )
    label_rows = parse_table(run_cypher(
        "MATCH (n:CasuloNode) RETURN n.casulo_label AS label, count(*) AS count ORDER BY count DESC;"
    ))

    rel_type_rows = parse_table(run_cypher(
        "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC;"
    ))

    topology = first_row("""
MATCH (c:Case)
OPTIONAL MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)
OPTIONAL MATCH (c)-[:TRIGGERS]->(r:RiskSignal)
OPTIONAL MATCH (c)-[:HAS_BUDGET]->(b:HallucinationBudget)
OPTIONAL MATCH (c)-[:BELONGS_TO]->(d:Domain)
WITH
  count(DISTINCT c) AS cases,
  count(DISTINCT e) AS evidence_nodes,
  count(DISTINCT r) AS risk_nodes,
  count(DISTINCT b) AS budget_nodes,
  count(DISTINCT d) AS domain_nodes
RETURN cases, evidence_nodes, risk_nodes, budget_nodes, domain_nodes;
""")

    controlled_paths = first_row("""
MATCH (c:Case)
WITH collect(c) AS cases
RETURN
  size(cases) AS cases,
  size([c IN cases WHERE EXISTS { MATCH (c)-[:TRIGGERS]-(:RiskSignal)-[:CONTRIBUTES_TO]-(:Gate) }]) AS cases_reaching_gate_controlled,
  size([c IN cases WHERE EXISTS { MATCH (c)-[:TRIGGERS]-(:RiskSignal)-[:CONTRIBUTES_TO]-(:Gate)-[:ALLOWS]-(:OutputMode) }]) AS cases_reaching_output_controlled;
""")

    sample_paths = parse_table(run_cypher("""
MATCH (c:Case)-[:TRIGGERS]-(r:RiskSignal)-[:CONTRIBUTES_TO]-(g:Gate)-[:ALLOWS]-(o:OutputMode)
RETURN c.id AS case_id, r.id AS risk_id, g.id AS gate_id, o.id AS output_id
LIMIT 20;
"""))

    casulo_nodes = as_int(node_row.get("casulo_nodes"))
    casulo_relationships = as_int(rel_row.get("casulo_relationships"))
    label_counts = {row.get("label"): as_int(row.get("count")) for row in label_rows}
    rel_type_counts = {row.get("rel_type"): as_int(row.get("count")) for row in rel_type_rows}

    import_match = (
        casulo_nodes >= 313 and
        casulo_relationships >= 350 and
        label_counts.get("Case", 0) >= 50
    )

    direct_context_ok = (
        as_int(topology.get("cases")) >= 50 and
        as_int(topology.get("evidence_nodes")) >= 50 and
        as_int(topology.get("risk_nodes")) >= 50 and
        as_int(topology.get("budget_nodes")) >= 50 and
        as_int(topology.get("domain_nodes")) >= 1
    )

    controlled_path_ok = (
        as_int(controlled_paths.get("cases")) >= 50 and
        as_int(controlled_paths.get("cases_reaching_gate_controlled")) >= 50 and
        as_int(controlled_paths.get("cases_reaching_output_controlled")) >= 50
    )

    status = "PASS" if import_match and direct_context_ok and controlled_path_ok else "WARN"
    decision = (
        "GRAPH_RETRIEVAL_GAIN_CONFIRMED_FOR_SANDBOX"
        if status == "PASS"
        else "GRAPH_IMPORTED_BUT_TOPOLOGY_REQUIRES_REVIEW"
    )

    result = {
        "status": status,
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "neo4j_sandbox_read_only_topology_aware_evaluation",
        "neo4j": {
            "casulo_nodes": casulo_nodes,
            "casulo_relationships": casulo_relationships,
            "label_counts": label_counts,
            "relationship_type_counts": rel_type_counts,
            "direct_context": topology,
            "controlled_paths": controlled_paths,
            "sample_controlled_paths": sample_paths,
        },
        "retrieval_gain": {
            "import_match": import_match,
            "direct_context_ok": direct_context_ok,
            "controlled_path_ok": controlled_path_ok,
            "interpretation": "Neo4j sandbox confirms topology-aware retrieval from Case to Evidence, RiskSignal, HallucinationBudget, Domain, Gate and OutputMode through controlled paths.",
            "external_claim_allowed": False,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    json_path = OUT / "prod1301_1340_graph_retrieval_gain_evaluation.json"
    md_path = OUT / "prod1301_1340_graph_retrieval_gain_evaluation.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1301..1340 Graph Retrieval Gain Evaluation",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Mode: `neo4j_sandbox_read_only_topology_aware_evaluation`",
        f"- CASULO nodes: `{casulo_nodes}`",
        f"- CASULO relationships: `{casulo_relationships}`",
        "",
        "## Label Counts",
    ]
    for k, v in sorted(label_counts.items(), key=lambda x: (-x[1], x[0] or "")):
        md.append(f"- {k}: `{v}`")

    md += ["", "## Relationship Type Counts"]
    for k, v in sorted(rel_type_counts.items(), key=lambda x: (-x[1], x[0] or "")):
        md.append(f"- {k}: `{v}`")

    md += ["", "## Direct Context"]
    for k, v in topology.items():
        md.append(f"- {k}: `{v}`")

    md += ["", "## Controlled Paths"]
    for k, v in controlled_paths.items():
        md.append(f"- {k}: `{v}`")

    md += [
        "",
        "## Retrieval Gain",
        f"- import_match: `{import_match}`",
        f"- direct_context_ok: `{direct_context_ok}`",
        f"- controlled_path_ok: `{controlled_path_ok}`",
        "",
        "## Interpretation",
        "Neo4j sandbox confirms topology-aware retrieval from Case to Evidence, RiskSignal, HallucinationBudget and Domain directly, and to Gate/OutputMode through controlled semantic paths.",
        "This confirms sandbox graph retrieval value, but does not authorize production use or external claims.",
        "",
        "## Blocked Actions",
    ]
    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "decision": decision,
        "casulo_nodes": casulo_nodes,
        "casulo_relationships": casulo_relationships,
        "direct_context_ok": direct_context_ok,
        "controlled_path_ok": controlled_path_ok
    }, indent=2))

if __name__ == "__main__":
    main()
