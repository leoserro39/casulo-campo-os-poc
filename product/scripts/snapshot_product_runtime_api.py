#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

from api.services.product_runtime_service import ProductRuntimeService


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "outputs"))
    args = parser.parse_args()

    service = ProductRuntimeService(Path(args.repo))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshots = {
        "health": service.health(),
        "product_status": service.product_status(),
        "verticals": service.verticals(),
        "vesselflow": service.vertical("vesselflow"),
        "vesselflow_state_request": service.state_request("vesselflow"),
        "vesselflow_import_manifest": service.vesselflow_import_manifest(),
        "reports": service.reports(),
    }

    (out_dir / "prod006_010_product_runtime_api_snapshot.json").write_text(
        json.dumps(snapshots, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "prod006_010_product_runtime_api_snapshot.md").write_text(
        snapshot_md(snapshots),
        encoding="utf-8",
    )

    print(json.dumps({"status": "PASS", "outputs": [
        str(out_dir / "prod006_010_product_runtime_api_snapshot.json"),
        str(out_dir / "prod006_010_product_runtime_api_snapshot.md"),
    ]}, indent=2))
    return 0


def snapshot_md(snapshots) -> str:
    status = snapshots["product_status"]
    vf = snapshots["vesselflow"]
    lines = [
        "# PROD-006..010 Product Runtime API Snapshot",
        "",
        f"- Status: `{status.get('status')}`",
        f"- Product direction: `{status.get('product_direction')}`",
        f"- Runtime mode: `{status.get('runtime_mode')}`",
        "",
        "## Vertical Summary",
    ]
    for item in snapshots["verticals"]["verticals"]:
        lines.append(f"- `{item.get('vertical_id')}` / `{item.get('complexity')}` / domains `{item.get('domains_count')}` / gates `{item.get('gates_count')}`")
    lines += [
        "",
        "## VesselFlow",
        f"- Status: `{vf.get('status')}`",
        f"- Name: `{vf.get('vertical', {}).get('vertical_name')}`",
        f"- Complexity: `{vf.get('vertical', {}).get('complexity')}`",
        "",
        "## Blocked Actions",
    ]
    for item in status.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Next", status.get("next_recommended_step", "")]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
