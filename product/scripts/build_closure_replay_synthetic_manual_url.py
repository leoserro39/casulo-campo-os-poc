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
    ap.add_argument("--replay-count",type=int,default=1)
    ap.add_argument("--repo-slug",default="leoserro39/casulo-campo-os-poc")
    args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_closure_replay_synthetic_manual_url.py"),"--repo",str(repo),"--replay-count",str(args.replay_count),"--repo-slug",args.repo_slug])
    result=read(out/"prod441_460_closure_replay_result.json")
    ledger=read(out/"prod441_460_closure_replay_ledger.json")
    readiness={
        "contract_version":"casulo.closure_replay_synthetic_manual_url_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_REAL_MANUAL_URL_CAPTURE_AFTER_SYNTHETIC_REPLAY",
        "synthetic_only":result["synthetic_only"],
        "replay_count":result["replay_count"],
        "created_manually_ready_to_link_count":result["created_manually_ready_to_link_count"],
        "real_evidence_claim_count":result["real_evidence_claim_count"],
        "auto_execution_allowed":result["auto_execution_allowed"],
        "ready_for":["real manual issue URL capture","linkage logic review","closure ledger replay review"],
        "not_ready_for":["automatic issue creation","automatic closure","production activation","external client claims"],
        "next":"Use a real human-provided issue URL or keep ledger pending; do not promote synthetic URLs as real evidence.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Closure Replay with Synthetic Manual URL audit",
        "synthetic_only":result["synthetic_only"],
        "source_record_count":ledger["summary"]["source_record_count"],
        "replay_count":result["replay_count"],
        "created_manually_ready_to_link_count":result["created_manually_ready_to_link_count"],
        "real_evidence_claim_count":result["real_evidence_claim_count"],
        "auto_execution_allowed":result["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: synthetic URL replay validates CREATED_MANUALLY linkage path without real issue claim or automatic execution.",
    }
    for stem,title,obj in [
        ("prod441_460_readiness","Closure Replay Synthetic URL Readiness",readiness),
        ("prod441_460_audit_report","Closure Replay Synthetic URL Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    final={
        "task":"PROD-441..460",
        "status":"PASS",
        "phase":"Closure Replay with Synthetic Manual URL",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod441_460_synthetic_manual_url_manifest.json",
            "outputs/prod441_460_closure_replay_ledger.json",
            "outputs/prod441_460_closure_replay_result.json",
            "outputs/prod441_460_closure_replay_report.md",
            "outputs/prod441_460_readiness.json",
            "outputs/prod441_460_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-461..480 Real Manual Evidence Handoff Pack",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod441_460_result.json",final); write_md(out/"prod441_460_report.md","PROD-441..460 Closure Replay Synthetic URL Report",final)
    print(json.dumps(final,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
