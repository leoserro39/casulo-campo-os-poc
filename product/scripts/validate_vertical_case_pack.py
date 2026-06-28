#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED = ["vertical_manifest.json", "domain_map.json", "entity_map.json", "gate_map.json", "operational_cube_seed.json", "expected_outputs.md"]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="product/verticals")
    args = parser.parse_args()
    root = Path(args.root)
    verticals = ["small_service", "legal_office", "vesselflow"]
    errors = []
    warnings = []
    if not root.exists():
        errors.append(f"missing vertical root: {root}")
    for vid in verticals:
        vdir = root / vid
        if not vdir.exists():
            errors.append(f"missing vertical dir: {vid}")
            continue
        for filename in REQUIRED:
            if not (vdir / filename).exists():
                errors.append(f"{vid}: missing {filename}")
        manifest_path = vdir / "vertical_manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                for key in ["vertical_id", "vertical_name", "complexity", "domains", "entities", "evidence_types", "gates", "expected_cube_faces", "blocked_by_default"]:
                    if key not in manifest:
                        errors.append(f"{vid}: manifest missing key {key}")
                if manifest.get("vertical_id") != vid:
                    errors.append(f"{vid}: vertical_id mismatch")
                if "implementation_execution" not in manifest.get("blocked_by_default", []):
                    errors.append(f"{vid}: implementation_execution must be blocked by default")
            except Exception as exc:
                errors.append(f"{vid}: invalid manifest JSON: {exc}")
    result = {"status": "FAIL" if errors else "PASS", "verticals": verticals, "checks": len(verticals) * len(REQUIRED), "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
