#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

EXPECTED_OUTPUTS = [
    "State Snapshot",
    "Operational Graph",
    "Domain Map",
    "Evidence Manifest",
    "Gate Matrix",
    "Risk/Fragility Summary",
    "Delta Recommendations",
    "Cube/Cupula State",
    "Cockpit Replay",
    "Micrograph Timeline",
    "Internal Review Report",
]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_optional(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_state_request(vertical_id: str, root: Path) -> Dict[str, Any]:
    vertical_dir = root / "product" / "verticals" / vertical_id
    if not vertical_dir.exists():
        raise FileNotFoundError(f"missing vertical dir: {vertical_dir}")

    manifest = read_json(vertical_dir / "vertical_manifest.json")
    domain_map = read_json(vertical_dir / "domain_map.json")
    entity_map = read_json(vertical_dir / "entity_map.json")
    gate_map = read_json(vertical_dir / "gate_map.json")
    cube_seed = read_json(vertical_dir / "operational_cube_seed.json")

    sample_input = read_optional(vertical_dir / "sample_intake.md") or read_optional(vertical_dir / "sample_state_prompt.md")

    return {
        "contract_version": "operational_cube.vertical_state_request.v0.3",
        "vertical_id": vertical_id,
        "vertical_name": manifest["vertical_name"],
        "complexity": manifest["complexity"],
        "objective": manifest["purpose"],
        "target_user": manifest["target_user"],
        "domains": manifest["domains"],
        "domain_map": domain_map,
        "entities": manifest["entities"],
        "entity_map": entity_map,
        "evidence_types": manifest["evidence_types"],
        "gates": manifest["gates"],
        "gate_map": gate_map,
        "cube": cube_seed,
        "sample_input": sample_input.strip(),
        "expected_outputs": EXPECTED_OUTPUTS,
        "blocked_actions": manifest["blocked_by_default"],
        "instruction": (
            "Define the operational state for this vertical. Produce state, evidence, gates, deltas, "
            "Cube/Cupula state, replay, timeline and internal report. Do not authorize external use or implementation."
        ),
    }


def state_request_markdown(req: Dict[str, Any]) -> str:
    lines = [
        f"# Vertical State Request — {req['vertical_name']}",
        "",
        f"- Vertical ID: `{req['vertical_id']}`",
        f"- Complexity: `{req['complexity']}`",
        f"- Target user: {req['target_user']}",
        "",
        "## Objective",
        "",
        req["objective"],
        "",
        "## Domains",
    ]
    for item in req.get("domains", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Entities"]
    for item in req.get("entities", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Evidence Types"]
    for item in req.get("evidence_types", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Gates"]
    for item in req.get("gates", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Cube Faces"]
    for face, meaning in req.get("cube", {}).get("faces", {}).items():
        lines.append(f"- `{face}`: {meaning}")
    lines += ["", "## Expected Outputs"]
    for item in req.get("expected_outputs", []):
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in req.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Sample Input", "", req.get("sample_input", "_No sample input provided._"), ""]
    lines += ["## Product Instruction", "", req["instruction"], ""]
    return "\n".join(lines)


def write_state_request(vertical_id: str, root: Path, output_dir: Path) -> Dict[str, Any]:
    req = build_state_request(vertical_id=vertical_id, root=root)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"prod_vert004_006_{vertical_id}_state_request.json"
    md_path = output_dir / f"prod_vert004_006_{vertical_id}_state_request.md"

    json_path.write_text(json.dumps(req, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(state_request_markdown(req), encoding="utf-8")

    return {
        "status": "PASS",
        "vertical_id": vertical_id,
        "vertical_name": req["vertical_name"],
        "complexity": req["complexity"],
        "generated_outputs": [str(json_path), str(md_path)],
        "blocked_actions": req["blocked_actions"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Operational Cube vertical state request.")
    parser.add_argument("--vertical", required=True, choices=["small_service", "legal_office", "vesselflow", "all"])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    root = Path(args.repo)
    output_dir = Path(args.output_dir)
    verticals = ["small_service", "legal_office", "vesselflow"] if args.vertical == "all" else [args.vertical]

    results: List[Dict[str, Any]] = []
    for vertical in verticals:
        results.append(write_state_request(vertical_id=vertical, root=root, output_dir=output_dir))

    result = {"status": "PASS", "verticals": verticals, "results": results}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
