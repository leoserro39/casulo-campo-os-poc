#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
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

PRIORITY_SCORE = {
    "P0_BLOCKER": 100,
    "P1_REVIEW": 80,
    "P2_EVIDENCE_OR_TASK": 60,
    "P3_STRUCTURE": 40,
    "P4_CALIBRATION": 20,
}

DELTA_REVIEW_ROUTE = {
    "delta_production": "production_readiness_owner",
    "delta_domain": "domain_owner",
    "delta_evidence": "evidence_owner",
    "delta_conflict": "human_arbitrator",
    "delta_execution": "technical_reviewer",
    "delta_rule": "rule_owner",
    "delta_human_review": "human_reviewer",
    "delta_missingness": "artifact_owner",
    "delta_graph_structure": "graph_architect",
    "delta_model_behavior": "calibration_owner",
    "delta_ambiguity": "context_owner",
}

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def flatten_issues(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues = []
    for result in results:
        for issue in result.get("issue_candidates", []):
            issue = dict(issue)
            issue["case_title"] = result.get("title", "")
            issue["case_decision"] = result.get("decision", "")
            issue["case_readiness"] = result.get("graph", {}).get("readiness", "")
            issues.append(issue)
    return issues

def delta_from_issue(issue: Dict[str, Any]) -> str:
    for label in issue.get("labels", []):
        if label.startswith("delta-"):
            return label.replace("delta-", "delta_")
    title = issue.get("title", "")
    if "delta_" in title:
        return title.split("delta_", 1)[1].split()[0].strip("`:.")
    return "delta_unknown"

def select_issues(issues: List[Dict[str, Any]], max_selected: int) -> List[Dict[str, Any]]:
    repeated_delta = Counter(delta_from_issue(i) for i in issues)
    enriched = []
    for issue in issues:
        delta = delta_from_issue(issue)
        priority = issue.get("priority", "P4_CALIBRATION")
        score = PRIORITY_SCORE.get(priority, 10) + min(20, repeated_delta[delta] * 2)
        if delta in ["delta_production", "delta_domain", "delta_evidence", "delta_conflict"]:
            score += 10
        enriched_issue = dict(issue)
        enriched_issue["source_delta"] = delta
        enriched_issue["selection_score"] = min(130, score)
        enriched_issue["review_route"] = DELTA_REVIEW_ROUTE.get(delta, "review_owner")
        enriched.append(enriched_issue)
    enriched.sort(key=lambda x: (-x["selection_score"], x["case_id"], x["issue_id"]))
    return enriched[:max_selected]

def make_review_decisions(selected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    decisions = []
    for idx, issue in enumerate(selected, 1):
        priority = issue.get("priority")
        delta = issue.get("source_delta")
        if priority == "P0_BLOCKER":
            rec = "APPROVE_FOR_HUMAN_REVIEW_ISSUE"
        elif priority == "P1_REVIEW":
            rec = "APPROVE_FOR_REVIEW_QUEUE"
        elif delta in ["delta_evidence", "delta_missingness"]:
            rec = "REQUEST_EVIDENCE_OR_ARTIFACT"
        else:
            rec = "KEEP_AS_CANDIDATE_BACKLOG"
        decisions.append({
            "decision_id": f"REVIEW-DECISION-{idx:03d}",
            "issue_id": issue["issue_id"],
            "case_id": issue["case_id"],
            "priority": priority,
            "source_delta": delta,
            "review_route": issue["review_route"],
            "recommended_decision": rec,
            "requires_human_approval": True,
            "auto_created_issue": False,
            "blocked_actions": BLOCKED_ACTIONS,
        })
    return decisions

def group_review(selected: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_priority = defaultdict(list)
    by_delta = defaultdict(list)
    by_case = defaultdict(list)
    by_route = defaultdict(list)
    for issue in selected:
        by_priority[issue["priority"]].append(issue["issue_id"])
        by_delta[issue["source_delta"]].append(issue["issue_id"])
        by_case[issue["case_id"]].append(issue["issue_id"])
        by_route[issue["review_route"]].append(issue["issue_id"])
    return {
        "by_priority": dict(by_priority),
        "by_delta": dict(by_delta),
        "by_case": dict(by_case),
        "by_route": dict(by_route),
    }

def write_console_md(path: Path, console: Dict[str, Any], selected: List[Dict[str, Any]]) -> None:
    lines = [
        "# PROD-321..340 Graph Case Review Console",
        "",
        f"- Status: `{console['status']}`",
        f"- Source cases: `{console['case_count']}`",
        f"- Total available issues: `{console['total_issue_candidates']}`",
        f"- Selected issues: `{console['selected_issue_count']}`",
        f"- Decision: `{console['decision']}`",
        "",
        "## Selected Issues",
    ]
    for issue in selected:
        lines.append(f"- `{issue['issue_id']}` `{issue['priority']}` `{issue['source_delta']}` route `{issue['review_route']}` score `{issue['selection_score']}`")
    lines += ["", "## Review Groups"]
    for group_name, group in console["review_groups"].items():
        lines.append(f"### {group_name}")
        for k, values in group.items():
            lines.append(f"- `{k}`: `{', '.join(values)}`")
    write_md(path, lines)

def write_human_pack(path: Path, selected: List[Dict[str, Any]], decisions: List[Dict[str, Any]]) -> None:
    lines = [
        "# PROD-321..340 Human Review Pack",
        "",
        "This pack is review-only. It does not create GitHub issues, activate production, merge code, or make client-facing claims.",
        "",
        "## Priority Review Queue",
    ]
    decision_by_issue = {d["issue_id"]: d for d in decisions}
    for issue in selected:
        d = decision_by_issue[issue["issue_id"]]
        lines += [
            f"### {issue['issue_id']} — {issue['title']}",
            f"- Case: `{issue['case_id']}`",
            f"- Priority: `{issue['priority']}`",
            f"- Delta: `{issue['source_delta']}`",
            f"- Review route: `{issue['review_route']}`",
            f"- Recommended decision: `{d['recommended_decision']}`",
            f"- Human approval required: `{d['requires_human_approval']}`",
            "",
            "#### Required action",
            issue.get("body", "").split("## Required action", 1)[-1].split("## Acceptance criteria", 1)[0].strip() if "## Required action" in issue.get("body", "") else "Review required.",
            "",
        ]
    write_md(path, lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--max-selected", type=int, default=12)
    args = parser.parse_args()

    repo = Path(args.repo)
    out = repo / "outputs"
    results_path = out / "prod301_320_real_graph_case_results.json"
    aggregate_path = out / "prod301_320_real_graph_case_aggregate.json"
    if not results_path.exists():
        raise SystemExit(f"missing {results_path}")
    results = read_json(results_path).get("results", [])
    aggregate = read_json(aggregate_path) if aggregate_path.exists() else {}
    issues = flatten_issues(results)
    selected = select_issues(issues, args.max_selected)
    decisions = make_review_decisions(selected)
    groups = group_review(selected)

    decision = "READY_FOR_HUMAN_REVIEW_SELECTION"
    if any(i.get("priority") == "P0_BLOCKER" for i in selected):
        decision = "P0_REVIEW_QUEUE_READY_HUMAN_APPROVAL_REQUIRED"

    console = {
        "status": "PASS",
        "console": "casulo.graph_case_review_console.v0.1",
        "case_count": len(results),
        "aggregate_decision": aggregate.get("decision"),
        "total_issue_candidates": len(issues),
        "selected_issue_count": len(selected),
        "review_groups": groups,
        "decision": decision,
        "interpretation": "The review console selected high-priority issue candidates from real/anonymized graph cases and prepared a human approval pack without creating issues automatically.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    selection_policy = {
        "status": "PASS",
        "policy": "CASULO issue selection policy",
        "max_selected": args.max_selected,
        "rules": [
            "Prioritize P0 blockers.",
            "Prefer production/domain/evidence/conflict deltas.",
            "Boost deltas repeated across case outputs.",
            "Do not create GitHub issues automatically.",
            "Require human approval before promoting any candidate.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod321_340_review_console.json", console)
    write_console_md(out / "prod321_340_review_console.md", console, selected)
    write_json(out / "prod321_340_issue_selection.json", {"status": "PASS", "selected_issues": selected, "selection_policy": selection_policy})
    write_json(out / "prod321_340_review_decision_log.json", {"status": "PASS", "review_decisions": decisions})
    write_json(out / "prod321_340_human_review_pack.json", {"status": "PASS", "selected_issues": selected, "review_decisions": decisions})
    write_human_pack(out / "prod321_340_human_review_pack.md", selected, decisions)
    write_json(out / "prod321_340_selection_policy.json", selection_policy)

    csv_path = out / "prod321_340_selected_issues.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fields = ["issue_id", "case_id", "priority", "source_delta", "review_route", "selection_score", "title"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for issue in selected:
            writer.writerow({k: issue.get(k, "") for k in fields})

    print(json.dumps({"status": "PASS", "selected": len(selected), "decision": decision}, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
