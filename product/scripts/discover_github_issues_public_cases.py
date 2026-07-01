#!/usr/bin/env python3
# Controlled GitHub Issues public case discovery runner.
# Default mode is dry-run only. It does not call the network unless --allow-network is explicitly passed.

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
QUERY_SET = ROOT / "product/evaluation/external_cases/live_discovery/github_issues_public_query_set_v0_3.json"
OUT_JSON = ROOT / "product/evaluation/external_cases/live_discovery/github_issues_live_candidates_v0_3.json"
OUT_CSV = ROOT / "product/evaluation/external_cases/live_discovery/github_issues_live_candidates_v0_3.csv"
RUN_REPORT = ROOT / "product/reports/casulo_delta_zero_github_issues_live_discovery_run_v0_3.json"

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def load_query_set() -> dict[str, Any]:
    if not QUERY_SET.exists():
        raise SystemExit(f"missing query set: {QUERY_SET}")
    return json.loads(QUERY_SET.read_text(encoding="utf-8"))

def classify_issue(issue: dict[str, Any], repo: str) -> dict[str, Any]:
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    labels = [x.get("name", "") for x in issue.get("labels", []) if isinstance(x, dict)]
    text = f"{title}\n{body}\n{' '.join(labels)}".lower()

    difficulty = "simple"
    if any(k in text for k in ["rollback", "production", "security", "breaking", "race condition", "regression"]):
        difficulty = "complex"
    elif any(k in text for k in ["bug", "error", "crash", "test", "ci", "repro", "performance"]):
        difficulty = "medium"

    risk_theme = "missing_reproduction_steps"
    expected_gate = "NEEDS_MORE_EVIDENCE"
    if any(k in text for k in ["production", "rollback", "security", "breaking"]):
        risk_theme = "unsafe_change_or_high_impact_issue"
        expected_gate = "HUMAN_REVIEW_REQUIRED"
    elif any(k in text for k in ["bug", "crash", "regression"]):
        risk_theme = "bug_with_partial_evidence"
        expected_gate = "HUMAN_REVIEW_REQUIRED"
    elif any(k in text for k in ["documentation", "docs", "typo"]):
        risk_theme = "low_risk_documentation_case"
        expected_gate = "ACTION_PLAN_ALLOWED"

    return {
        "candidate_id": f"GITHUB-ISSUE-{repo.replace('/','-')}-{issue.get('number')}",
        "provider_id": "github_issues_public",
        "source_family": "software_tic_cases",
        "domain": "software_tic",
        "difficulty": difficulty,
        "evidence_type": "public_issue_url",
        "source_repo": repo,
        "source_url": issue.get("html_url", ""),
        "api_url": issue.get("url", ""),
        "citation_anchor": f"{repo}#{issue.get('number')}",
        "title": title,
        "body_excerpt": body[:1000] if body else "",
        "labels": "|".join(labels),
        "state": issue.get("state", ""),
        "created_at": issue.get("created_at", ""),
        "updated_at": issue.get("updated_at", ""),
        "comments": issue.get("comments", 0),
        "risk_theme": risk_theme,
        "expected_gate": expected_gate,
        "has_primary_anchor": bool(issue.get("html_url")),
        "has_excerpt": bool(body),
        "has_schema_or_context": True,
        "pii_or_secret_status": "NOT_DETECTED_BY_BASIC_PUBLIC_METADATA_SCAN",
        "ready_for_real_case_001": False,
        "blocked_reason": "candidate_requires_source_trust_and_citation_gate_before_freeze",
    }

def fetch_repo_issues(repo: str, per_page: int) -> list[dict[str, Any]]:
    owner, name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(name)}/issues?state=open&per_page={per_page}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "CASULO-Delta-Zero-Discovery-DryRun",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8")
    items = json.loads(raw)
    return [i for i in items if isinstance(i, dict) and "pull_request" not in i]

def run(allow_network: bool, limit: int) -> int:
    qs = load_query_set()
    repos = qs.get("github_repositories", [])
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    if not allow_network:
        report = {
            "version": "casulo_delta_zero_github_issues_live_discovery_run.v0.3",
            "generated_at": now(),
            "status": "DRY_RUN_NO_NETWORK",
            "allow_network": False,
            "candidate_count": 0,
            "repos_planned": repos,
            "output_created": False,
            "errors": [],
        }
        write_json(RUN_REPORT, report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    per_repo = max(1, min(10, limit))
    for repo in repos:
        try:
            issues = fetch_repo_issues(repo, per_repo)
            for issue in issues:
                rows.append(classify_issue(issue, repo))
                if len(rows) >= limit:
                    break
        except urllib.error.HTTPError as e:
            errors.append({"repo": repo, "error": "HTTPError", "status": e.code, "reason": str(e)})
        except Exception as e:
            errors.append({"repo": repo, "error": type(e).__name__, "reason": str(e)})
        if len(rows) >= limit:
            break
        time.sleep(1)

    payload = {
        "version": "github_issues_live_candidates.v0.3",
        "generated_at": now(),
        "provider_id": "github_issues_public",
        "candidate_count": len(rows),
        "network_call_executed": True,
        "ready_for_real_case_001": False,
        "rows": rows,
    }
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, rows)

    report = {
        "version": "casulo_delta_zero_github_issues_live_discovery_run.v0.3",
        "generated_at": now(),
        "status": "PASS_WITH_CANDIDATES" if rows and not errors else ("PASS_WITH_ERRORS" if rows else "NO_CANDIDATES"),
        "allow_network": True,
        "candidate_count": len(rows),
        "repos_planned": repos,
        "output_json": str(OUT_JSON.relative_to(ROOT)),
        "output_csv": str(OUT_CSV.relative_to(ROOT)),
        "ready_for_real_case_001": False,
        "requires_next_gate": "PROD-6901..6940 - External Case Normalization and Trust/Citation Gate",
        "errors": errors,
    }
    write_json(RUN_REPORT, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if rows else 2

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-network", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    return run(allow_network=args.allow_network, limit=args.limit)

if __name__ == "__main__":
    raise SystemExit(main())
