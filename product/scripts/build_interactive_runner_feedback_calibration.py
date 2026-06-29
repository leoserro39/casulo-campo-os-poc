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
cmd = [sys.executable, str(repo / "product/scripts/run_interactive_runner_feedback_calibration.py"), "--repo", str(repo)]
p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode:
    raise SystemExit(p.stdout + p.stderr)
print(p.stdout)
