#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / '05_outputs' / 'triage' / 'triage_manifest.json'
DOMAINS_DIR = ROOT / '01_domains'
ALLOWED = {p.name for p in DOMAINS_DIR.iterdir() if p.is_dir()}

if not MANIFEST.exists():
    raise SystemExit('Missing manifest. Run triage_inbox.py first.')
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
created = 0
updated = 0
skipped = 0
for item in manifest.get('items', []):
    dom = item.get('proposed_domain')
    if dom not in ALLOWED:
        skipped += 1
        continue
    slug = item.get('record_slug') or item.get('problem_id') or 'problem_to_review'
    out = DOMAINS_DIR / dom / 'problems' / f'{slug}.md'
    content = f'''# Problem Record: {item.get('problem_id')}

Status: proposed
Domain: {dom}
Source: {item.get('source_path')}
Evidence level: {item.get('evidence_level')}
Confidence: {item.get('confidence')}
Generated at UTC: {datetime.now(timezone.utc).isoformat()}

## Summary

{item.get('summary')}

## Gate

This is a proposed problem record generated from inbox triage. It is not validated until reviewed by a human operator and connected to evidence.
'''
    if out.exists():
        updated += 1
    else:
        created += 1
    out.write_text(content, encoding='utf-8')
print('TRIAGE_APPLIED')
print(f'created: {created}')
print(f'updated: {updated}')
print(f'skipped: {skipped}')
