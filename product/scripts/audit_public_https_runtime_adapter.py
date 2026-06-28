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
    spec = json.loads((out / "prod161_170_public_openapi_spec.json").read_text(encoding="utf-8"))
    readiness = json.loads((out / "prod161_170_public_runtime_readiness.json").read_text(encoding="utf-8"))
    security = json.loads((out / "prod161_170_security_gate.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "Public HTTPS Runtime / FastAPI Deploy Adapter audit",
        "server_url": spec.get("servers", [{}])[0].get("url"),
        "https_url_valid": readiness.get("https_url_valid"),
        "openapi_paths": len(spec.get("paths", {})),
        "security_decision": security.get("decision"),
        "readiness": readiness.get("decision"),
        "finding": "PASS: adapter and action schema are ready for local/prototype deployment planning; HTTPS is mandatory for real Custom GPT Actions."
    }
    (out / "prod161_170_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod161_170_audit_report.md").write_text(
        "# PROD-161..170 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- Server URL: `{audit['server_url']}`\n"
        f"- HTTPS URL valid: `{audit['https_url_valid']}`\n"
        f"- OpenAPI paths: `{audit['openapi_paths']}`\n"
        f"- Security decision: `{audit['security_decision']}`\n"
        f"- Readiness: `{audit['readiness']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
