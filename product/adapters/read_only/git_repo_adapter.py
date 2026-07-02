#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BLOCKED_ACTIONS = [
    "automatic_merge",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_activation",
    "client_facing_validated_claim",
    "commercial_claim",
]

def run_git(args, timeout=10):
    try:
        cp = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "ok": cp.returncode == 0,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "command": "git " + " ".join(args),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": "git " + " ".join(args)}

def git_repo_status():
    return {
        "adapter": "git_repo_adapter.v0.1",
        "mode": "LOCAL_GIT_READ_ONLY",
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "head_full": run_git(["rev-parse", "HEAD"]),
        "branch": run_git(["branch", "--show-current"]),
        "status_short": run_git(["status", "--short"]),
        "last_commit": run_git(["log", "--oneline", "-1"]),
        "recent_commits": run_git(["log", "--oneline", "-20"]),
        "tags_at_head": run_git(["tag", "--points-at", "HEAD"]),
        "remote": run_git(["remote", "-v"]),
        "writes_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def git_repo_timeline(limit=80):
    raw = run_git(["log", "--date=iso", "--pretty=format:%h%x09%H%x09%ad%x09%s", "-n", str(limit)])
    commits = []
    if raw.get("ok"):
        for line in raw.get("stdout", "").splitlines():
            parts = line.split("\t", 3)
            if len(parts) == 4:
                commits.append({"short": parts[0], "sha": parts[1], "date": parts[2], "message": parts[3]})
    return {
        "adapter": "git_repo_adapter.v0.1",
        "mode": "LOCAL_GIT_READ_ONLY",
        "limit": limit,
        "count": len(commits),
        "commits": commits,
        "writes_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

if __name__ == "__main__":
    print(json.dumps(git_repo_status(), indent=2, ensure_ascii=False))
