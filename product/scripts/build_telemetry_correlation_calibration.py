#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
repo=Path(args.repo)
p=subprocess.run([sys.executable,str(repo/"product/scripts/run_telemetry_correlation_calibration.py"),"--repo",str(repo)],capture_output=True,text=True)
if p.returncode: raise SystemExit(p.stdout+p.stderr)
print(p.stdout)
