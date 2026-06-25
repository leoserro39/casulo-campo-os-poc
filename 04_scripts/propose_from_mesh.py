#!/usr/bin/env python3
import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "05_outputs/rag/chunks.jsonl"
GRAPH = ROOT / "05_outputs/graph/graph.json"
OUT = ROOT / "05_outputs/proposals"

def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))

def terms(s):
    return [w for w in re.findall(r"[a-z0-9_]+", norm(s)) if len(w) >= 3]

def slug(s):
    x = "_".join(terms(s)[:8])
    return x or "proposal"

def read_chunks():
    rows = []
    if not CHUNKS.exists():
        return rows
    for line in CHUNKS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows

def read_graph():
    if not GRAPH.exists():
        return {"nodes": [], "relationships": []}
    return json.loads(GRAPH.read_text(encoding="utf-8"))

def select(question, limit=5):
    qterms = terms(question)
    scored = []
    for c in read_chunks():
        hay = norm(" ".join([
            c.get("text", ""),
            c.get("source_path", ""),
            c.get("domain") or "",
            c.get("case_id") or "",
            c.get("allowed_use") or "",
        ]))
        score = sum(1 for t in qterms if t in hay)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1].get("source_path", "")))
    return [c for _, c in scored[:limit]]

def infer_domain(question, chunks):
    q = norm(question)
    if "whatsapp" in q or "atendimento" in q or "resposta" in q:
        return "atendimento"
    if "venda" in q or "pedido" in q:
        return "vendas"
    if chunks and chunks[0].get("domain"):
        return chunks[0]["domain"]
    return "gestao"

def proposal_items(domain):
    if domain == "atendimento":
        return [
            "Criar roteiro minimo de atendimento WhatsApp com respostas base.",
            "Separar mensagens em: novo contato, aguardando confirmacao e resolvido.",
            "Medir tempo de primeira resposta ou mensagens sem resposta por dia.",
            "Rodar por 7 dias antes de promover mudanca para estado canonico.",
        ]
    if domain == "vendas":
        return [
            "Criar fluxo simples de confirmacao de pedido.",
            "Registrar pedido aberto, confirmado e perdido.",
            "Medir pedidos sem confirmacao antes/depois.",
            "Validar com humano antes de virar rotina oficial.",
        ]
    return [
        "Selecionar uma dor prioritaria.",
        "Coletar evidencia minima.",
        "Criar micro-acao de 7 dias.",
        "Manter status PROPOSED ate revisao humana.",
    ]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", required=True)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    chunks = select(args.ask)
    graph = read_graph()
    domain = infer_domain(args.ask, chunks)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    base = f"proposal_{slug(args.ask)}_{stamp}"
    md = OUT / f"{base}.md"
    js = OUT / f"{base}.json"

    chars = sum(len(c.get("text", "")) for c in chunks)
    tokens = chars // 4
    sources = [c.get("source_path", "unknown") for c in chunks]

    lines = [
        "# CASULO Campo OS Proposal",
        "",
        "- status: PROPOSED",
        f"- generated_utc: {stamp}",
        f"- question: {args.ask}",
        f"- inferred_domain: {domain}",
        f"- graph_nodes: {len(graph.get('nodes', []))}",
        f"- graph_relationships: {len(graph.get('relationships', []))}",
        f"- chunks_used: {len(chunks)}",
        f"- estimated_tokens: {tokens}",
        "",
        "## Sources",
    ]
    lines += [f"- {s}" for s in sources] or ["- no matched source"]
    lines += ["", "## Controlled proposal"]
    lines += [f"- {x}" for x in proposal_items(domain)]
    lines += [
        "",
        "## Gates",
        "- do not change canonical state automatically",
        "- require human review before updating solution_packet.md",
        "- require measured evidence before promoting return_delta.json",
        "",
        "## Suggested next action",
        "- Review and decide: approve, adjust, reject, or ask for more evidence.",
        "",
    ]

    md.write_text("\n".join(lines), encoding="utf-8")
    js.write_text(json.dumps({
        "status": "PROPOSED",
        "generated_utc": stamp,
        "question": args.ask,
        "inferred_domain": domain,
        "sources": sources,
        "chunks_used": len(chunks),
        "estimated_tokens": tokens,
        "proposal_md": str(md.relative_to(ROOT)),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("PROPOSAL_CREATED")
    print("proposal:", md.relative_to(ROOT))
    print("trace:", js.relative_to(ROOT))
    print("domain:", domain)
    print("chunks_used:", len(chunks))
    print("estimated_tokens:", tokens)

if __name__ == "__main__":
    main()
