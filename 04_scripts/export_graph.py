#!/usr/bin/env python3
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '05_outputs' / 'graph'
OUT.mkdir(parents=True, exist_ok=True)

nodes = []
rels = []
seen = set()

def add_node(node_id, label, props):
    if node_id in seen:
        return
    seen.add(node_id)
    item = {'id': node_id, 'label': label}
    item.update(props)
    nodes.append(item)

def add_rel(start, rel_type, end, props=None):
    item = {'start': start, 'type': rel_type, 'end': end}
    if props:
        item.update(props)
    rels.append(item)

# Domains
for domdir in sorted((ROOT / '01_domains').iterdir()):
    if not domdir.is_dir():
        continue
    dom = domdir.name
    add_node(f'domain:{dom}', 'Domain', {'name': dom, 'source_path': str((domdir/'DOMAIN.md').relative_to(ROOT))})
    for prob in sorted((domdir / 'problems').glob('*.md')):
        pid = f'problem:{prob.stem}'
        add_node(pid, 'Problem', {'name': prob.stem, 'domain': dom, 'source_path': str(prob.relative_to(ROOT))})
        add_rel(pid, 'PROBLEM_IN_DOMAIN', f'domain:{dom}', {'source_path': str(prob.relative_to(ROOT))})

# Cases
for case in sorted((ROOT / '02_cases').iterdir()):
    if not case.is_dir():
        continue
    cid = f'case:{case.name}'
    state_path = case / 'business_state.json'
    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding='utf-8'))
    add_node(cid, 'Case', {'case_id': case.name, 'business_name': state.get('business_name', case.name), 'source_path': str(state_path.relative_to(ROOT))})
    for dom in (state.get('domains') or {}).keys():
        add_rel(cid, 'CASE_HAS_DOMAIN', f'domain:{dom}', {'source_path': str(state_path.relative_to(ROOT))})
    problem = state.get('priority_problem')
    if problem:
        pid = f'problem:{problem}'
        add_node(pid, 'Problem', {'name': problem, 'domain': state.get('priority_domain'), 'source_path': str(state_path.relative_to(ROOT))})
        add_rel(cid, 'CASE_HAS_PROBLEM', pid, {'source_path': str(state_path.relative_to(ROOT))})
        if state.get('priority_domain'):
            add_rel(pid, 'PROBLEM_IN_DOMAIN', f'domain:{state.get("priority_domain")}', {'source_path': str(state_path.relative_to(ROOT))})
    ev_path = case / 'evidence_ledger.jsonl'
    if ev_path.exists():
        for line in ev_path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            ev = json.loads(line)
            eid = f'evidence:{ev.get("evidence_id")}'
            add_node(eid, 'Evidence', {'evidence_id': ev.get('evidence_id'), 'domain': ev.get('domain'), 'source_path': ev.get('source_path', str(ev_path.relative_to(ROOT))), 'summary': ev.get('summary','')})
            add_rel(cid, 'CASE_HAS_EVIDENCE', eid, {'source_path': str(ev_path.relative_to(ROOT))})
            for sup in ev.get('supports', []):
                pid = f'problem:{sup}'
                add_node(pid, 'Problem', {'name': sup, 'source_path': str(ev_path.relative_to(ROOT))})
                add_rel(eid, 'EVIDENCE_SUPPORTS_PROBLEM', pid, {'source_path': str(ev_path.relative_to(ROOT))})
    sol_path = case / 'solution_packet.md'
    if sol_path.exists():
        sid = f'solution:{case.name}:solution_packet'
        add_node(sid, 'Solution', {'name': 'solution_packet', 'case_id': case.name, 'source_path': str(sol_path.relative_to(ROOT))})
        if problem:
            add_rel(sid, 'SOLUTION_ADDRESSES_PROBLEM', f'problem:{problem}', {'source_path': str(sol_path.relative_to(ROOT))})
    delta_path = case / 'return_delta.json'
    if delta_path.exists():
        delta = json.loads(delta_path.read_text(encoding='utf-8'))
        did = f'delta:{delta.get("delta_id", case.name)}'
        add_node(did, 'Delta', {'delta_id': delta.get('delta_id'), 'status': delta.get('status'), 'source_path': str(delta_path.relative_to(ROOT))})
        add_rel(did, 'DELTA_CHANGES_CASE', cid, {'source_path': str(delta_path.relative_to(ROOT))})
    metrics_path = case / 'metrics_before_after.json'
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding='utf-8'))
        for m in metrics.get('metrics', []):
            mid = f'metric:{case.name}:{m.get("metric_id")}'
            add_node(mid, 'Metric', {'metric_id': m.get('metric_id'), 'case_id': case.name, 'status': m.get('status'), 'source_path': str(metrics_path.relative_to(ROOT))})
            add_rel(cid, 'CASE_HAS_METRIC', mid, {'source_path': str(metrics_path.relative_to(ROOT))})

graph = {'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'source_root': str(ROOT), 'nodes': nodes, 'relationships': rels}
(OUT / 'graph.json').write_text(json.dumps(graph, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# CSV export
fieldnames = sorted({k for n in nodes for k in n.keys()})
with (OUT / 'nodes.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for n in nodes:
        writer.writerow(n)
relfields = sorted({k for r in rels for k in r.keys()})
with (OUT / 'relationships.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=relfields)
    writer.writeheader()
    for r in rels:
        writer.writerow(r)
print('GRAPH_EXPORTED')
print(f'nodes: {len(nodes)}')
print(f'relationships: {len(rels)}')
print(f'graph: {(OUT / "graph.json").relative_to(ROOT)}')
