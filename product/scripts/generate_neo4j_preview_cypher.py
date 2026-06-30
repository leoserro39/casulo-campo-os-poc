#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

def q(value):
    return json.dumps(str(value), ensure_ascii=False)

def safe_type(value):
    s = str(value or "RELATED_TO")
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in s).upper()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--out", default="outputs/prod1261_1300_preview_import.cypher")
    args = parser.parse_args()
    repo = Path(args.repo)
    nodes = repo / "outputs/prod941_980_graph_export_nodes.jsonl"
    rels = repo / "outputs/prod941_980_graph_export_relationships.jsonl"
    lines = [
        "// CASULO Neo4j sandbox preview import",
        "// Generated offline. Review before execution.",
        "CREATE CONSTRAINT casulo_node_id IF NOT EXISTS FOR (n:CasuloNode) REQUIRE n.id IS UNIQUE;"
    ]
    if nodes.exists():
        for line in nodes.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            node_id = obj.get("id")
            label = safe_type(obj.get("label", "CasuloNode"))
            props = obj.get("properties", {})
            lines.append(f"MERGE (n:CasuloNode {{id: {q(node_id)}}}) SET n:{label}, n += {json.dumps(props, ensure_ascii=False)};")
    if rels.exists():
        for line in rels.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            rel_type = safe_type(obj.get("type", "RELATED_TO"))
            start = obj.get("from")
            end = obj.get("to")
            props = obj.get("properties", {})
            lines.append(f"MATCH (a:CasuloNode {{id: {q(start)}}}), (b:CasuloNode {{id: {q(end)}}}) MERGE (a)-[r:{rel_type}]->(b) SET r += {json.dumps(props, ensure_ascii=False)};")
    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
