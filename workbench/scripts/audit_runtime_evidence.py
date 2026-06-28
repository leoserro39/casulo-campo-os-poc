#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.runtime_evidence_audit import audit_report_markdown, audit_runtime_evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit CASULO controlled runtime evidence.")
    parser.add_argument("--case-id", default="real_controlled_template_001")
    parser.add_argument("--runtime-root", default=str(ROOT / "runtime_outputs"))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-dir", default=str(ROOT.parent / "outputs"))
    args = parser.parse_args()

    audit = audit_runtime_evidence(case_id=args.case_id, runtime_root=Path(args.runtime_root))

    if args.write_report:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "wb014_runtime_evidence_audit_result.json").write_text(
            json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (out / "wb014_runtime_evidence_audit_report.md").write_text(
            audit_report_markdown(audit),
            encoding="utf-8",
        )

    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 1 if audit.get("status") != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
