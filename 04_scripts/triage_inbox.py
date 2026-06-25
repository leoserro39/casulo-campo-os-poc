#!/usr/bin/env python3
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / '00_inbox' / 'raw_docs'
OUT = ROOT / '05_outputs' / 'triage' / 'triage_manifest.json'
DOMAINS = {
    'atendimento': ['whatsapp','mensagem','cliente','resposta','atendimento','pos-venda','pergunta'],
    'vendas': ['venda','pedido','encomenda','proposta','cliente','confirmado','faturamento'],
    'operacao': ['estoque','producao','rotina','entrega','processo','caixa','caderno'],
    'financeiro': ['caixa','cobranca','margem','inadimplencia','pagamento','custo'],
    'marketing': ['conteudo','campanha','instagram','rede social','vitrine','divulgacao'],
    'gestao': ['dono','responsavel','prioridade','decisao','agenda','equipe'],
    'tecnologia': ['sistema','planilha','automacao','ia','software','dados'],
    'impacto': ['resultado','metrica','antes','depois','impacto','indicador'],
}

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or 'item'

def score_domain(text):
    low = text.lower()
    scores = {}
    for dom, keys in DOMAINS.items():
        scores[dom] = sum(low.count(k) for k in keys)
    best = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = round(min(0.95, max(0.25, scores[best] / total)), 2)
    if scores[best] == 0:
        best = 'gestao'
        confidence = 0.25
    return best, confidence, scores

def infer_problem(text, domain):
    low = text.lower()
    if domain == 'atendimento' and ('demora' in low or 'sem resposta' in low or 'whatsapp' in low):
        return 'demora_resposta_whatsapp'
    if domain == 'vendas' and ('pedido' in low or 'encomenda' in low):
        return 'pedidos_sem_confirmacao'
    if domain == 'operacao' and ('caderno' in low or 'rotina' in low):
        return 'rotina_operacional_fragmentada'
    return f'problema_{domain}_a_validar'

manifest = {
    'manifest_id': 'triage_manifest_demo_001',
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'source_dir': str(INBOX.relative_to(ROOT)),
    'rules': {
        'create_domains_automatically': False,
        'allowed_domains': list(DOMAINS.keys()),
        'do_not_delete_or_move_originals': True,
    },
    'items': []
}

for p in sorted(INBOX.glob('*')):
    if not p.is_file():
        continue
    text = p.read_text(encoding='utf-8', errors='replace')
    dom, confidence, scores = score_domain(text)
    problem = infer_problem(text, dom)
    manifest['items'].append({
        'source_path': str(p.relative_to(ROOT)),
        'proposed_domain': dom,
        'problem_id': problem,
        'record_slug': slugify(problem),
        'evidence_level': 'raw',
        'confidence': confidence,
        'domain_scores': scores,
        'action': 'create_problem_record',
        'summary': 'Triagem automatica por palavras-chave para POC repo-as-mesh.'
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'TRIAGE_MANIFEST_CREATED: {OUT.relative_to(ROOT)}')
print(f'items: {len(manifest["items"])}')
