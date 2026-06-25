#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '05_outputs' / 'rag' / 'chunks.jsonl'
OUT.parent.mkdir(parents=True, exist_ok=True)
SKIP_PARTS = {'05_outputs'}
EXTS = {'.md','.json','.jsonl','.yaml','.yml'}

def infer_domain(path):
    parts = path.parts
    if '01_domains' in parts:
        i = parts.index('01_domains')
        if len(parts) > i + 1:
            return parts[i+1]
    return None

def infer_case(path):
    parts = path.parts
    if '02_cases' in parts:
        i = parts.index('02_cases')
        if len(parts) > i + 1:
            return parts[i+1]
    return None

def chunk_text(text, size=900):
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    cur = ''
    for p in paras:
        if len(cur) + len(p) + 2 <= size:
            cur = (cur + '\n\n' + p).strip()
        else:
            if cur:
                chunks.append(cur)
            cur = p[:size]
    if cur:
        chunks.append(cur)
    return chunks or [text[:size]]

items = []
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in EXTS:
        continue
    rel = p.relative_to(ROOT)
    if rel.parts and rel.parts[0] in SKIP_PARTS:
        continue
    text = p.read_text(encoding='utf-8', errors='replace')
    for idx, ch in enumerate(chunk_text(text)):
        raw_id = f'{rel}:{idx}'
        chunk_id = hashlib.sha1(raw_id.encode('utf-8')).hexdigest()[:16]
        items.append({
            'chunk_id': chunk_id,
            'source_path': str(rel),
            'domain': infer_domain(rel),
            'case_id': infer_case(rel),
            'allowed_use': 'diagnosis_and_navigation',
            'evidence_level': 'derived_from_repo',
            'created_at_utc': datetime.now(timezone.utc).isoformat(),
            'text': ch
        })
with OUT.open('w', encoding='utf-8') as f:
    for item in items:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
print('RAG_INDEX_CREATED')
print(f'chunks: {len(items)}')
print(f'output: {OUT.relative_to(ROOT)}')
