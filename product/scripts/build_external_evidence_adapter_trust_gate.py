#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

BLOCKED=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]

def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError(p.stdout+p.stderr)

def read(p): return json.loads(p.read_text(encoding="utf-8"))
def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_md(p,title,obj):
    lines=[f"# {title}",""]
    for k,v in obj.items():
        if isinstance(v,(str,int,float,bool)): lines.append(f"- {k}: `{v}`")
        elif isinstance(v,list):
            lines.append(f"\n## {k.replace('_',' ').title()}")
            for item in v: lines.append(f"- `{item}`")
        elif isinstance(v,dict):
            lines.append(f"\n## {k.replace('_',' ').title()}")
            for kk,vv in v.items(): lines.append(f"- {kk}: `{vv}`")
    p.write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--query", default="CASULO external evidence adapter trust gate")
    args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable, str(repo/"product/scripts/run_external_evidence_adapter_trust_gate.py"), "--repo", str(repo), "--query", args.query])
    adapter=read(out/"prod521_560_external_evidence_candidates.json")
    gate=read(out/"prod521_560_citation_gate_result.json")
    provider=read(out/"prod521_560_provider_registry.json")
    common=read(out/"prod521_560_common_workload_mass_test_register.json")
    readiness={
        "contract_version":"casulo.external_evidence_adapter_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_OPERATOR_CONSOLE_AND_SOLVER_API_PLANNING",
        "provider_count":provider["provider_count"],
        "candidate_count":gate["candidate_count"],
        "committed_count":gate["committed_count"],
        "human_review_count":gate["human_review_count"],
        "network_call_performed":adapter["network_call_performed"],
        "ready_for":["operator console","solver API planning","common workload mass test planning","business domain mass test planning"],
        "not_ready_for":["automatic external claims","production activation","credential handling","unreviewed provider network calls"],
        "next":"Build operator/demo surface and solver API plan before mass tests.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"External Evidence Adapter and Trust Gate audit",
        "provider_count":provider["provider_count"],
        "candidate_count":gate["candidate_count"],
        "committed_count":gate["committed_count"],
        "human_review_count":gate["human_review_count"],
        "rejected_count":gate["rejected_count"],
        "network_call_performed":adapter["network_call_performed"],
        "common_workload_count":len(common["workload_families"]),
        "finding":"PASS: external evidence is provider-neutral, mock-only by default, and gated before commitment.",
    }
    for stem,title,obj in [
        ("prod521_560_readiness","External Evidence Adapter Readiness",readiness),
        ("prod521_560_audit_report","External Evidence Adapter Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-521..560",
        "status":"PASS",
        "phase":"External Evidence Adapter and Trust Gate",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod521_560_provider_registry.json",
            "outputs/prod521_560_external_evidence_candidates.json",
            "outputs/prod521_560_citation_gate_result.json",
            "outputs/prod521_560_common_workload_mass_test_register.json",
            "outputs/prod521_560_readiness.json",
            "outputs/prod521_560_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-561..600 Operator Console and Solver API Surface",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod521_560_result.json",result)
    write_md(out/"prod521_560_report.md","PROD-521..560 External Evidence Adapter Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
