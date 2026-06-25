#!/usr/bin/env python3
import argparse
import json
import unicodedata
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / '05_outputs' / 'graph' / 'graph.json'
RAG = ROOT / '05_outputs' / 'rag' / 'chunks.jsonl'

LAST = {'query': None, 'matched_chunks': 0, 'chars_read': 0, 'estimated_tokens': 0, 'sources': []}


def ensure_indexes():
    missing = []
    if not GRAPH.exists():
        missing.append('graph')
    if not RAG.exists():
        missing.append('rag')
    if missing:
        print('Aviso: indices derivados ausentes:', ', '.join(missing))
        print('Rode: python 04_scripts/export_graph.py && python 04_scripts/build_rag_index.py')


def load_graph():
    if not GRAPH.exists():
        return {'nodes': [], 'relationships': []}
    return json.loads(GRAPH.read_text(encoding='utf-8'))


def load_chunks():
    if not RAG.exists():
        return []
    out = []
    for line in RAG.read_text(encoding='utf-8').splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def tokens_estimate(chars):
    return max(1, round(chars / 4))


def search_chunks(query, limit=5):
    chunks = load_chunks()
    terms = [t.lower() for t in re.findall(r'[a-zA-Z0-9_À-ÿ]+', query) if len(t) >= 3]
    scored = []
    for ch in chunks:
        text = ch.get('text', '')
        low = text.lower() + ' ' + str(ch.get('domain') or '') + ' ' + str(ch.get('case_id') or '')
        score = sum(low.count(t) for t in terms)
        if score:
            scored.append((score, ch))
    scored.sort(key=lambda x: (-x[0], x[1].get('source_path','')))
    result = [ch for _, ch in scored[:limit]]
    chars = sum(len(ch.get('text','')) for ch in result)
    LAST.update({
        'query': query,
        'matched_chunks': len(result),
        'chars_read': chars,
        'estimated_tokens': tokens_estimate(chars),
        'sources': [ch.get('source_path') for ch in result]
    })
    return result


def summarize_state():
    graph = load_graph()
    nodes = graph.get('nodes', [])
    rels = graph.get('relationships', [])
    by_label = {}
    for n in nodes:
        by_label[n.get('label','Unknown')] = by_label.get(n.get('label','Unknown'), 0) + 1
    return [
        'Estado operacional da malha:',
        f'- nos: {len(nodes)}',
        f'- relacoes: {len(rels)}',
        '- por tipo: ' + ', '.join(f'{k}={v}' for k, v in sorted(by_label.items())),
        '- fonte da verdade: arquivos Git/Markdown/JSON',
        '- grafo/RAG: projecoes derivadas',
    ]


def list_problems():
    graph = load_graph()
    problems = [n for n in graph.get('nodes', []) if n.get('label') == 'Problem']
    if not problems:
        return ['Nenhum problema encontrado no grafo.']
    lines = ['Problemas encontrados:']
    for n in problems[:20]:
        lines.append(f'- {n.get("name")} | dominio={n.get("domain")} | fonte={n.get("source_path")}')
    return lines


def list_solutions():
    graph = load_graph()
    sols = [n for n in graph.get('nodes', []) if n.get('label') == 'Solution']
    if not sols:
        return ['Nenhuma solucao encontrada no grafo.']
    lines = ['Solucoes encontradas:']
    for n in sols:
        lines.append(f'- {n.get("name")} | case={n.get("case_id")} | fonte={n.get("source_path")}')
    return lines


def graph_info():
    graph = load_graph()
    return [
        'Grafo derivado:',
        f'- arquivo: {GRAPH.relative_to(ROOT) if GRAPH.exists() else "ausente"}',
        f'- gerado_em: {graph.get("generated_at_utc")}',
        f'- nodes.csv: 05_outputs/graph/nodes.csv',
        f'- relationships.csv: 05_outputs/graph/relationships.csv',
    ]


def propose_next_action(query):
    hits = search_chunks(query, limit=5)
    if not hits:
        return ['Nao encontrei base suficiente. Proposta segura: criar questions.md ou pedir mais evidencia.']
    sources = ', '.join(sorted(set(ch.get('source_path') for ch in hits)))
    return [
        'Proposta controlada:',
        '- nao alterar estado canonico automaticamente;',
        '- gerar/atualizar solution_packet.md somente apos revisao;',
        '- manter return_delta.json como proposto ate medir resultado;',
        f'- fontes consultadas: {sources}',
        '- proxima micro-acao sugerida: validar uma dor prioritaria e uma metrica antes/depois.'
    ]


def answer(query):
    q = query.lower().strip()
    if q in {'estado','status','malha'} or 'estado operacional' in q:
        return summarize_state()
    if 'problema' in q or q == 'problemas':
        return list_problems()
    if 'solucao' in q or 'solução' in q or q == 'solucoes':
        return list_solutions()
    if 'grafo' in q or 'graph' in q or 'neo4j' in q:
        return graph_info()
    if 'consumo' in q or 'tokens' in q:
        return [
            'Ultimo consumo estimado:',
            f'- pergunta: {LAST.get("query")}',
            f'- chunks usados: {LAST.get("matched_chunks")}',
            f'- caracteres lidos: {LAST.get("chars_read")}',
            f'- tokens estimados: {LAST.get("estimated_tokens")}',
            '- fontes: ' + (', '.join(LAST.get('sources') or []) or 'nenhuma')
        ]
    return propose_next_action(query)


def normalize_query(value):
    value = value.strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return value


def main():
    parser = argparse.ArgumentParser(description='Chat local deterministico da malha CASULO Campo OS.')
    parser.add_argument('--ask', help='Pergunta unica para o chat local')
    args = parser.parse_args()
    ensure_indexes()
    if args.ask:
        for line in answer(args.ask):
            print(line)
        return
    print('CASULO Campo OS Chat local')
    print('Digite: estado, problemas, solucoes, grafo, consumo, ou sair')
    while True:
        try:
            q = normalize_query(input('casulo> '))
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in {'sair','exit','quit'}:
            break
        for line in answer(q):
            print(line)
        print('')

if __name__ == '__main__':
    main()
