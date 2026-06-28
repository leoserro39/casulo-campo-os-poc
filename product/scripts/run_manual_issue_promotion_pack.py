#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
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

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:120] or "issue"

def selected_issues(repo: Path) -> List[Dict[str, Any]]:
    data = read_json(repo / "outputs/prod321_340_issue_selection.json")
    return data.get("selected_issues", [])

def decision_map(repo: Path) -> Dict[str, Dict[str, Any]]:
    path = repo / "outputs/prod321_340_review_decision_log.json"
    if not path.exists():
        return {}
    rows = read_json(path).get("review_decisions", [])
    return {r["issue_id"]: r for r in rows}

def default_manifest(selected: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "status": "DRAFT_REVIEW_REQUIRED",
        "approval_policy": "no_issue_is_approved_by_default",
        "instructions": [
            "Edit approved_issue_ids manually after human review.",
            "Only include issue IDs explicitly approved by the reviewer.",
            "Do not approve production automation or client-facing claims.",
        ],
        "available_issue_ids": [i["issue_id"] for i in selected],
        "approved_issue_ids": [],
        "blocked_actions": BLOCKED_ACTIONS,
    }

def load_or_create_manifest(repo: Path, selected: List[Dict[str, Any]]) -> Dict[str, Any]:
    path = repo / "product/poc/manual_issue_promotion/approved_issue_manifest.json"
    if path.exists():
        return read_json(path)
    manifest = default_manifest(selected)
    write_json(path, manifest)
    return manifest

def issue_markdown(issue: Dict[str, Any], decision: Dict[str, Any]) -> str:
    labels = ", ".join(issue.get("labels", []))
    return f"""# {issue['title']}

## CASULO Review Metadata

- Issue candidate: `{issue['issue_id']}`
- Case: `{issue['case_id']}`
- Priority: `{issue.get('priority')}`
- Source delta: `{issue.get('source_delta')}`
- Review route: `{issue.get('review_route')}`
- Selection score: `{issue.get('selection_score')}`
- Recommended decision: `{decision.get('recommended_decision', 'REVIEW_REQUIRED')}`
- Human approval required: `{decision.get('requires_human_approval', True)}`
- Auto-created issue: `False`

## Labels

`{labels}`

{issue.get('body', '').strip()}

## Manual Promotion Guardrails

- This file is a review artifact.
- It does not create a GitHub issue by itself.
- The GitHub command template must be copied and executed manually only after approval.
- No production automation is enabled by this issue.
- No client-facing claim is authorized by this issue.
"""

def command_template(issue: Dict[str, Any], filename: str) -> str:
    labels = ",".join(issue.get("labels", []))
    title = issue["title"].replace('"', '\\"')
    return f'gh issue create --title "{title}" --body-file "{filename}" --label "{labels}"'

def build(repo: Path, promote_approved_only: bool) -> Dict[str, Any]:
    selected = selected_issues(repo)
    decisions = decision_map(repo)
    manifest = load_or_create_manifest(repo, selected)
    approved_ids = set(manifest.get("approved_issue_ids", []))
    if promote_approved_only:
        promote = [i for i in selected if i["issue_id"] in approved_ids]
    else:
        promote = selected

    issue_dir = repo / "outputs/prod341_360_issue_markdown"
    commands = []
    issue_files = []
    for idx, issue in enumerate(promote, 1):
        filename = f"{idx:03d}_{slug(issue['issue_id'])}.md"
        rel_path = f"outputs/prod341_360_issue_markdown/{filename}"
        path = repo / rel_path
        md = issue_markdown(issue, decisions.get(issue["issue_id"], {}))
        write_text(path, md)
        issue_files.append({
            "issue_id": issue["issue_id"],
            "path": rel_path,
            "priority": issue.get("priority"),
            "source_delta": issue.get("source_delta"),
            "review_route": issue.get("review_route"),
            "approved": issue["issue_id"] in approved_ids,
        })
        commands.append({
            "issue_id": issue["issue_id"],
            "command": command_template(issue, rel_path),
            "manual_only": True,
            "approved": issue["issue_id"] in approved_ids,
        })

    promotion = {
        "status": "PASS",
        "mode": "approved_only" if promote_approved_only else "review_template_all_selected",
        "selected_count": len(selected),
        "approved_count": len(approved_ids),
        "promoted_template_count": len(promote),
        "issue_files": issue_files,
        "command_templates": commands,
        "auto_created_count": 0,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    policy = {
        "status": "PASS",
        "manual_promotion_policy": [
            "No issue is created automatically.",
            "Approval manifest starts empty by default.",
            "Issue markdown can be reviewed before command execution.",
            "Commands are manual templates only.",
            "Production automation and client-facing claims remain blocked.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    out = repo / "outputs"
    write_json(out / "prod341_360_approved_issue_manifest_snapshot.json", manifest)
    write_json(out / "prod341_360_manual_issue_promotion.json", promotion)
    write_json(out / "prod341_360_manual_promotion_policy.json", policy)

    commands_md = [
        "# PROD-341..360 Manual GitHub Issue Command Templates",
        "",
        "These commands are manual-only templates. Do not execute unless the corresponding issue candidate is approved.",
        "",
    ]
    for row in commands:
        commands_md.append(f"## {row['issue_id']}")
        commands_md.append(f"- Approved in manifest: `{row['approved']}`")
        commands_md.append("")
        commands_md.append("```bash")
        commands_md.append(row["command"])
        commands_md.append("```")
        commands_md.append("")
    write_text(out / "prod341_360_gh_issue_command_templates.md", "\n".join(commands_md))

    pack_md = [
        "# PROD-341..360 Manual Issue Promotion Pack",
        "",
        f"- Status: `{promotion['status']}`",
        f"- Mode: `{promotion['mode']}`",
        f"- Selected candidates: `{promotion['selected_count']}`",
        f"- Approved in manifest: `{promotion['approved_count']}`",
        f"- Generated issue markdown files: `{len(issue_files)}`",
        f"- Auto-created issues: `{promotion['auto_created_count']}`",
        "",
        "## Issue Files",
    ]
    for item in issue_files:
        pack_md.append(f"- `{item['issue_id']}` → `{item['path']}` approved `{item['approved']}`")
    pack_md += ["", "## Policy"]
    for rule in policy["manual_promotion_policy"]:
        pack_md.append(f"- {rule}")
    write_text(out / "prod341_360_manual_issue_promotion.md", "\n".join(pack_md) + "\n")

    return promotion

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--all-selected", action="store_true", help="Generate templates for all selected issues, not only approved manifest entries.")
    args = parser.parse_args()
    result = build(Path(args.repo), promote_approved_only=not args.all_selected)
    print(json.dumps({
        "status": result["status"],
        "mode": result["mode"],
        "selected_count": result["selected_count"],
        "approved_count": result["approved_count"],
        "promoted_template_count": result["promoted_template_count"],
        "auto_created_count": result["auto_created_count"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
