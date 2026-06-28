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
    ap.add_argument("--repo",default=".")
    args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_milestone_snapshot_operational_readiness.py"),"--repo",str(repo)])
    snapshot=read(out/"prod481_500_milestone_snapshot.json")
    dossier=read(out/"prod481_500_operational_readiness_dossier.json")
    readiness={
        "contract_version":"casulo.milestone_snapshot_readiness.v0.1",
        "status":"PASS",
        "decision":dossier["decision"],
        "phase_count":snapshot["phase_count"],
        "phase_tags_found":snapshot["phase_tags_found"],
        "pending_real_manual_url_count":snapshot["pending_evidence"]["pending_real_manual_url_count"],
        "valid_real_evidence_count":snapshot["pending_evidence"]["valid_real_evidence_count"],
        "ready_for":dossier["ready_for"],
        "not_ready_for":dossier["not_ready_for"],
        "next":"Either capture real manual evidence URL or begin next cycle with a fresh milestone tag/snapshot.",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod481_500_readiness.json",readiness)
    write_md(out/"prod481_500_readiness.md","Milestone Snapshot Readiness",readiness)
    result={
        "task":"PROD-481..500",
        "status":"PASS",
        "phase":"Milestone Snapshot and Operational Readiness Dossier",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod481_500_tag_chain_inventory.json",
            "outputs/prod481_500_milestone_snapshot.json",
            "outputs/prod481_500_operational_readiness_dossier.json",
            "outputs/prod481_500_operational_readiness_dossier.md",
            "outputs/prod481_500_pending_evidence_register.json",
            "outputs/prod481_500_readiness.json",
            "outputs/prod481_500_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-501..520 Runtime Endpoint Preservation and Surface Consolidation",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod481_500_result.json",result)
    write_md(out/"prod481_500_report.md","PROD-481..500 Milestone Snapshot Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
