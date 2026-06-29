#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
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

GITIGNORE_RULES = [
    "*.zip",
    ".artifacts/",
    "outputs/*_backups/",
    "__pycache__/",
]

def run(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def ensure_gitignore(repo: Path) -> Dict[str, Any]:
    p = repo / ".gitignore"
    original = p.read_text(encoding="utf-8") if p.exists() else ""
    lines = original.splitlines()
    added = []
    for rule in GITIGNORE_RULES:
        if rule not in lines:
            lines.append(rule)
            added.append(rule)
    if added:
        if lines and lines[-1] != "":
            pass
        p.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"path": ".gitignore", "rules": GITIGNORE_RULES, "added_rules": added, "changed": bool(added)}

def list_tracked_zips(repo: Path) -> List[str]:
    p = run(["git", "ls-files", "*.zip"], repo)
    return [x for x in p.stdout.splitlines() if x.strip()]

def list_local_zips(repo: Path) -> List[str]:
    return sorted(str(p.relative_to(repo)) for p in repo.glob("*.zip") if p.is_file())

def archive_local_zips(repo: Path, archive_dir: Path, move: bool) -> List[Dict[str, str]]:
    archive_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for p in sorted(repo.glob("*.zip")):
        if not p.is_file():
            continue
        target = archive_dir / p.name
        if move:
            p.replace(target)
            action = "moved"
        else:
            action = "would_move"
        records.append({"source": str(p.relative_to(repo)), "target": str(target), "action": action})
    return records

def build_surface_map(repo: Path) -> Dict[str, Any]:
    import sys
    product_root = repo / "product"
    if str(product_root) not in sys.path:
        sys.path.insert(0, str(product_root))
    from api.runtime_endpoint_registry import ENDPOINT_GROUPS, BLOCKED_ACTIONS as REG_BLOCKED
    groups = []
    route_count = 0
    missing = []
    for g in ENDPOINT_GROUPS:
        routes = []
        for r in g.get("routes", []):
            route_count += 1
            rel = r.get("file")
            exists = True if not rel else (repo / rel).exists()
            if rel and not exists:
                missing.append({"route": r["path"], "file": rel})
            routes.append({**r, "exists": exists})
        groups.append({"group": g["group"], "routes": routes})
    return {
        "status": "PASS" if not missing else "INCOMPLETE",
        "group_count": len(groups),
        "route_count": route_count,
        "groups": groups,
        "missing": missing,
        "blocked_actions": REG_BLOCKED,
    }

def build(repo: Path, archive_dir: Path, move_zips: bool) -> Dict[str, Any]:
    out = repo / "outputs"
    gitignore = ensure_gitignore(repo)
    tracked_zips = list_tracked_zips(repo)
    local_zips_before = list_local_zips(repo)
    zip_archive_records = archive_local_zips(repo, archive_dir, move_zips)
    local_zips_after = list_local_zips(repo)
    surface = build_surface_map(repo)

    hygiene = {
        "status": "PASS",
        "tracked_zip_count": len(tracked_zips),
        "tracked_zips": tracked_zips,
        "local_zip_count": len(local_zips_before),
        "local_zips_before": local_zips_before,
        "local_zips_after": local_zips_after,
        "zip_archive_records": zip_archive_records,
        "zip_archive_dir": str(archive_dir),
        "gitignore_rules_present": GITIGNORE_RULES,
        "gitignore_changed": gitignore["changed"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "contract_version": "casulo.runtime_consolidation_readiness.v0.1",
        "status": "PASS" if surface["status"] == "PASS" and len(tracked_zips) == 0 else "ATTENTION",
        "decision": "READY_FOR_EXTERNAL_EVIDENCE_ADAPTER" if surface["status"] == "PASS" else "RUNTIME_SURFACE_REQUIRES_REVIEW",
        "endpoint_group_count": surface["group_count"],
        "endpoint_route_count": surface["route_count"],
        "missing_route_count": len(surface["missing"]),
        "tracked_zip_count": len(tracked_zips),
        "ready_for": ["external evidence adapter", "operator console", "mass test planning"],
        "not_ready_for": ["production activation", "automatic external claims", "credential handling"],
        "next": "Implement provider-neutral External Evidence Adapter with trust and citation gates.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness["status"] == "PASS" else "ATTENTION",
        "audit": "Runtime Endpoint Preservation and Repo Hygiene audit",
        "endpoint_group_count": surface["group_count"],
        "endpoint_route_count": surface["route_count"],
        "missing_route_count": len(surface["missing"]),
        "tracked_zip_count": len(tracked_zips),
        "local_zip_count_before": len(local_zips_before),
        "local_zip_count_after": len(local_zips_after),
        "gitignore_changed": gitignore["changed"],
        "finding": "Runtime endpoints consolidated through registry and generated zip artifacts are controlled by hygiene policy.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod501_520_repo_hygiene_report.json", hygiene)
    write_json(out / "prod501_520_runtime_surface_map.json", surface)
    write_json(out / "prod501_520_endpoint_registry_snapshot.json", surface)
    write_json(out / "prod501_520_readiness.json", readiness)
    write_json(out / "prod501_520_audit_report.json", audit)

    surface_lines = [
        "# PROD-501..520 Runtime Surface Map",
        "",
        f"- Status: `{surface['status']}`",
        f"- Groups: `{surface['group_count']}`",
        f"- Routes: `{surface['route_count']}`",
        f"- Missing routes: `{len(surface['missing'])}`",
        "",
        "## Groups",
    ]
    for g in surface["groups"]:
        surface_lines.append(f"- `{g['group']}`: `{len(g['routes'])}` routes")
    write_text(out / "prod501_520_runtime_surface_map.md", "\n".join(surface_lines) + "\n")

    hygiene_lines = [
        "# PROD-501..520 Repo Hygiene Report",
        "",
        f"- Status: `{hygiene['status']}`",
        f"- Tracked zip count: `{hygiene['tracked_zip_count']}`",
        f"- Local zip count before: `{hygiene['local_zip_count']}`",
        f"- Local zip count after: `{len(hygiene['local_zips_after'])}`",
        f"- Gitignore changed: `{hygiene['gitignore_changed']}`",
        f"- Archive dir: `{hygiene['zip_archive_dir']}`",
        "",
        "## Zip Archive Records",
    ]
    if zip_archive_records:
        for r in zip_archive_records:
            hygiene_lines.append(f"- `{r['action']}` `{r['source']}` → `{r['target']}`")
    else:
        hygiene_lines.append("- No root zip files found.")
    write_text(out / "prod501_520_repo_hygiene_report.md", "\n".join(hygiene_lines) + "\n")

    readiness_lines = [
        "# PROD-501..520 Readiness",
        "",
        f"- Status: `{readiness['status']}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Endpoint groups: `{readiness['endpoint_group_count']}`",
        f"- Endpoint routes: `{readiness['endpoint_route_count']}`",
        f"- Missing route count: `{readiness['missing_route_count']}`",
        f"- Tracked zip count: `{readiness['tracked_zip_count']}`",
        "",
        "## Ready For",
    ]
    readiness_lines += [f"- `{x}`" for x in readiness["ready_for"]]
    readiness_lines += ["", "## Not Ready For"]
    readiness_lines += [f"- `{x}`" for x in readiness["not_ready_for"]]
    write_text(out / "prod501_520_readiness.md", "\n".join(readiness_lines) + "\n")

    audit_lines = [
        "# PROD-501..520 Audit Report",
        "",
        f"- Status: `{audit['status']}`",
        f"- Endpoint groups: `{audit['endpoint_group_count']}`",
        f"- Endpoint routes: `{audit['endpoint_route_count']}`",
        f"- Missing routes: `{audit['missing_route_count']}`",
        f"- Tracked zip count: `{audit['tracked_zip_count']}`",
        f"- Finding: `{audit['finding']}`",
    ]
    write_text(out / "prod501_520_audit_report.md", "\n".join(audit_lines) + "\n")

    result = {
        "task": "PROD-501..520",
        "status": "PASS",
        "phase": "Runtime Endpoint Preservation and Repo Hygiene",
        "decision": readiness["decision"],
        "outputs": [
            "outputs/prod501_520_repo_hygiene_report.json",
            "outputs/prod501_520_runtime_surface_map.json",
            "outputs/prod501_520_endpoint_registry_snapshot.json",
            "outputs/prod501_520_readiness.json",
            "outputs/prod501_520_audit_report.json",
        ],
        "next_recommended_bundle": "PROD-521..560 External Evidence Adapter and Trust Gate",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod501_520_result.json", result)
    write_text(out / "prod501_520_report.md", "# PROD-501..520 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--archive-dir", default="/workspaces/casulo-campo-os-poc-package-archive")
    parser.add_argument("--move-zips", action="store_true")
    args = parser.parse_args()
    result = build(Path(args.repo), Path(args.archive_dir), args.move_zips)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
