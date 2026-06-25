#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "05_outputs" / "reviews"
OUT = ROOT / "05_outputs" / "return_deltas"


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def slug(value):
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value or "").strip("_").lower()
    return text[:90] or "return_delta"


def latest_approved_review():
    files = sorted(REVIEWS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in files:
        data = read_json(path)
        if data.get("decision") == "APPROVED" and data.get("artifact_type") == "proposal":
            return path, data
    raise SystemExit("no approved proposal review found")


def extract_proposal_bullets(proposal_json_path):
    md_path = proposal_json_path.with_suffix(".md")
    if not md_path.exists():
        return []

    lines = md_path.read_text(encoding="utf-8").splitlines()
    in_section = False
    bullets = []

    for line in lines:
        if line.strip() == "## Controlled proposal":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            bullets.append(line.strip()[2:])

    return bullets


def build_return_delta(review_path, review):
    artifact_path = ROOT / review["artifact_path"]
    proposal = read_json(artifact_path)
    changes = extract_proposal_bullets(artifact_path)

    question = proposal.get("question") or review.get("artifact_id") or "approved proposal"
    domain = proposal.get("inferred_domain") or review.get("source_summary", {}).get("inferred_domain") or "unknown"
    mesh_delta = proposal.get("mesh_delta") or review.get("source_summary", {}).get("mesh_delta") or {}

    if not changes:
        changes = [
            "Create controlled pilot action from approved proposal.",
            "Measure operational effect before canonical promotion.",
        ]

    stamp = utc_stamp()
    base = "return_delta_%s_%s" % (slug(question), stamp)

    delta = {
        "status": "RETURN_DELTA_PROPOSED",
        "generated_utc": stamp,
        "source_review": rel(review_path),
        "source_proposal": review["artifact_path"],
        "question": question,
        "target_branch": domain,
        "canonical_effect": "PROPOSED_ONLY",
        "requires_final_apply": True,
        "approved_by": review.get("reviewer"),
        "approval_notes": review.get("notes"),
        "mesh_delta": mesh_delta,
        "proposed_changes": changes,
        "safety_rules": [
            "Do not modify canonical state automatically.",
            "Apply only after explicit final approval.",
            "Keep original proposal, review and return delta traceable.",
            "Measure pilot result before promoting long-term state.",
        ],
        "next_action": "Run final apply gate if the operator wants to promote this return delta.",
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")

    json_path.write_text(json.dumps(delta, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Return Delta Proposal",
        "",
        "- status: RETURN_DELTA_PROPOSED",
        "- generated_utc: %s" % stamp,
        "- source_review: %s" % rel(review_path),
        "- source_proposal: %s" % review["artifact_path"],
        "- target_branch: %s" % domain,
        "- canonical_effect: PROPOSED_ONLY",
        "- requires_final_apply: true",
        "",
        "## Approved by",
        "",
        "- %s" % review.get("reviewer"),
        "",
        "## Proposed changes",
        "",
    ]

    lines.extend(["- " + item for item in changes])

    lines.extend([
        "",
        "## Mesh Delta Reference",
        "",
        "- Delta_L: %s" % mesh_delta.get("Delta_L"),
        "- H_pre: %s" % mesh_delta.get("H_pre"),
        "- gate: %s" % mesh_delta.get("gate"),
        "- support_ratio: %s" % mesh_delta.get("support_ratio"),
        "- missing_ratio: %s" % mesh_delta.get("missing_ratio"),
        "",
        "## Safety rules",
        "",
    ])

    lines.extend(["- " + item for item in delta["safety_rules"]])

    lines.extend([
        "",
        "## Next action",
        "",
        "- Run final apply gate if the operator wants to promote this return delta.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("RETURN_DELTA_PROPOSED")
    print("return_delta:", rel(md_path))
    print("trace:", rel(json_path))
    print("target_branch:", domain)
    print("canonical_effect: PROPOSED_ONLY")
    print("requires_final_apply: true")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-approved-review", action="store_true")
    parser.add_argument("--review")
    args = parser.parse_args()

    if args.latest_approved_review:
        review_path, review = latest_approved_review()
    elif args.review:
        review_path = ROOT / args.review
        review = read_json(review_path)
    else:
        raise SystemExit("use --latest-approved-review or --review PATH")

    if review.get("decision") != "APPROVED":
        raise SystemExit("review is not APPROVED")

    build_return_delta(review_path, review)


if __name__ == "__main__":
    main()
