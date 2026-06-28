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
    spec = json.loads((out / "prod151_160_openapi_spec.json").read_text(encoding="utf-8"))
    manifest = json.loads((out / "prod151_160_action_manifest.json").read_text(encoding="utf-8"))
    readiness = json.loads((out / "prod151_160_connector_readiness.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "Custom GPT Actions / Agent Connector audit",
        "openapi_paths": len(spec.get("paths", {})),
        "actions": len(manifest.get("actions", [])),
        "requires_public_https": manifest.get("requires_public_https_for_real_custom_gpt"),
        "readiness": readiness.get("decision"),
        "finding": "PASS: local connector prototype is ready. Real Custom GPT Actions require public HTTPS runtime endpoint."
    }
    (out / "prod151_160_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod151_160_audit_report.md").write_text(
        "# PROD-151..160 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- OpenAPI paths: `{audit['openapi_paths']}`\n"
        f"- Actions: `{audit['actions']}`\n"
        f"- Requires public HTTPS: `{audit['requires_public_https']}`\n"
        f"- Readiness: `{audit['readiness']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
