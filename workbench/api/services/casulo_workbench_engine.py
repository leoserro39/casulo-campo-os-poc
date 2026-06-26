"""CASULO Workbench v0.2 runtime-hardened engine.

Hardening goals:
- check mode can compute all artifacts without writing files
- write mode is explicit
- contracts can be validated before the Cubo/Cupula consumes state
- generated artifacts are grouped by case and can be redirected to runtime output dirs
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
OUTPUTS = ROOT / "outputs"
DEFAULT_STABLE_TS = "1970-01-01T00:00:00+00:00"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def load_case(case_name: str) -> Dict[str, Any]:
    path = EXAMPLES / case_name / "case.json"
    if not path.exists():
        raise FileNotFoundError(f"case not found: {case_name} ({path})")
    return json.loads(path.read_text(encoding="utf-8"))


def list_case_names() -> List[str]:
    if not EXAMPLES.exists():
        return []
    return [path.name for path in sorted(EXAMPLES.iterdir()) if (path / "case.json").exists()]


def source_quality(source: Dict[str, Any]) -> float:
    metrics = [
        source.get("completeness", 0.0),
        source.get("freshness", 0.0),
        source.get("consistency", 0.0),
        source.get("traceability", 0.0),
        source.get("trust", 0.0),
    ]
    base = mean(float(x) for x in metrics)
    sensitivity = float(source.get("sensitivity", 0.0))
    penalty = min(0.20, sensitivity * 0.10)
    return round(max(0.0, min(1.0, base - penalty)), 3)


def quality_label(score: float) -> str:
    if score < 0.31:
        return "LOW"
    if score < 0.61:
        return "CONTROLLED"
    if score < 0.81:
        return "ACCEPTABLE"
    return "HIGH"


def compute_data_quality(case: Dict[str, Any]) -> Dict[str, Any]:
    items = []
    for source in case["sources"]:
        score = source_quality(source)
        items.append({
            "source_id": source["id"],
            "name": source["name"],
            "type": source["type"],
            "domains": source.get("domains", []),
            "score": score,
            "label": quality_label(score),
            "use_policy": "USE" if score >= 0.61 else "USE_WITH_CAUTION" if score >= 0.31 else "NEED_CONFIRMATION",
        })
    overall = round(mean([item["score"] for item in items]), 3) if items else 0.0
    return {"overall_score": overall, "overall_label": quality_label(overall), "sources": items}


def compute_domain_scores(case: Dict[str, Any], dq: Dict[str, Any]) -> List[Dict[str, Any]]:
    source_scores = {item["source_id"]: item["score"] for item in dq["sources"]}
    domains = []
    for domain in case["domains"]:
        supporting_sources = [
            src for src in case["sources"] if domain["id"] in src.get("domains", [])
        ]
        scores = [source_scores[src["id"]] for src in supporting_sources]
        quality = round(mean(scores), 3) if scores else 0.0
        risks = domain.get("risks", [])
        risk_factor = min(1.0, len(risks) / 5)
        state_confidence = round(max(0.0, quality - risk_factor * 0.12), 3)
        domains.append({
            "id": domain["id"],
            "name": domain["name"],
            "branches": domain.get("branches", []),
            "risks": risks,
            "supporting_sources": [src["id"] for src in supporting_sources],
            "data_quality": quality,
            "state_confidence": state_confidence,
        })
    return domains


def build_graph(case: Dict[str, Any], domains: List[Dict[str, Any]], dq: Dict[str, Any]) -> Dict[str, Any]:
    nodes = [{"id": case["case_id"], "type": "Case", "label": case["title"]}]
    edges = []

    for domain in domains:
        nodes.append({"id": domain["id"], "type": "Domain", "label": domain["name"], "state_confidence": domain["state_confidence"]})
        edges.append({"source": case["case_id"], "target": domain["id"], "type": "HAS_DOMAIN"})
        for branch in domain.get("branches", []):
            branch_id = f"{domain['id']}::{slug(branch)}"
            nodes.append({"id": branch_id, "type": "ComputableBranch", "label": branch})
            edges.append({"source": domain["id"], "target": branch_id, "type": "HAS_BRANCH"})

    for source in case["sources"]:
        nodes.append({"id": source["id"], "type": "Source", "label": source["name"]})
        for domain_id in source.get("domains", []):
            edges.append({"source": domain_id, "target": source["id"], "type": "CONSUMES_SOURCE"})

    for inter in case.get("intersections", []):
        nodes.append({"id": inter["id"], "type": "Intersection", "label": inter["description"], "impact": inter.get("impact", "medium")})
        d1, d2 = inter["domains"]
        edges.append({"source": d1, "target": inter["id"], "type": "INTERSECTS_WITH"})
        edges.append({"source": d2, "target": inter["id"], "type": "INTERSECTS_WITH"})
        if inter.get("delta_id"):
            edges.append({"source": inter["id"], "target": inter["delta_id"], "type": "GENERATES_DELTA"})

    for delta in case.get("deltas", []):
        nodes.append({"id": delta["id"], "type": "Delta", "label": delta["title"]})
        gate_id = f"gate::{delta['id']}"
        nodes.append({"id": gate_id, "type": "Gate", "label": delta.get("gate_hint", "PREPARE")})
        edges.append({"source": delta["id"], "target": gate_id, "type": "HAS_GATE"})

    return {"nodes": nodes, "edges": edges, "data_quality": dq}


def compute_fragility(case: Dict[str, Any], domains: List[Dict[str, Any]], dq: Dict[str, Any]) -> Dict[str, Any]:
    avg_conf = round(mean([d["state_confidence"] for d in domains]), 3) if domains else 0.0
    contradiction_count = len([i for i in case.get("intersections", []) if i.get("impact") == "high"])
    missing_ratio = round(len([d for d in domains if d["data_quality"] < 0.61]) / max(1, len(domains)), 3)
    sync_coverage = round(len(case.get("intersections", [])) / max(1, len(domains)), 3)
    raw_risk = (1 - dq["overall_score"]) * 0.35 + missing_ratio * 0.25 + min(1, contradiction_count / 4) * 0.20 + (1 - min(1, sync_coverage)) * 0.20
    h_pre = round(max(0.0, min(1.0, raw_risk)), 3)
    h_post = round(max(0.0, h_pre - 0.12), 3)
    state_confidence = round(max(0.0, min(1.0, (avg_conf + dq["overall_score"]) / 2)), 3)
    if h_pre <= 0.30 and dq["overall_score"] >= 0.61:
        decision = "ALLOW_SOLUTION"
    elif h_pre <= 0.50:
        decision = "RECOMMEND_SMALLER_DELTA"
    elif h_pre <= 0.70:
        decision = "NEED_MORE_EVIDENCE"
    else:
        decision = "HUMAN_REVIEW_REQUIRED"
    return {
        "h_pre": h_pre,
        "h_post": h_post,
        "delta_l": round(h_pre - h_post, 3),
        "missing_ratio": missing_ratio,
        "contradiction_count": contradiction_count,
        "sync_coverage": sync_coverage,
        "state_confidence": state_confidence,
        "decision": decision,
    }


def compute_gates(case: Dict[str, Any], fragility: Dict[str, Any], dq: Dict[str, Any]) -> List[Dict[str, Any]]:
    gates = []
    for delta in case.get("deltas", []):
        hint = delta.get("gate_hint", "PREPARE")
        if fragility["decision"] == "ALLOW_SOLUTION" and dq["overall_score"] >= 0.61:
            status = hint if hint in {"DO_NOW", "PREPARE", "MEASURE_FIRST"} else "PREPARE"
        elif fragility["decision"] == "RECOMMEND_SMALLER_DELTA":
            status = "PREPARE" if hint == "DO_NOW" else hint
        else:
            status = "MEASURE_FIRST" if hint != "BLOCK" else "BLOCK"
        gates.append({
            "delta_id": delta["id"],
            "delta_title": delta["title"],
            "gate_status": status,
            "solution_package": delta.get("solution_package", "to_define"),
            "expected_metric": delta.get("expected_metric", "state improvement"),
        })
    return gates


def ledger_events(case: Dict[str, Any], dq: Dict[str, Any], fragility: Dict[str, Any], gates: List[Dict[str, Any]], generated_at: str) -> List[Dict[str, Any]]:
    return [
        {"ts": generated_at, "event": "CASE_LOADED", "case_id": case["case_id"]},
        {"ts": generated_at, "event": "DATA_QUALITY_COMPUTED", "score": dq["overall_score"], "label": dq["overall_label"]},
        {"ts": generated_at, "event": "FRAGILITY_COMPUTED", "h_pre": fragility["h_pre"], "decision": fragility["decision"]},
        {"ts": generated_at, "event": "GATES_COMPUTED", "count": len(gates)},
        {"ts": generated_at, "event": "SNAPSHOT_READY", "case_id": case["case_id"]},
    ]


def report_markdown(case: Dict[str, Any], dq: Dict[str, Any], domains: List[Dict[str, Any]], fragility: Dict[str, Any], gates: List[Dict[str, Any]]) -> str:
    lines = [
        f"# CASULO Workbench Diagnostic Report - {case['title']}",
        "",
        f"- Case ID: `{case['case_id']}`",
        f"- Vertical: `{case.get('vertical', 'unknown')}`",
        f"- Objective: {case.get('objective', 'not defined')}",
        "",
        "## Data Quality",
        f"- Overall: `{dq['overall_score']}` (`{dq['overall_label']}`)",
        "",
        "## Operational Fragility",
        f"- H_pre: `{fragility['h_pre']}`",
        f"- H_post: `{fragility['h_post']}`",
        f"- Delta_L: `{fragility['delta_l']}`",
        f"- Decision: `{fragility['decision']}`",
        "",
        "## Domains",
    ]
    for d in domains:
        lines.append(f"- **{d['name']}** - quality `{d['data_quality']}`, confidence `{d['state_confidence']}`")
    lines += ["", "## Gates"]
    for gate in gates:
        lines.append(f"- `{gate['gate_status']}` - {gate['delta_title']} -> {gate['solution_package']}")
    return "\n".join(lines) + "\n"


def codex_task_markdown(case: Dict[str, Any], gates: List[Dict[str, Any]], fragility: Dict[str, Any]) -> str:
    actionable = [g for g in gates if g["gate_status"] in {"DO_NOW", "PREPARE", "MEASURE_FIRST"}]
    lines = [
        f"# Codex Executor Task - {case['title']}",
        "",
        f"Case ID: `{case['case_id']}`",
        f"Fragility decision: `{fragility['decision']}`",
        "",
        "## Scope",
        "Implement only solution packages derived from CASULO gates.",
        "",
        "## Candidate packages",
    ]
    for gate in actionable:
        lines.append(f"- Gate `{gate['gate_status']}`: {gate['delta_title']} -> `{gate['solution_package']}`")
    lines += [
        "",
        "## Constraints",
        "- Do not make business/legal decisions.",
        "- Do not use sensitive data without explicit approval.",
        "- Preserve CASULO state artifacts and validation.",
    ]
    return "\n".join(lines) + "\n"


def build_case_artifacts(case_name: str, generated_at: Optional[str] = None) -> Dict[str, Any]:
    ts = generated_at or utc_now()
    case = load_case(case_name)
    dq = compute_data_quality(case)
    domains = compute_domain_scores(case, dq)
    graph = build_graph(case, domains, dq)
    fragility = compute_fragility(case, domains, dq)
    gates = compute_gates(case, fragility, dq)
    events = ledger_events(case, dq, fragility, gates, ts)
    snapshot = {
        "contract_version": "workbench.state_snapshot.v0.2",
        "generated_at": ts,
        "case": {"case_id": case["case_id"], "title": case["title"], "vertical": case.get("vertical")},
        "data_quality": dq,
        "domains": domains,
        "fragility": fragility,
        "gates": gates,
    }
    return {
        "case_name": case_name,
        "case": case,
        "data_quality": dq,
        "domains": domains,
        "graph": graph,
        "fragility": fragility,
        "gates": gates,
        "ledger_events": events,
        "state_snapshot": snapshot,
        "diagnostic_report": report_markdown(case, dq, domains, fragility, gates),
        "codex_task": codex_task_markdown(case, gates, fragility),
    }


def summarize_artifacts(artifacts: Dict[str, Any], output_path: Optional[Path] = None) -> Dict[str, Any]:
    case = artifacts["case"]
    dq = artifacts["data_quality"]
    fragility = artifacts["fragility"]
    gates = artifacts["gates"]
    result = {
        "case_name": artifacts["case_name"],
        "case_id": case["case_id"],
        "data_quality": dq["overall_score"],
        "fragility": fragility["h_pre"],
        "decision": fragility["decision"],
        "gates": len(gates),
    }
    if output_path is not None:
        result["outputs"] = str(output_path)
    return result


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_case_artifacts(artifacts: Dict[str, Any], output_root: Path = OUTPUTS) -> Path:
    case_out = output_root / artifacts["case_name"]
    case_out.mkdir(parents=True, exist_ok=True)
    write_json(case_out / "state_snapshot.json", artifacts["state_snapshot"])
    write_json(case_out / "graph.json", artifacts["graph"])
    (case_out / "ledger.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in artifacts["ledger_events"]) + "\n",
        encoding="utf-8",
    )
    (case_out / "diagnostic_report.md").write_text(artifacts["diagnostic_report"], encoding="utf-8")
    (case_out / "codex_task.md").write_text(artifacts["codex_task"], encoding="utf-8")
    return case_out


def run_case(case_name: str, write: bool = False, output_root: Path = OUTPUTS, stable_time: bool = False) -> Dict[str, Any]:
    generated_at = DEFAULT_STABLE_TS if stable_time else None
    artifacts = build_case_artifacts(case_name, generated_at=generated_at)
    output_path = write_case_artifacts(artifacts, output_root=output_root) if write else None
    return summarize_artifacts(artifacts, output_path=output_path)


def run_all_cases(write: bool = False, output_root: Path = OUTPUTS, stable_time: bool = False) -> List[Dict[str, Any]]:
    return [run_case(name, write=write, output_root=output_root, stable_time=stable_time) for name in list_case_names()]


def export_codex_task(case_name: str, output_dir: Path, stable_time: bool = False) -> Path:
    artifacts = build_case_artifacts(case_name, generated_at=DEFAULT_STABLE_TS if stable_time else None)
    output_dir.mkdir(parents=True, exist_ok=True)
    dst = output_dir / f"{case_name}_codex_task.md"
    dst.write_text(artifacts["codex_task"], encoding="utf-8")
    return dst
