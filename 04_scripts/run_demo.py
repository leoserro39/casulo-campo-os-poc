#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / '05_outputs' / 'reports' / 'poc_status.md'
SCRIPTS = [
    'validate_mesh.py',
    'triage_inbox.py',
    'apply_triage_manifest.py',
    'export_graph.py',
    'build_rag_index.py',
    'validate_mesh.py',
]

outputs = []
failed = False
for script in SCRIPTS:
    cmd = [sys.executable, str(ROOT / '04_scripts' / script)]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    outputs.append((script, proc.returncode, proc.stdout))
    print(f'==> {script}')
    print(proc.stdout.rstrip())
    if proc.returncode != 0:
        failed = True
        break

# Read counts if available.
node_count = rel_count = chunk_count = 'n/a'
graph = ROOT / '05_outputs' / 'graph' / 'graph.json'
rag = ROOT / '05_outputs' / 'rag' / 'chunks.jsonl'
if graph.exists():
    import json
    data = json.loads(graph.read_text(encoding='utf-8'))
    node_count = len(data.get('nodes', []))
    rel_count = len(data.get('relationships', []))
if rag.exists():
    chunk_count = sum(1 for line in rag.read_text(encoding='utf-8').splitlines() if line.strip())

status = 'FAIL' if failed else 'PASS'
lines = [
    '# CASULO Campo OS POC Status',
    '',
    f'Generated UTC: {datetime.now(timezone.utc).isoformat()}',
    f'Status: {status}',
    '',
    '## Created/validated capabilities',
    '',
    '- repo-as-mesh folder structure',
    '- canonical domains',
    '- demo case',
    '- triage manifest',
    '- proposed problem records',
    '- graph export',
    '- RAG chunks index',
    '- local deterministic chat',
    '',
    '## Counts',
    '',
    f'- graph nodes: {node_count}',
    f'- graph relationships: {rel_count}',
    f'- RAG chunks: {chunk_count}',
    '',
    '## Command log',
    '',
]
for script, code, out in outputs:
    lines.extend([f'### {script}', '', f'Exit code: {code}', '', '```text', out.rstrip(), '```', ''])
lines.extend([
    '## Next recommended task',
    '',
    'Add a controlled Neo4j import layer from nodes.csv and relationships.csv while keeping Git as the source of truth.',
    '',
    '## Important rule',
    '',
    'The chat may suggest actions, but persistent state changes must be written as files and validated before acceptance.',
])
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'POC_STATUS_REPORT: {REPORT.relative_to(ROOT)}')
if failed:
    sys.exit(1)
