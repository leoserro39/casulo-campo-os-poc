#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/runtime_endpoint_preservation.contract.json",
    "product/contracts/repo_hygiene_zip_cleanup.contract.json",
    "product/contracts/runtime_surface_map.contract.json",
    "product/contracts/endpoint_registry.contract.json",
    "product/contracts/runtime_consolidation_readiness.contract.json",
    "product/schemas/runtime_endpoint_registry.schema.json",
    "product/schemas/repo_hygiene_report.schema.json",
    "product/schemas/runtime_surface_map.schema.json",
    "product/api/runtime_endpoint_registry.py",
    "product/scripts/run_runtime_preservation_repo_hygiene.py",
    "product/scripts/build_runtime_preservation_repo_hygiene.py",
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--archive-dir", default="/workspaces/casulo-campo-os-poc-package-archive")
    ap.add_argument("--move-zips", action="store_true")
    args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        cmd=[sys.executable,str(repo/"product/scripts/build_runtime_preservation_repo_hygiene.py"),"--repo",str(repo),"--archive-dir",args.archive_dir]
        if args.move_zips: cmd.append("--move-zips")
        p=subprocess.run(cmd,capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod501_520_repo_hygiene_report.json",
        "outputs/prod501_520_runtime_surface_map.json",
        "outputs/prod501_520_endpoint_registry_snapshot.json",
        "outputs/prod501_520_readiness.json",
        "outputs/prod501_520_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        surface=json.loads((repo/"outputs/prod501_520_runtime_surface_map.json").read_text(encoding="utf-8"))
        if surface.get("route_count", 0) < 40:
            errors.append("route_count unexpectedly low; endpoint preservation may be incomplete")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
