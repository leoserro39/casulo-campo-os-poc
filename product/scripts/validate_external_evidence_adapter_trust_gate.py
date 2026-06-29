#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/external_evidence_adapter.contract.json",
    "product/contracts/source_trust_policy.contract.json",
    "product/contracts/citation_gate.contract.json",
    "product/contracts/provider_contracts.contract.json",
    "product/contracts/common_workload_mass_test_register.contract.json",
    "product/schemas/external_evidence_candidate.schema.json",
    "product/schemas/citation_gate_result.schema.json",
    "product/schemas/external_evidence_provider.schema.json",
    "product/schemas/common_workload_mass_test_register.schema.json",
    "product/scripts/run_external_evidence_adapter_trust_gate.py",
    "product/scripts/build_external_evidence_adapter_trust_gate.py",
    "outputs/prod501_520_runtime_surface_map.json",
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--query", default="CASULO external evidence adapter trust gate")
    args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_external_evidence_adapter_trust_gate.py"),"--repo",str(repo),"--query",args.query],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod521_560_provider_registry.json",
        "outputs/prod521_560_external_evidence_candidates.json",
        "outputs/prod521_560_citation_gate_result.json",
        "outputs/prod521_560_common_workload_mass_test_register.json",
        "outputs/prod521_560_readiness.json",
        "outputs/prod521_560_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        adapter=json.loads((repo/"outputs/prod521_560_external_evidence_candidates.json").read_text(encoding="utf-8"))
        if adapter.get("network_call_performed") is not False:
            errors.append("network_call_performed must be false by default")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
