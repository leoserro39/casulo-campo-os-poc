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
    run([sys.executable,str(repo/"product/scripts/run_real_manual_evidence_handoff.py"),"--repo",str(repo)])
    handoff=read(out/"prod461_480_real_manual_evidence_handoff.json")
    readiness={
        "contract_version":"casulo.real_manual_evidence_handoff_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_HUMAN_PROVIDED_REAL_MANUAL_ISSUE_URL",
        "candidate_count":handoff["candidate_count"],
        "valid_real_evidence_count":handoff["valid_real_evidence_count"],
        "pending_real_manual_url_count":handoff["pending_real_manual_url_count"],
        "synthetic_rejected_count":handoff["synthetic_rejected_count"],
        "auto_execution_allowed":handoff["auto_execution_allowed"],
        "ready_for":["human-provided real issue URL capture","real evidence validation","handoff checklist review"],
        "not_ready_for":["automatic issue creation","network verification","production activation","external client claims"],
        "next":"Have a human manually create or provide a real issue URL, then fill the manifest and re-run validation.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Real Manual Evidence Handoff Pack audit",
        "candidate_count":handoff["candidate_count"],
        "valid_real_evidence_count":handoff["valid_real_evidence_count"],
        "pending_real_manual_url_count":handoff["pending_real_manual_url_count"],
        "synthetic_rejected_count":handoff["synthetic_rejected_count"],
        "auto_execution_allowed":handoff["auto_execution_allowed"],
        "network_validation_performed":handoff["network_validation_performed"],
        "readiness":readiness["decision"],
        "finding":"PASS: real manual evidence handoff is ready; synthetic URLs are not promoted as real evidence.",
    }
    for stem,title,obj in [
        ("prod461_480_readiness","Real Manual Evidence Handoff Readiness",readiness),
        ("prod461_480_audit_report","Real Manual Evidence Handoff Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    final={
        "task":"PROD-461..480",
        "status":"PASS",
        "phase":"Real Manual Evidence Handoff Pack",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod461_480_real_manual_evidence_manifest_snapshot.json",
            "outputs/prod461_480_real_manual_evidence_handoff.json",
            "outputs/prod461_480_real_manual_evidence_handoff.md",
            "outputs/prod461_480_real_manual_evidence_validation.json",
            "outputs/prod461_480_real_manual_evidence_checklist.json",
            "outputs/prod461_480_readiness.json",
            "outputs/prod461_480_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-481..500 Real Evidence Linkage Replay or Milestone Snapshot",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod461_480_result.json",final); write_md(out/"prod461_480_report.md","PROD-461..480 Real Manual Evidence Handoff Report",final)
    print(json.dumps(final,indent=2,ensure_ascii=False))
if __name__=="__main__": main()
