#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def run(cmd, cwd=None):
    p=subprocess.run(cmd,capture_output=True,text=True,cwd=str(cwd) if cwd else None)
    if p.returncode:
        raise RuntimeError(p.stdout+p.stderr)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--archive-dir", default="/workspaces/casulo-campo-os-poc-package-archive")
    ap.add_argument("--move-zips", action="store_true")
    args=ap.parse_args()
    repo=Path(args.repo)
    cmd=[sys.executable, str(repo/"product/scripts/run_runtime_preservation_repo_hygiene.py"), "--repo", str(repo), "--archive-dir", args.archive_dir]
    if args.move_zips:
        cmd.append("--move-zips")
    run(cmd)
    print((repo/"outputs/prod501_520_result.json").read_text(encoding="utf-8"))
if __name__=="__main__": main()
