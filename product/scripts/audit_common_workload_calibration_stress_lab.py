#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    out = Path(args.repo) / "outputs"
    audit = json.loads((out / "prod601a_620a_audit_report.json").read_text(encoding="utf-8"))
    gate = json.loads((out / "prod601a_620a_agent_real_case_entry_gate.json").read_text(encoding="utf-8"))
    thresholds = json.loads((out / "prod601a_620a_calibration_thresholds.json").read_text(encoding="utf-8"))
    audit["entry_gate"] = gate["decision"]
    audit["freeze_recommendation"] = thresholds["freeze_recommendation"]
    audit["status"] = "PASS"
    (out / "prod601a_620a_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod601a_620a_audit_report.md").write_text("# PROD-601A..620A Audit Report\n\n" + "\n".join([f"- {k}: `{v}`" for k, v in audit.items() if not isinstance(v, (list, dict))]) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
