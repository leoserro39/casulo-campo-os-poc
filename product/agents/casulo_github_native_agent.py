#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib import request

ROOT = Path.cwd()

def rj(path: str, default=None):
    p = ROOT / path
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def safe_key(value: str) -> str:
    value = value.strip() or "default"
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value[:120]

def default_prompt(case_id: str) -> str:
    ctx = rj("product/evaluation/real_tests/real_case_001/real_case_001_context_packet_v0_3.json", {})
    ev = rj("product/evaluation/real_tests/real_case_001/real_case_001_evidence_packet_v0_3.json", {})
    return (
        "CASULO GitHub Native Agent\n"
        f"CASE_ID={case_id}\n"
        "CONTEXT=" + json.dumps(ctx, ensure_ascii=False) + "\n"
        "EVIDENCE=" + json.dumps(ev, ensure_ascii=False) + "\n"
        "Required sections: Operational state; Evidence used; Evidence gaps; Gate decision; "
        "Allowed actions; Blocked actions; Risk of hallucination/overclaim; Next safe step. "
        "Do not claim production/client/commercial/validated hallucination reduction."
    )

def load_prompt(case_id: str, prompt_file: str | None) -> tuple[str, str]:
    if prompt_file:
        p = ROOT / prompt_file
        if not p.exists():
            raise SystemExit(f"PROMPT_FILE_NOT_FOUND: {prompt_file}")
        return p.read_text(encoding="utf-8"), prompt_file
    return default_prompt(case_id), "default_real_case_001_context_packet"

def call_openai(txt: str, model: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    assert key, "OPENAI_API_KEY required"
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Controlled CASULO operational-state agent. Respect gates, evidence boundaries and blocked actions."},
            {"role": "user", "content": txt},
        ],
        "temperature": 0.1,
    }
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data).encode(),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
        method="POST",
    )
    return json.loads(request.urlopen(req, timeout=120).read().decode())["choices"][0]["message"]["content"]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", default="REAL-CASE-001")
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--allow-llm", action="store_true")
    ap.add_argument("--prompt-file", default=None)
    ap.add_argument("--run-key", default=None)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    run_key = safe_key(args.run_key) if args.run_key else None
    if args.out_dir:
        out = ROOT / args.out_dir
    elif run_key:
        out = ROOT / "product" / "agent_runs" / "real_case_001" / run_key
    else:
        out = ROOT / "product" / "agent_runs" / "real_case_001"
    out.mkdir(parents=True, exist_ok=True)

    prompt, prompt_source = load_prompt(args.case_id, args.prompt_file)

    output = "DRY_RUN_ONLY"
    if args.allow_llm:
        output = call_openai(prompt, args.model)

    run = {
        "version": "casulo_github_native_agent_run.v0.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": args.case_id,
        "run_key": run_key or "default",
        "model": args.model,
        "llm_executed": bool(args.allow_llm),
        "ready_for_delta_zero_scoring": bool(args.allow_llm),
        "prompt_source": prompt_source,
        "output_dir": str(out.relative_to(ROOT)),
        "external_writes_executed": False,
        "blocked_actions": [
            "client_facing_validated_claim",
            "production_activation",
            "commercial_claim",
            "validated_model_gain_claim",
            "validated_hallucination_reduction_claim",
            "automatic_merge",
            "github_issue_comment",
            "github_pr_comment",
            "external_repo_write",
            "production_neo4j_write"
        ]
    }

    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    (out / "model_output.md").write_text(output, encoding="utf-8")
    (out / "agent_run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(run, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
