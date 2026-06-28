from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))

def build_internal_review_handoff(audit_result_path: Path) -> Dict[str, Any]:
    audit = load_json(audit_result_path)
    summaries = audit.get('summaries', {})
    diagnostic = summaries.get('diagnostic', {})
    human_review = summaries.get('human_review', {})
    controlled_report = summaries.get('controlled_report', {})
    execution = summaries.get('execution', {})
    return {
        'contract_version': 'workbench.internal_review_handoff.v1.0',
        'case_id': audit.get('case_id'),
        'source_audit_status': audit.get('status'),
        'files_checked': audit.get('files_checked'),
        'sanitization': {'raw_runtime_contents_included': False, 'runtime_paths_included': True, 'summary_only': True},
        'diagnostic': {'status': diagnostic.get('status'), 'manifest_decision': diagnostic.get('manifest_decision'), 'data_quality': diagnostic.get('data_quality'), 'h_pre': diagnostic.get('h_pre'), 'h_post': diagnostic.get('h_post'), 'delta_l': diagnostic.get('delta_l'), 'decision': diagnostic.get('decision'), 'human_review_required': diagnostic.get('human_review_required')},
        'human_review': {'review_status': human_review.get('review_status'), 'decision': human_review.get('decision'), 'review_required': human_review.get('review_required'), 'blocked_next_actions': human_review.get('blocked_next_actions', [])},
        'controlled_report': {'status': controlled_report.get('status'), 'human_review_decision': controlled_report.get('human_review_decision'), 'ready_for_internal_review': controlled_report.get('ready_for_internal_review'), 'ready_for_client_review': controlled_report.get('ready_for_client_review'), 'implementation_authorized': controlled_report.get('implementation_authorized')},
        'execution': {'status': execution.get('status'), 'mode': execution.get('mode'), 'next_gate': execution.get('next_gate')},
        'limits': ['Internal review only.', 'Not client-facing truth.', 'No implementation authorized.', 'Runtime outputs remain ignored and must not be committed.'],
        'next_actions': ['Review controlled test evidence summary internally.', 'Confirm whether more evidence is required before any client-facing review.', 'Keep implementation blocked until a later solution gate explicitly approves execution.', 'Prepare a small-delta discussion using diagnostic decision and H_pre/H_post values.'],
    }

def validate_internal_review_handoff(handoff: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if handoff.get('contract_version') != 'workbench.internal_review_handoff.v1.0': errors.append('invalid contract_version')
    if handoff.get('source_audit_status') != 'PASS': errors.append('source audit must be PASS')
    if handoff.get('sanitization', {}).get('raw_runtime_contents_included') is not False: errors.append('raw runtime contents must not be included')
    if handoff.get('controlled_report', {}).get('implementation_authorized') is not False: errors.append('implementation must remain unauthorized')
    if handoff.get('controlled_report', {}).get('ready_for_client_review') is not False: errors.append('client review must remain false until explicit later approval')
    if 'implementation_execution' not in handoff.get('human_review', {}).get('blocked_next_actions', []): errors.append('implementation_execution must remain blocked')
    return errors

def handoff_markdown(handoff: Dict[str, Any]) -> str:
    d=handoff.get('diagnostic',{}); h=handoff.get('human_review',{}); c=handoff.get('controlled_report',{}); e=handoff.get('execution',{})
    lines=[f"# Internal Review Handoff - {handoff.get('case_id')}",'',f"- Source audit status: `{handoff.get('source_audit_status')}`",f"- Files checked: `{handoff.get('files_checked')}`",f"- Runtime raw contents included: `{handoff.get('sanitization',{}).get('raw_runtime_contents_included')}`",'', '## Diagnostic Summary', f"- Status: `{d.get('status')}`", f"- Manifest decision: `{d.get('manifest_decision')}`", f"- Data quality: `{d.get('data_quality')}`", f"- H_pre: `{d.get('h_pre')}`", f"- H_post: `{d.get('h_post')}`", f"- Delta_L: `{d.get('delta_l')}`", f"- Diagnostic decision: `{d.get('decision')}`",'', '## Human Review Gate', f"- Review status: `{h.get('review_status')}`", f"- Decision: `{h.get('decision')}`", f"- Review required: `{h.get('review_required')}`",'', '## Controlled Report Status', f"- Ready for internal review: `{c.get('ready_for_internal_review')}`", f"- Ready for client review: `{c.get('ready_for_client_review')}`", f"- Implementation authorized: `{c.get('implementation_authorized')}`",'', '## Execution', f"- Status: `{e.get('status')}`", f"- Mode: `{e.get('mode')}`", f"- Next gate: {e.get('next_gate')}",'','## Limits']
    for item in handoff.get('limits',[]): lines.append(f'- {item}')
    lines += ['', '## Next Actions']
    for item in handoff.get('next_actions',[]): lines.append(f'- {item}')
    return '\n'.join(lines)+'\n'

def brief_markdown(handoff: Dict[str, Any]) -> str:
    d=handoff.get('diagnostic',{}); c=handoff.get('controlled_report',{})
    return '\n'.join([f"# Internal Review Brief - {handoff.get('case_id')}", '', f"Controlled audit status: `{handoff.get('source_audit_status')}`.", f"Diagnostic decision: `{d.get('decision')}`.", f"Data quality: `{d.get('data_quality')}`.", f"H_pre/H_post: `{d.get('h_pre')}` -> `{d.get('h_post')}`.", f"Ready for internal review: `{c.get('ready_for_internal_review')}`.", f"Ready for client review: `{c.get('ready_for_client_review')}`.", f"Implementation authorized: `{c.get('implementation_authorized')}`.", '', 'Use this pack for internal review only.', ''])

def next_actions_markdown(handoff: Dict[str, Any]) -> str:
    lines=['# Internal Review Next Actions','']
    for item in handoff.get('next_actions',[]): lines.append(f'- {item}')
    lines += ['', '## Blocked', '- client-facing claim', '- implementation execution', '- production activation', '']
    return '\n'.join(lines)

def write_internal_review_handoff(output_dir: Path, audit_result_path: Path) -> Dict[str, Any]:
    handoff=build_internal_review_handoff(audit_result_path); errors=validate_internal_review_handoff(handoff)
    result={'status':'FAIL' if errors else 'PASS','case_id':handoff.get('case_id'),'source_audit_status':handoff.get('source_audit_status'),'ready_for_internal_review':handoff.get('controlled_report',{}).get('ready_for_internal_review'),'ready_for_client_review':handoff.get('controlled_report',{}).get('ready_for_client_review'),'implementation_authorized':handoff.get('controlled_report',{}).get('implementation_authorized'),'errors':errors,'generated_outputs':[]}
    if not errors:
        output_dir.mkdir(parents=True,exist_ok=True)
        files={'wb015_internal_review_handoff.json':json.dumps(handoff,indent=2,ensure_ascii=False)+'\n','wb015_internal_review_handoff.md':handoff_markdown(handoff),'wb015_internal_review_brief.md':brief_markdown(handoff),'wb015_internal_review_next_actions.md':next_actions_markdown(handoff)}
        for name,content in files.items():
            path=output_dir/name; path.write_text(content,encoding='utf-8'); result['generated_outputs'].append(str(path))
    return result
