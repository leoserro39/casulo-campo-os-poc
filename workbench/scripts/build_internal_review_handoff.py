#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from api.services.internal_review_handoff import write_internal_review_handoff

def main()->int:
    p=argparse.ArgumentParser(description='Build CASULO internal review handoff pack.')
    p.add_argument('--audit-result',default=str(ROOT.parent/'outputs'/'wb014_runtime_evidence_audit_result.json'))
    p.add_argument('--output-dir',default=str(ROOT.parent/'outputs'))
    a=p.parse_args()
    result=write_internal_review_handoff(output_dir=Path(a.output_dir),audit_result_path=Path(a.audit_result))
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 1 if result.get('status')!='PASS' else 0
if __name__=='__main__': raise SystemExit(main())
