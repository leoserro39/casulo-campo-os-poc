#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable

def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items

def cypher_string(value: Any) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)

def safe_label(value: Any) -> str:
    raw = str(value or "CasuloNode")
    raw = re.sub(r"[^A-Za-z0-9_]", "_", raw)
    if not raw or raw[0].isdigit():
        raw = "N_" + raw
    return raw[:80]

def safe_rel(value: Any) -> str:
    raw = str(value or "RELATED_TO")
    raw = re.sub(r"[^A-Za-z0-9_]", "_", raw).upper()
    if not raw or raw[0].isdigit():
        raw = "R_" + raw
    return raw[:80]

def pick(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return default

def props_from(obj: Dict[str, Any]) -> Dict[str, Any]:
    props = obj.get("properties")
    if isinstance(props, dict):
        return props
    return {k: v for k, v in obj.items() if k not in {"id", "label", "type", "from", "to", "source", "target", "start", "end", "start_id", "end_id"}}

def cypher_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)

def cypher_map(props: Dict[str, Any]) -> str:
    pairs = []
    for k, v in props.items():
        key = re.sub(r"[^A-Za-z0-9_]", "_", str(k))
        if not key or key[0].isdigit():
            key = "p_" + key
        if not isinstance(v, (str, int, float, bool)) and v is not None:
            v = json.dumps(v, ensure_ascii=False)
        pairs.append(f"{key}: {cypher_value(v)}")
    return "{" + ", ".join(pairs) + "}"

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--nodes", default="outputs/prod941_980_graph_export_nodes.jsonl")
    parser.add_argument("--relationships", default="outputs/prod941_980_graph_export_relationships.jsonl")
    parser.add_argument("--out", default="outputs/prod1261_1300_neo4j_sandbox_import_preview.cypher")
    args = parser.parse_args()

    repo = Path(args.repo)
    nodes_path = repo / args.nodes
    rels_path = repo / args.relationships
    out_path = repo / args.out

    nodes = list(load_jsonl(nodes_path))
    rels = list(load_jsonl(rels_path))

    lines = [
        "// CASULO Neo4j sandbox import preview",
        "// Generated offline. Review before execution.",
        "// Sandbox only. Do not run against production.",
        "CREATE CONSTRAINT casulo_node_id IF NOT EXISTS FOR (n:CasuloNode) REQUIRE n.id IS UNIQUE;",
        ""
    ]

    for node in nodes:
        node_id = pick(node, "id", "node_id", default="")
        label = safe_label(pick(node, "label", "type", default="CasuloNode"))
        props = props_from(node)
        props["casulo_label"] = label
        lines.append(f"MERGE (n:CasuloNode {{id: {cypher_string(node_id)}}})")
        lines.append(f"SET n:{label}, n += {cypher_map(props)};")
        lines.append("")

    for rel in rels:
        start = pick(rel, "from", "source", "start", "start_id", default="")
        end = pick(rel, "to", "target", "end", "end_id", default="")
        rel_type = safe_rel(pick(rel, "type", "label", default="RELATED_TO"))
        props = props_from(rel)
        props["casulo_rel_type"] = rel_type
        lines.append(f"MATCH (a:CasuloNode {{id: {cypher_string(start)}}}), (b:CasuloNode {{id: {cypher_string(end)}}})")
        lines.append(f"MERGE (a)-[r:{rel_type}]->(b)")
        lines.append(f"SET r += {cypher_map(props)};")
        lines.append("")

    lines += [
        "// Verification queries",
        "MATCH (n:CasuloNode) RETURN count(n) AS casulo_nodes;",
        "MATCH (:CasuloNode)-[r]->(:CasuloNode) RETURN count(r) AS casulo_relationships;",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "nodes_seen": len(nodes),
        "relationships_seen": len(rels),
        "cypher_file": str(out_path),
        "will_execute_now": False,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
