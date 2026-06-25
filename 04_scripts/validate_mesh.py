#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOMAINS = ['atendimento','vendas','operacao','financeiro','marketing','gestao','tecnologia','impacto']
REQUIRED_ROOT_DIRS = ['00_program','00_inbox/raw_docs','01_domains','02_cases','03_micrographs','04_scripts','05_outputs']
REQUIRED_CASE_FILES = ['intake.md','business_state.json','evidence_ledger.jsonl','diagnosis.md','solution_packet.md','execution_checklist.md','metrics_before_after.json','return_delta.json','public_case.md']
REQUIRED_DOMAIN_FILES = ['DOMAIN.md','state.json','evidence.jsonl']
REQUIRED_DELTA_KEYS = ['status','evidence_refs','changed_state','open_gaps','next_actions']

errors = []
warnings = []
checks = 0

def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)

def warn(cond, msg):
    if not cond:
        warnings.append(msg)

def load_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'Invalid JSON: {path.relative_to(ROOT)} :: {exc}')
        return None

def load_jsonl(path):
    count = 0
    try:
        for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.strip():
                continue
            json.loads(line)
            count += 1
    except Exception as exc:
        errors.append(f'Invalid JSONL: {path.relative_to(ROOT)} line {i} :: {exc}')
    return count

for rel in REQUIRED_ROOT_DIRS:
    check((ROOT / rel).exists(), f'Missing required path: {rel}')

for dom in DOMAINS:
    d = ROOT / '01_domains' / dom
    check(d.exists(), f'Missing domain folder: {dom}')
    for fname in REQUIRED_DOMAIN_FILES:
        p = d / fname
        check(p.exists(), f'Missing domain file: {dom}/{fname}')
    for sub in ['problems','solutions','deltas']:
        check((d / sub).exists(), f'Missing domain subfolder: {dom}/{sub}')
    if (d / 'state.json').exists():
        data = load_json(d / 'state.json')
        if data:
            check(data.get('domain_id') == dom, f'Domain state domain_id mismatch: {dom}')
    if (d / 'evidence.jsonl').exists():
        load_jsonl(d / 'evidence.jsonl')

cases_dir = ROOT / '02_cases'
case_dirs = [p for p in cases_dir.iterdir() if p.is_dir()] if cases_dir.exists() else []
check(bool(case_dirs), 'No cases found in 02_cases')

for case in case_dirs:
    for fname in REQUIRED_CASE_FILES:
        check((case / fname).exists(), f'Missing case file: {case.name}/{fname}')
    if (case / 'business_state.json').exists():
        data = load_json(case / 'business_state.json')
        if data:
            check(data.get('case_id') == case.name, f'Case id mismatch in {case.name}/business_state.json')
            priority = data.get('priority_domain')
            warn(priority in DOMAINS, f'Case {case.name} priority_domain is not canonical: {priority}')
    if (case / 'metrics_before_after.json').exists():
        load_json(case / 'metrics_before_after.json')
    if (case / 'return_delta.json').exists():
        delta = load_json(case / 'return_delta.json')
        if delta:
            for key in REQUIRED_DELTA_KEYS:
                check(key in delta, f'Missing return_delta key in {case.name}: {key}')
            check(delta.get('case_id') == case.name, f'Delta case_id mismatch in {case.name}/return_delta.json')
    if (case / 'evidence_ledger.jsonl').exists():
        count = load_jsonl(case / 'evidence_ledger.jsonl')
        warn(count > 0, f'Empty evidence ledger: {case.name}')

# Output folders may be empty in first run, but must exist.
for rel in ['05_outputs/triage','05_outputs/graph','05_outputs/rag','05_outputs/reports']:
    check((ROOT / rel).exists(), f'Missing output folder: {rel}')

status = 'PASS' if not errors else 'FAIL'
print(f'CASULO_CAMPO_VALIDATE: {status}')
print(f'checks: {checks}')
print(f'errors: {len(errors)}')
print(f'warnings: {len(warnings)}')
if errors:
    print('\nERRORS:')
    for e in errors:
        print(f'- {e}')
if warnings:
    print('\nWARNINGS:')
    for w in warnings:
        print(f'- {w}')
if errors:
    sys.exit(1)
