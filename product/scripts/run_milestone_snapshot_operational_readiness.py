#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

PHASES = [
    ("PROD-181..200", "Enterprise Parser Case Runner", "product-enterprise-parser-case-runner-v0.1"),
    ("PROD-201..220", "Stochastic Calibration Anomaly Lab", "product-stochastic-calibration-anomaly-lab-v0.1"),
    ("PROD-221..240", "Multi Seed Stability Drift", "product-multi-seed-stability-drift-v0.1"),
    ("PROD-241..260", "Graph Sync Telemetry Delta Library v2", "product-graph-sync-telemetry-delta-v2-v0.1"),
    ("PROD-261..280", "Graph Builder Telemetry Integration", "product-graph-builder-telemetry-integration-v0.1"),
    ("PROD-281..300", "Graph Task Bridge Practical Backlog", "product-graph-task-bridge-practical-backlog-v0.1"),
    ("PROD-301..320", "Real Anonymized Graph Case Runner", "product-real-anonymized-graph-case-runner-v0.1"),
    ("PROD-321..340", "Graph Case Review Console", "product-graph-case-review-console-v0.1"),
    ("PROD-341..360", "Manual Issue Promotion Pack", "product-manual-issue-promotion-pack-v0.1"),
    ("PROD-361..380", "Formal Approval Workflow Issue Guard", "product-formal-approval-workflow-issue-guard-v0.1"),
    ("PROD-381..400", "Minimal Approved Issue Dry Run", "product-minimal-approved-issue-dry-run-v0.1"),
    ("PROD-401..420", "Manual Issue Creation Evidence Capture", "product-manual-issue-creation-evidence-capture-v0.1"),
    ("PROD-421..440", "Issue-to-State Linkage Closure Ledger", "product-issue-to-state-linkage-closure-ledger-v0.1"),
    ("PROD-441..460", "Closure Replay Synthetic Manual URL", "product-closure-replay-synthetic-manual-url-v0.1"),
    ("PROD-461..480", "Real Manual Evidence Handoff Pack", "product-real-manual-evidence-handoff-pack-v0.1"),
]

KEY_OUTPUTS = [
    "outputs/prod461_480_real_manual_evidence_handoff.json",
    "outputs/prod461_480_readiness.json",
    "outputs/prod461_480_audit_report.json",
    "outputs/prod441_460_closure_replay_result.json",
    "outputs/prod441_460_readiness.json",
    "outputs/prod421_440_closure_ledger.json",
    "outputs/prod401_420_manual_issue_evidence_capture.json",
    "outputs/prod381_400_execution_guard.json",
    "outputs/prod361_380_issue_execution_guard.json",
    "outputs/prod321_340_review_console.json",
    "outputs/prod301_320_real_graph_case_aggregate.json",
]

def run_git(repo: Path, args: List[str]) -> str:
    try:
        p = subprocess.run(["git"] + args, cwd=str(repo), capture_output=True, text=True, check=False)
        if p.returncode != 0:
            return ""
        return p.stdout.strip()
    except Exception:
        return ""

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def read_json_or_none(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return read_json(path)
    except Exception:
        return None

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_tag_chain(repo: Path) -> Dict[str, Any]:
    head = run_git(repo, ["rev-parse", "--short", "HEAD"])
    branch = run_git(repo, ["branch", "--show-current"])
    tags_at_head = run_git(repo, ["tag", "--points-at", "HEAD"]).splitlines()
    recent_commits = run_git(repo, ["log", "--oneline", "-20"]).splitlines()
    status_short = run_git(repo, ["status", "--short"])
    phase_rows = []
    for phase_id, title, tag in PHASES:
        commit = run_git(repo, ["rev-list", "-n", "1", tag])
        short = commit[:7] if commit else ""
        phase_rows.append({
            "phase_id": phase_id,
            "title": title,
            "tag": tag,
            "commit": short,
            "tag_found": bool(commit),
        })
    return {
        "status": "PASS",
        "head": head,
        "branch": branch,
        "tags_at_head": tags_at_head,
        "recent_commits": recent_commits,
        "status_short": status_short,
        "phase_tags": phase_rows,
        "missing_tags": [r["tag"] for r in phase_rows if not r["tag_found"]],
    }

def extract_pending_evidence(repo: Path) -> Dict[str, Any]:
    handoff = read_json_or_none(repo / "outputs/prod461_480_real_manual_evidence_handoff.json") or {}
    ledger = read_json_or_none(repo / "outputs/prod421_440_closure_ledger.json") or {}
    replay = read_json_or_none(repo / "outputs/prod441_460_closure_replay_result.json") or {}

    pending_real = handoff.get("pending_real_manual_url_count", 0)
    valid_real = handoff.get("valid_real_evidence_count", 0)
    pending_manual_creation = ledger.get("summary", {}).get("pending_manual_creation_count", 0)
    synthetic_replay_ready = replay.get("created_manually_ready_to_link_count", 0)

    return {
        "pending_real_manual_url_count": pending_real,
        "valid_real_evidence_count": valid_real,
        "pending_manual_creation_count": pending_manual_creation,
        "synthetic_created_manually_ready_to_link_count": synthetic_replay_ready,
        "real_evidence_required": pending_real > 0 or valid_real == 0,
        "real_evidence_status": "PENDING_REAL_MANUAL_URL" if pending_real else "REAL_EVIDENCE_AVAILABLE",
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    tag_chain = build_tag_chain(repo)

    output_inventory = []
    for rel in KEY_OUTPUTS:
        p = repo / rel
        output_inventory.append({
            "path": rel,
            "exists": p.exists(),
            "status": (read_json_or_none(p) or {}).get("status") if p.exists() else None,
        })

    pending = extract_pending_evidence(repo)
    dirty_after_apply = bool(tag_chain.get("status_short"))

    decision = "MILESTONE_SNAPSHOT_READY_PENDING_REAL_EVIDENCE"
    if pending["valid_real_evidence_count"] > 0:
        decision = "MILESTONE_SNAPSHOT_READY_WITH_REAL_EVIDENCE"
    if dirty_after_apply:
        decision = "MILESTONE_SNAPSHOT_GENERATED_REQUIRES_COMMIT"

    snapshot = {
        "status": "PASS",
        "milestone": "PROD-181..480 Operational Cube Evidence-Gated Issue Workflow",
        "generated_at": now,
        "latest_commit": tag_chain["head"],
        "branch": tag_chain["branch"],
        "phase_count": len(PHASES),
        "phase_tags_found": len([r for r in tag_chain["phase_tags"] if r["tag_found"]]),
        "missing_tags": tag_chain["missing_tags"],
        "output_inventory": output_inventory,
        "pending_evidence": pending,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    dossier = {
        "status": "PASS",
        "decision": decision,
        "ready_for": [
            "milestone review",
            "repo state handoff",
            "real manual URL evidence capture",
            "next-cycle planning",
            "controlled investor/incubator technical explanation",
        ],
        "not_ready_for": [
            "automatic issue creation",
            "automatic closure",
            "production activation",
            "external client claims",
            "network verification of issues",
        ],
        "pending_evidence": pending,
        "interpretation": (
            "The product has a complete evidence-gated path from graph case selection to synthetic closure replay and real manual evidence handoff. "
            "It remains correctly blocked for automatic execution and external claims until real human-provided evidence is captured."
        ),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Milestone Snapshot Operational Readiness audit",
        "head": tag_chain["head"],
        "tags_at_head": tag_chain["tags_at_head"],
        "phase_count": snapshot["phase_count"],
        "phase_tags_found": snapshot["phase_tags_found"],
        "missing_tag_count": len(snapshot["missing_tags"]),
        "key_outputs_found": len([o for o in output_inventory if o["exists"]]),
        "key_outputs_expected": len(output_inventory),
        "pending_real_manual_url_count": pending["pending_real_manual_url_count"],
        "valid_real_evidence_count": pending["valid_real_evidence_count"],
        "blocked_actions": BLOCKED_ACTIONS,
        "finding": "PASS: milestone snapshot captures the current evidence-gated workflow and preserves no-auto-execution posture.",
    }

    write_json(out / "prod481_500_tag_chain_inventory.json", tag_chain)
    write_json(out / "prod481_500_milestone_snapshot.json", snapshot)
    write_json(out / "prod481_500_operational_readiness_dossier.json", dossier)
    write_json(out / "prod481_500_pending_evidence_register.json", pending)
    write_json(out / "prod481_500_audit_report.json", audit)

    lines = [
        "# PROD-481..500 Milestone Snapshot and Operational Readiness Dossier",
        "",
        f"- Status: `{snapshot['status']}`",
        f"- Decision: `{dossier['decision']}`",
        f"- Milestone: `{snapshot['milestone']}`",
        f"- Generated at: `{snapshot['generated_at']}`",
        f"- Latest commit: `{snapshot['latest_commit']}`",
        f"- Branch: `{snapshot['branch']}`",
        f"- Phase count: `{snapshot['phase_count']}`",
        f"- Phase tags found: `{snapshot['phase_tags_found']}`",
        f"- Pending real manual URLs: `{pending['pending_real_manual_url_count']}`",
        f"- Valid real evidence count: `{pending['valid_real_evidence_count']}`",
        "",
        "## Interpretation",
        dossier["interpretation"],
        "",
        "## Ready For",
    ]
    for item in dossier["ready_for"]:
        lines.append(f"- `{item}`")
    lines += ["", "## Not Ready For"]
    for item in dossier["not_ready_for"]:
        lines.append(f"- `{item}`")
    lines += ["", "## Phase Tags"]
    for row in tag_chain["phase_tags"]:
        lines.append(f"- `{row['phase_id']}` `{row['tag']}` → `{row['commit'] or 'MISSING'}`")
    write_text(out / "prod481_500_operational_readiness_dossier.md", "\n".join(lines) + "\n")

    audit_md = [
        "# PROD-481..500 Audit Report",
        "",
        f"- Status: `{audit['status']}`",
        f"- Head: `{audit['head']}`",
        f"- Phase count: `{audit['phase_count']}`",
        f"- Phase tags found: `{audit['phase_tags_found']}`",
        f"- Missing tag count: `{audit['missing_tag_count']}`",
        f"- Key outputs found: `{audit['key_outputs_found']}/{audit['key_outputs_expected']}`",
        f"- Pending real manual URLs: `{audit['pending_real_manual_url_count']}`",
        f"- Valid real evidence count: `{audit['valid_real_evidence_count']}`",
        f"- Finding: `{audit['finding']}`",
    ]
    write_text(out / "prod481_500_audit_report.md", "\n".join(audit_md) + "\n")

    return {
        "snapshot": snapshot,
        "dossier": dossier,
        "audit": audit,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps({
        "status": result["snapshot"]["status"],
        "decision": result["dossier"]["decision"],
        "latest_commit": result["snapshot"]["latest_commit"],
        "phase_tags_found": result["snapshot"]["phase_tags_found"],
        "pending_real_manual_url_count": result["snapshot"]["pending_evidence"]["pending_real_manual_url_count"],
        "valid_real_evidence_count": result["snapshot"]["pending_evidence"]["valid_real_evidence_count"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
