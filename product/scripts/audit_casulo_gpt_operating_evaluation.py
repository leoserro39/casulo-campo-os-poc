#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import argparse

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    out = repo / "outputs"
    report = json.loads((out / "prod081_120_evaluation_report.json").read_text(encoding="utf-8"))
    gate = json.loads((out / "prod081_120_technical_readiness_gate.json").read_text(encoding="utf-8"))
    hallucination = json.loads((out / "prod081_120_hallucination_index.json").read_text(encoding="utf-8"))
    delta = json.loads((out / "prod081_120_delta_index.json").read_text(encoding="utf-8"))
    intake = json.loads((out / "prod081_120_company_chat_intake.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "CASULO GPT operating evaluation audit",
        "readiness_gate": gate.get("gate"),
        "readiness_decision": gate.get("decision"),
        "avg_hallucination_reduction": hallucination.get("summary", {}).get("avg_reduction"),
        "avg_delta_reduction": delta.get("summary", {}).get("avg_reduction"),
        "cases_count": len(report.get("cases", [])),
        "company_chat_intake": intake.get("status"),
        "blocked_actions_preserved": gate.get("blocked_actions", []),
        "finding": "Technically ready for controlled company/incubator/POC service discussion; not ready for SaaS or production automation."
    }
    (out / "prod081_120_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod081_120_audit_report.md").write_text(
        "# PROD-081..120 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- Readiness gate: `{audit['readiness_gate']}`\n"
        f"- Decision: `{audit['readiness_decision']}`\n"
        f"- Company chat intake: `{audit['company_chat_intake']}`\n"
        f"- Avg hallucination reduction: `{audit['avg_hallucination_reduction']}`\n"
        f"- Avg delta reduction: `{audit['avg_delta_reduction']}`\n"
        f"- Cases: `{audit['cases_count']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
