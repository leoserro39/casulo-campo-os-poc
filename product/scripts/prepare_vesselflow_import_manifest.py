#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any


REQUIRED_INPUTS = [
    "dataset_or_workbook",
    "expected_nomination_flow",
    "qualification_rules",
    "known_blocking_rules",
]

OPTIONAL_INPUTS = [
    "contract_records",
    "pvq_q88_extract",
    "certificate_list",
    "cargo_platform_matrix",
    "decision_logs",
    "audit_reports",
]


def build_manifest(output_dir: Path) -> Dict[str, Any]:
    manifest = {
        "contract_version": "operational_cube.vesselflow_import_manifest.v0.3",
        "vertical_id": "vesselflow",
        "status": "WAITING_FOR_USER_DATA",
        "required_inputs": REQUIRED_INPUTS,
        "optional_inputs": OPTIONAL_INPUTS,
        "received_inputs": [],
        "missing_required_inputs": REQUIRED_INPUTS,
        "default_policy": "Do not execute nomination automatically. Define controlled operational state only.",
        "expected_outputs": [
            "State Snapshot",
            "Operational Graph",
            "Domain Map",
            "Contract Map",
            "Nomination Flow",
            "Gate Matrix",
            "Evidence Manifest",
            "Risk/Fragility Index",
            "Delta Recommendations",
            "Cube/Cupula State",
            "Cockpit Replay",
            "Report",
        ],
        "blocked_actions": [
            "automatic_nomination",
            "client_facing_claim",
            "implementation_execution",
            "production_activation",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "prod_vert004_006_vesselflow_import_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "prod_vert004_006_vesselflow_import_manifest.md").write_text(
        manifest_md(manifest),
        encoding="utf-8",
    )
    return manifest


def manifest_md(manifest: Dict[str, Any]) -> str:
    lines = [
        "# VesselFlow Import Manifest",
        "",
        f"- Status: `{manifest['status']}`",
        f"- Default policy: {manifest['default_policy']}",
        "",
        "## Required Inputs",
    ]
    for item in manifest["required_inputs"]:
        lines.append(f"- `{item}`")
    lines += ["", "## Optional Inputs"]
    for item in manifest["optional_inputs"]:
        lines.append(f"- `{item}`")
    lines += ["", "## Expected Outputs"]
    for item in manifest["expected_outputs"]:
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in manifest["blocked_actions"]:
        lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    manifest = build_manifest(Path(args.output_dir))
    print(json.dumps({"status": "PASS", "manifest": manifest}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
