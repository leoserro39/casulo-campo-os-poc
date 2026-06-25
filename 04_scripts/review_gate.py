#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "05_outputs" / "reviews"


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def norm_decision(value):
    v = (value or "").strip().lower()
    aliases = {
        "approve": "APPROVED",
        "approved": "APPROVED",
        "aprovar": "APPROVED",
        "aprovado": "APPROVED",
        "reject": "REJECTED",
        "rejected": "REJECTED",
        "rejeitar": "REJECTED",
        "rejeitado": "REJECTED",
        "needs_more_evidence": "NEEDS_MORE_EVIDENCE",
        "evidence": "NEEDS_MORE_EVIDENCE",
        "mais_evidencia": "NEEDS_MORE_EVIDENCE",
        "pedir_evidencia": "NEEDS_MORE_EVIDENCE",
    }
    if v not in aliases:
        raise SystemExit("invalid decision: use approve, reject, or needs_more_evidence")
    return aliases[v]


def slug(value):
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value or "").strip("_").lower()
    return text[:90] or "artifact"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def rel(path):
    return str(path.relative_to(ROOT))


def latest_proposal():
    files = sorted((ROOT / "05_outputs" / "proposals").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit("no proposal json found")
    return files[0]


def classify_artifact(path):
    rp = rel(path)
    if "/proposals/" in rp:
        return "proposal"
    if "/source_intake/manifests/" in rp:
        return "source_manifest"
    if "/deltas/" in rp:
        return "mesh_delta"
    return "artifact"


def next_action_for(decision):
    if decision == "APPROVED":
        return "Eligible for return delta proposal. Canonical state is still unchanged."
    if decision == "REJECTED":
        return "Do not promote this artifact. Keep it as rejected evidence."
    return "Collect more evidence or reduce scope before promotion."


def write_review(artifact_path, decision, reviewer, notes):
    artifact_path = Path(artifact_path)
    if not artifact_path.is_absolute():
        artifact_path = ROOT / artifact_path
    if not artifact_path.exists():
        raise SystemExit("artifact not found: %s" % artifact_path)

    REVIEWS.mkdir(parents=True, exist_ok=True)

    data = read_json(artifact_path)
    artifact_type = classify_artifact(artifact_path)
    stamp = utc_stamp()
    decision = norm_decision(decision)

    artifact_id = (
        data.get("source_id")
        or data.get("question")
        or data.get("status")
        or artifact_path.stem
    )

    base = "review_%s_%s_%s" % (artifact_type, slug(str(artifact_id)), stamp)
    json_path = REVIEWS / (base + ".json")
    md_path = REVIEWS / (base + ".md")

    review = {
        "status": "RECORDED",
        "reviewed_utc": stamp,
        "reviewer": reviewer,
        "decision": decision,
        "artifact_type": artifact_type,
        "artifact_path": rel(artifact_path),
        "artifact_id": artifact_id,
        "notes": notes,
        "canonical_effect": "NONE",
        "next_action": next_action_for(decision),
        "source_summary": {
            "status": data.get("status"),
            "question": data.get("question"),
            "inferred_domain": data.get("inferred_domain"),
            "gate": data.get("gate"),
            "hallucination_risk": data.get("hallucination_risk"),
            "trust_score": data.get("trust_score"),
            "mesh_delta": data.get("mesh_delta"),
        },
    }

    json_path.write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Human Review",
        "",
        "- status: RECORDED",
        "- reviewed_utc: %s" % stamp,
        "- reviewer: %s" % reviewer,
        "- decision: %s" % decision,
        "- artifact_type: %s" % artifact_type,
        "- artifact_path: %s" % rel(artifact_path),
        "- canonical_effect: NONE",
        "",
        "## Notes",
        "",
        notes or "- none",
        "",
        "## Next action",
        "",
        "- %s" % next_action_for(decision),
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("HUMAN_REVIEW_RECORDED")
    print("review:", rel(md_path))
    print("trace:", rel(json_path))
    print("decision:", decision)
    print("canonical_effect: NONE")
    print("next_action:", next_action_for(decision))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact")
    parser.add_argument("--latest-proposal", action="store_true")
    parser.add_argument("--decision", required=True)
    parser.add_argument("--reviewer", default="human_operator")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.latest_proposal:
        artifact = latest_proposal()
    elif args.artifact:
        artifact = Path(args.artifact)
    else:
        raise SystemExit("use --artifact PATH or --latest-proposal")

    write_review(artifact, args.decision, args.reviewer, args.notes)


if __name__ == "__main__":
    main()
