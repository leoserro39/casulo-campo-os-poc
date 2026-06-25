#!/usr/bin/env python3
import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "05_outputs" / "rag" / "chunks.jsonl"
GRAPH = ROOT / "05_outputs" / "graph" / "graph.json"
OUT = ROOT / "05_outputs" / "deltas"

EXPECTED = {
    "atendimento": ["whatsapp", "cliente", "resposta", "tempo", "roteiro", "confirmacao", "resolvido", "metrica", "evidencia"],
    "vendas": ["pedido", "confirmacao", "cliente", "venda", "perdido", "aberto", "metrica", "evidencia"],
    "operacao": ["processo", "rotina", "estoque", "prazo", "responsavel", "metrica", "evidencia"],
    "financeiro": ["receita", "custo", "caixa", "pagamento", "controle", "metrica", "evidencia"],
    "marketing": ["conteudo", "canal", "campanha", "cliente", "conversao", "metrica", "evidencia"],
    "gestao": ["decisao", "prioridade", "responsavel", "rotina", "acompanhamento", "metrica", "evidencia"],
    "tecnologia": ["sistema", "automacao", "dados", "integracao", "ferramenta", "metrica", "evidencia"],
    "impacto": ["resultado", "antes", "depois", "indicador", "beneficio", "metrica", "evidencia"],
}

def norm(value):
    value = unicodedata.normalize("NFKD", (value or "").lower())
    return "".join(ch for ch in value if not unicodedata.combining(ch))

def words(value):
    return [w for w in re.findall(r"[a-z0-9_]+", norm(value)) if len(w) >= 3]

def slug(value):
    return "_".join(words(value)[:8]) or "mesh_delta"

def clamp(value):
    return max(0.0, min(1.0, value))

def read_chunks():
    if not CHUNKS.exists():
        return []
    rows = []
    for line in CHUNKS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows

def read_graph():
    if not GRAPH.exists():
        return {"nodes": [], "relationships": []}
    return json.loads(GRAPH.read_text(encoding="utf-8"))

def score_chunk(query_terms, chunk):
    hay = norm(" ".join([
        chunk.get("text", ""),
        chunk.get("source_path", ""),
        chunk.get("domain") or "",
        chunk.get("case_id") or "",
        chunk.get("allowed_use") or "",
    ]))
    return sum(1 for term in query_terms if term in hay)

def select_chunks(question, limit=7):
    query_terms = words(question)
    scored = []
    for chunk in read_chunks():
        score = score_chunk(query_terms, chunk)
        if score:
            scored.append((score, chunk))
    scored.sort(key=lambda item: (-item[0], item[1].get("source_path", "")))
    return [chunk for _, chunk in scored[:limit]]

def infer_domain(question, chunks):
    q = norm(question)
    for domain in EXPECTED:
        if domain in q:
            return domain
    if "whatsapp" in q or "resposta" in q or "cliente" in q:
        return "atendimento"
    if "pedido" in q or "venda" in q:
        return "vendas"
    for chunk in chunks:
        if chunk.get("domain"):
            return chunk["domain"]
    return "gestao"

def compute(question):
    chunks = select_chunks(question)
    graph = read_graph()
    domain = infer_domain(question, chunks)
    expected = EXPECTED.get(domain, EXPECTED["gestao"])

    text = norm(" ".join(c.get("text", "") for c in chunks))
    qwords = set(words(question))
    common = sorted([x for x in expected if x in text or x in qwords])
    missing = sorted([x for x in expected if x not in common])

    support_ratio = len(common) / max(1, len(expected))
    missing_ratio = len(missing) / max(1, len(expected))
    source_ratio = min(1.0, len(chunks) / 5.0)

    delta_l = clamp(0.10 + 0.50 * missing_ratio + 0.25 * (1.0 - source_ratio) + 0.15 * (1.0 - support_ratio))
    h_pre = clamp(0.15 + 0.55 * missing_ratio + 0.25 * (1.0 - source_ratio) - 0.10 * support_ratio)

    if delta_l <= 0.45 and h_pre <= 0.55:
        gate = "ALLOW_PROPOSAL"
        next_action = "Generate or review a controlled proposal."
    elif delta_l <= 0.70:
        gate = "PREPARE_OR_REDUCE_SCOPE"
        next_action = "Ask for missing evidence or reduce the proposed scope."
    else:
        gate = "BLOCK_STRONG_MANIFESTATION"
        next_action = "Do not generate a strong solution before collecting evidence."

    chars = sum(len(c.get("text", "")) for c in chunks)

    return {
        "status": "COMPUTED",
        "question": question,
        "inferred_domain": domain,
        "graph_nodes": len(graph.get("nodes", [])),
        "graph_relationships": len(graph.get("relationships", [])),
        "chunks_used": len(chunks),
        "estimated_tokens": chars // 4,
        "sources": [c.get("source_path", "unknown") for c in chunks],
        "expected_dimensions": expected,
        "common_dimensions": common,
        "missing_dimensions": missing,
        "support_ratio": round(support_ratio, 3),
        "missing_ratio": round(missing_ratio, 3),
        "Delta_L": round(delta_l, 3),
        "H_pre": round(h_pre, 3),
        "gate": gate,
        "next_action": next_action,
    }

def write_outputs(result):
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    base = "mesh_delta_%s_%s" % (slug(result["question"]), stamp)
    md = OUT / (base + ".md")
    js = OUT / (base + ".json")

    js.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS Mesh Delta",
        "",
        "- status: %s" % result["status"],
        "- question: %s" % result["question"],
        "- inferred_domain: %s" % result["inferred_domain"],
        "- graph_nodes: %s" % result["graph_nodes"],
        "- graph_relationships: %s" % result["graph_relationships"],
        "- chunks_used: %s" % result["chunks_used"],
        "- estimated_tokens: %s" % result["estimated_tokens"],
        "- support_ratio: %s" % result["support_ratio"],
        "- missing_ratio: %s" % result["missing_ratio"],
        "- Delta_L: %s" % result["Delta_L"],
        "- H_pre: %s" % result["H_pre"],
        "- gate: %s" % result["gate"],
        "",
        "## Sources",
    ]
    lines.extend(["- " + s for s in result["sources"]] or ["- no matched source"])
    lines.append("")
    lines.append("## Common dimensions")
    lines.extend(["- " + x for x in result["common_dimensions"]] or ["- none"])
    lines.append("")
    lines.append("## Missing dimensions")
    lines.extend(["- " + x for x in result["missing_dimensions"]] or ["- none"])
    lines.append("")
    lines.append("## Next action")
    lines.append("- " + result["next_action"])
    lines.append("")

    md.write_text("\n".join(lines), encoding="utf-8")

    print("MESH_DELTA_CREATED")
    print("delta:", md.relative_to(ROOT))
    print("trace:", js.relative_to(ROOT))
    print("domain:", result["inferred_domain"])
    print("Delta_L:", result["Delta_L"])
    print("H_pre:", result["H_pre"])
    print("gate:", result["gate"])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", required=True)
    args = parser.parse_args()
    write_outputs(compute(args.ask))

if __name__ == "__main__":
    main()
