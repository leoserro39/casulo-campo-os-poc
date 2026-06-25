#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect(pattern):
    return sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    proposals = collect("05_outputs/proposals/*.json")
    manifests = collect("05_outputs/source_intake/manifests/*.json")
    reviews = collect("05_outputs/reviews/*.json")

    reviewed_paths = set()
    review_items = []
    for p in reviews:
        data = read_json(p)
        reviewed_paths.add(data.get("artifact_path"))
        review_items.append({
            "path": rel(p),
            "artifact_path": data.get("artifact_path"),
            "artifact_type": data.get("artifact_type"),
            "decision": data.get("decision"),
            "reviewer": data.get("reviewer"),
            "next_action": data.get("next_action"),
        })

    pending = []

    for p in proposals:
        data = read_json(p)
        if rel(p) not in reviewed_paths:
            pending.append({
                "type": "proposal",
                "path": rel(p),
                "question": data.get("question"),
                "status": data.get("status"),
                "domain": data.get("inferred_domain"),
                "reason": "proposal is waiting for human decision",
            })

    for p in manifests:
        data = read_json(p)
        gate = data.get("gate", "")
        if "HUMAN" in gate and rel(p) not in reviewed_paths:
            pending.append({
                "type": "source_manifest",
                "path": rel(p),
                "source_id": data.get("source_id"),
                "gate": gate,
                "hallucination_risk": data.get("hallucination_risk"),
                "reason": "source intake requires human review",
            })

    board = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "pending_count": len(pending),
        "review_count": len(review_items),
        "pending": pending,
        "reviews": review_items,
    }

    json_path = OUT / "human_review_board.json"
    md_path = OUT / "human_review_board.md"

    json_path.write_text(json.dumps(board, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Human Review Board",
        "",
        "- generated_utc: %s" % board["generated_utc"],
        "- pending_count: %s" % board["pending_count"],
        "- review_count: %s" % board["review_count"],
        "",
        "## Pending human action",
        "",
    ]

    if pending:
        for item in pending:
            title = item.get("question") or item.get("source_id") or item.get("path")
            lines.append("- %s | type=%s | path=%s | reason=%s" % (
                title,
                item.get("type"),
                item.get("path"),
                item.get("reason"),
            ))
    else:
        lines.append("- none")

    lines.extend(["", "## Recorded reviews", ""])

    if review_items:
        for item in review_items:
            lines.append("- decision=%s | artifact=%s | reviewer=%s | next=%s" % (
                item.get("decision"),
                item.get("artifact_path"),
                item.get("reviewer"),
                item.get("next_action"),
            ))
    else:
        lines.append("- none")

    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("HUMAN_REVIEW_BOARD_CREATED")
    print("md:", rel(md_path))
    print("json:", rel(json_path))
    print("pending_count:", board["pending_count"])
    print("review_count:", board["review_count"])


if __name__ == "__main__":
    main()
