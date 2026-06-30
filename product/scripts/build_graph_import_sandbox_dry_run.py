#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)
p = subprocess.run([sys.executable, str(repo / "product/scripts/run_graph_import_sandbox_dry_run.py"), "--repo", str(repo)], capture_output=True, text=True)
if p.returncode:
    raise SystemExit(p.stdout + p.stderr)
print(p.stdout)
