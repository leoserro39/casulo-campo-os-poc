#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertical", required=True)
    parser.add_argument("--root", default="product/verticals")
    args = parser.parse_args()

    vdir = Path(args.root) / args.vertical
    manifest = json.loads((vdir / "vertical_manifest.json").read_text(encoding="utf-8"))
    domain_map = json.loads((vdir / "domain_map.json").read_text(encoding="utf-8"))
    gate_map = json.loads((vdir / "gate_map.json").read_text(encoding="utf-8"))
    cube_seed = json.loads((vdir / "operational_cube_seed.json").read_text(encoding="utf-8"))

    result = {
        "status": "PASS",
        "vertical_id": manifest["vertical_id"],
        "vertical_name": manifest["vertical_name"],
        "complexity": manifest["complexity"],
        "domains": len(manifest["domains"]),
        "entities": len(manifest["entities"]),
        "gates": len(manifest["gates"]),
        "domain_keys": list(domain_map.get("domains", {}).keys()),
        "blocked_by_default": gate_map.get("blocked_by_default", []),
        "cube_faces": list(cube_seed.get("faces", {}).keys()),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
