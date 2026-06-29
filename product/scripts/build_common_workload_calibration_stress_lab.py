#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--cases-per-workload", type=int, default=100)
    args = parser.parse_args()
    repo = Path(args.repo)
    p = subprocess.run([
        sys.executable,
        str(repo / "product/scripts/run_common_workload_calibration_stress_lab.py"),
        "--repo",
        str(repo),
        "--cases-per-workload",
        str(args.cases_per_workload),
    ], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit(p.stdout + p.stderr)
    print(p.stdout)
if __name__ == "__main__":
    main()
