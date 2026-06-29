#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)
p = subprocess.run([sys.executable, str(repo / "product/scripts/run_solver_agent_controlled_stub.py"), "--repo", str(repo)], capture_output=True, text=True)
if p.returncode:
    raise SystemExit(p.stdout + p.stderr)
print(p.stdout)
