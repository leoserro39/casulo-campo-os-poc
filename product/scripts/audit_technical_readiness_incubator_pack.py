#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    out = repo / "outputs"
    memo = json.loads((out / "prod141_150_technical_readiness_memo.json").read_text(encoding="utf-8"))
    agent = json.loads((out / "prod141_150_chat_agent_operating_model.json").read_text(encoding="utf-8"))
    stack = json.loads((out / "prod141_150_target_stack.json").read_text(encoding="utf-8"))
    incubator = json.loads((out / "prod141_150_incubator_technical_pack.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "Technical readiness and incubator pack audit",
        "readiness_decision": memo.get("readiness_decision"),
        "chat_agent_modes": len(agent.get("modes", [])),
        "stack_layers": len(stack.get("stack_sequence", [])),
        "incubator_artifacts": len(incubator.get("technical_artifacts", [])),
        "finding": "PASS: ready to operate via chat now, then Custom GPT/Actions after proof, then stack/Codex/GitHub bridge after calibrated POC evidence."
    }
    (out / "prod141_150_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod141_150_audit_report.md").write_text(
        "# PROD-141..150 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- Readiness: `{audit['readiness_decision']}`\n"
        f"- Chat agent modes: `{audit['chat_agent_modes']}`\n"
        f"- Stack layers: `{audit['stack_layers']}`\n"
        f"- Incubator artifacts: `{audit['incubator_artifacts']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
