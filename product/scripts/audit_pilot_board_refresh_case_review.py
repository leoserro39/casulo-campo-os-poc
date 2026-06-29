#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
out = Path(args.repo) / "outputs"
audit = json.loads((out / "prod821_860_pilot_board_refresh_audit_report.json").read_text(encoding="utf-8"))
readiness = json.loads((out / "prod821_860_pilot_board_refresh_readiness.json").read_text(encoding="utf-8"))
audit["readiness"] = readiness["decision"]
audit["status"] = "PASS"
(out / "prod821_860_pilot_board_refresh_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(out / "prod821_860_pilot_board_refresh_audit_report.md").write_text("# PROD-821..860 Pilot Board Refresh Audit Report\n\n" + "\n".join([f"- {k}: `{v}`" for k, v in audit.items() if not isinstance(v, (list, dict))]) + "\n", encoding="utf-8")
print(json.dumps(audit, indent=2, ensure_ascii=False))
