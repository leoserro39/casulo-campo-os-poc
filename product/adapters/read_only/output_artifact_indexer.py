#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCAN_DIRS = ["outputs", "docs/product", "product/contracts", "product/calibration", "product/cube", "product/agent_manifest", "product/actions", "product/exocortex", "product/graph"]
SUFFIXES = {".json", ".md", ".yaml", ".yml", ".cypher", ".txt"}

def read_json(path: Path, default=None):
    if not path.exists() or path.suffix != ".json":
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def artifact_index(max_items=300):
    items = []
    for d in SCAN_DIRS:
        root = ROOT / d
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.suffix not in SUFFIXES:
                continue
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            stat = p.stat()
            item = {
                "path": rel,
                "suffix": p.suffix,
                "size_bytes": stat.st_size,
                "modified_time_unix": int(stat.st_mtime),
            }
            if p.suffix == ".json":
                data = read_json(p, {})
                if isinstance(data, dict):
                    item["status"] = data.get("status")
                    item["phase"] = data.get("phase")
                    item["decision"] = data.get("decision")
                    item["next"] = data.get("next")
            items.append(item)
            if len(items) >= max_items:
                break
        if len(items) >= max_items:
            break
    return {
        "adapter": "output_artifact_indexer.v0.1",
        "mode": "LOCAL_REPO_ARTIFACT_READ_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_dirs": SCAN_DIRS,
        "count": len(items),
        "items": items,
        "writes_allowed": False,
    }

def find_artifacts(query: str, max_items=80):
    q = query.lower().strip()
    idx = artifact_index(max_items=1000)["items"]
    hits = [x for x in idx if q in x["path"].lower() or q in str(x.get("phase", "")).lower() or q in str(x.get("decision", "")).lower()]
    return {
        "adapter": "output_artifact_indexer.v0.1",
        "query": query,
        "count": len(hits[:max_items]),
        "items": hits[:max_items],
        "writes_allowed": False,
    }

if __name__ == "__main__":
    print(json.dumps(artifact_index(), indent=2, ensure_ascii=False))
