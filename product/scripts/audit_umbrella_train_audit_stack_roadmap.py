#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
out = Path(args.repo) / "outputs"
data = json.loads((out / "prod1181_1220_umbrella_train_audit.json").read_text(encoding="utf-8"))
(out / "prod1181_1220_umbrella_train_audit.md").write_text("# PROD-1181..1220 Umbrella Train Audit\n\n" + "\n".join([f"- {k}: `{v}`" for k, v in data.items() if not isinstance(v, (list, dict))]) + "\n", encoding="utf-8")
print(json.dumps(data, indent=2, ensure_ascii=False))
