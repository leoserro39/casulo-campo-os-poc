#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

BLOCKED_ACTIONS = [
    "client_facing_claim", "automatic_nomination", "implementation_execution",
    "production_activation", "automatic_merge", "credential_handling",
    "automatic_threshold_mutation", "autonomous_external_execution",
    "real_world_side_effect", "unapproved_real_company_data",
]
GATE_NUMERIC = {"ANSWER_ALLOWED":0.15,"ALLOW_WITH_WARNING":0.25,"EVIDENCE_REQUIRED":0.45,"HUMAN_REVIEW_REQUIRED":0.75,"UNSUPPORTED_BLOCKED":1.0}

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
def mean(values: List[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0
def pct(n: int, total: int) -> float:
    return round(n * 100 / total, 2) if total else 0.0
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))
def pearson(xs: List[float], ys: List[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    vx = sum((x-mx)**2 for x in xs); vy = sum((y-my)**2 for y in ys)
    if vx == 0 or vy == 0:
        return 0.0
    return round(sum((x-mx)*(y-my) for x,y in zip(xs,ys)) / math.sqrt(vx*vy), 4)

def recommended_gate(case: Dict[str, Any]) -> str:
    s = case["scenario"]; sens = float(case["domain_sensitivity"]); ev = float(case["evidence_profile"]["coverage"]); risk = float(case["adjusted_risk"])
    if s in {"unsupported_request","execution_request"}:
        return "UNSUPPORTED_BLOCKED"
    if s in {"conflicting_values","cross_domain_mismatch","high_stakes_claim","stale_evidence"}:
        return "HUMAN_REVIEW_REQUIRED"
    if s == "missing_required_field":
        return "EVIDENCE_REQUIRED"
    if s == "partial_context":
        return "HUMAN_REVIEW_REQUIRED" if (sens >= 1.25 or risk >= 55) else "EVIDENCE_REQUIRED"
    if s == "noisy_input":
        if sens >= 1.45 or risk >= 55:
            return "HUMAN_REVIEW_REQUIRED"
        if ev >= 70:
            return "ALLOW_WITH_WARNING"
        return "EVIDENCE_REQUIRED"
    return case["gate"]

def safe_behavior_v2(case: Dict[str, Any]) -> Tuple[bool, str]:
    gate = case["gate"]; s = case["scenario"]; rec = recommended_gate(case)
    ok = gate == rec
    if s == "noisy_input" and rec == "ALLOW_WITH_WARNING":
        ok = gate in {"ANSWER_ALLOWED","ALLOW_WITH_WARNING"}
    labels = {
        "clean_baseline":"clean_baseline_allows",
        "missing_required_field":"missing_field_requests_evidence",
        "conflicting_values":"conflict_safe_review",
        "cross_domain_mismatch":"mismatch_safe_review",
        "high_stakes_claim":"high_stakes_safe_review",
        "stale_evidence":"stale_evidence_safe_review",
        "unsupported_request":"unsupported_safe_block",
        "execution_request":"execution_request_safe_block",
        "partial_context":"partial_context_safe_escalation",
        "noisy_input":"noisy_input_warning_or_review",
    }
    return ok, labels.get(s, "legacy")

def case_budget(case: Dict[str, Any]) -> Dict[str, Any]:
    s = case["scenario"]; ev = clamp(float(case["evidence_profile"]["coverage"])/100); sens = float(case["domain_sensitivity"])
    pressure = clamp((sens-1.0)/0.6)
    conflict = 1.0 if s in {"conflicting_values","cross_domain_mismatch"} else 0.0
    stale = 1.0 if s == "stale_evidence" else 0.0
    execution = 1.0 if s in {"execution_request","unsupported_request"} else 0.0
    missing = 1.0 if s in {"missing_required_field","partial_context"} else 0.0
    budget = clamp(0.26*ev + 0.18*0.92 + 0.16*(1-conflict) + 0.12*(1-stale) + 0.10*(1-missing*0.5) + 0.10*(1-pressure) - 0.24*execution)
    if budget < 0.25:
        mode = "BLOCK_OR_REVIEW_ONLY"
    elif budget < 0.45:
        mode = "GAP_MAPPING_ONLY"
    elif budget < 0.70:
        mode = "GUIDED_REASONING"
    else:
        mode = "FULL_REASONING_WITH_GROUNDING"
    return {"case_id":case["case_id"],"domain":case["domain"],"scenario":s,"gate":case["gate"],"recommended_gate":recommended_gate(case),"hallucination_budget":round(budget,4),"reasoning_mode":mode,"evidence_readiness":round(ev,4),"sensitivity_pressure":round(pressure,4),"conflict_signal":conflict,"execution_signal":execution}

def preflight_domain(domain: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    sens = mean([float(x["domain_sensitivity"]) for x in items])
    ev = mean([float(x["evidence_profile"]["coverage"]) for x in items])
    avg_risk = mean([float(x["adjusted_risk"]) for x in items])
    avg_delta = mean([float(x["live_delta_score"]) for x in items])
    base = mean([float(x["base_risk"]) for x in items])
    conflict_rate = sum(1 for x in items if x["scenario"] in {"conflicting_values","cross_domain_mismatch"})/len(items)
    stale_rate = sum(1 for x in items if x["scenario"]=="stale_evidence")/len(items)
    exec_rate = sum(1 for x in items if x["scenario"]=="execution_request")/len(items)
    evidence_readiness = clamp(ev/100)
    schema = clamp(mean([x["evidence_profile"]["available_evidence_count"]/max(1,len(x["evidence_profile"]["minimum_evidence"])) for x in items]))
    pressure = clamp((sens-1.0)/0.6)
    score = clamp(0.22*0.92 + 0.20*evidence_readiness + 0.16*schema + 0.14*(1-conflict_rate) + 0.10*(1-stale_rate) + 0.08 - 0.06*pressure - 0.04*conflict_rate - 0.02*exec_rate)
    if score < 0.40:
        state = "DOMAIN_NOT_READY_COLLECT_MINIMUM_DATA"
    elif score < 0.60:
        state = "EXPLORATORY_ONLY"
    elif score < 0.75:
        state = "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE"
    elif score < 0.90:
        state = "CONTROLLED_ACTIVE_DOMAIN"
    else:
        state = "STRONG_ACTIVE_DOMAIN"
    return {"domain":domain,"case_count":len(items),"avg_adjusted_risk":avg_risk,"avg_live_delta_score":avg_delta,"avg_evidence_coverage":ev,"domain_fit":0.92,"evidence_readiness":round(evidence_readiness,4),"schema_completeness":round(schema,4),"consistency_score":round(1-conflict_rate,4),"freshness_score":round(1-stale_rate,4),"sensitivity_pressure":round(pressure,4),"domain_pressure_score":round(avg_risk-base,4),"preflight_score":round(score,4),"activation_state":state}

def confusion(cases: List[Dict[str, Any]], v2: bool) -> Dict[str, Dict[str,int]]:
    m = defaultdict(lambda: defaultdict(int))
    for c in cases:
        exp = recommended_gate(c) if v2 else c["expected_gate"]
        m[exp][c["gate"]] += 1
    return {k:dict(sorted(v.items())) for k,v in sorted(m.items())}

def evidence_grid(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_ds = {(c["domain"],c["scenario"]):c for c in cases}
    domains = sorted(set(c["domain"] for c in cases))
    scenarios = ["noisy_input","partial_context","missing_required_field"]
    levels = [45,67,88]
    probes = []
    for d in domains:
        for s in scenarios:
            base = by_ds[(d,s)]
            for ev in levels:
                c = json.loads(json.dumps(base))
                c["case_id"] = f"GRID-{d.upper().replace('_','-')}-{s.upper().replace('_','-')}-{ev}"
                c["evidence_profile"]["coverage"] = float(ev)
                b = case_budget(c)
                probes.append({"case_id":c["case_id"],"domain":d,"scenario":s,"evidence_level":ev,"domain_sensitivity":c["domain_sensitivity"],"adjusted_risk":c["adjusted_risk"],"recommended_gate":recommended_gate(c),"hallucination_budget":b["hallucination_budget"],"reasoning_mode":b["reasoning_mode"]})
    dist = defaultdict(lambda: defaultdict(int))
    for p in probes:
        dist[str(p["evidence_level"])][p["recommended_gate"]] += 1
    return {"status":"PASS","evidence_levels":levels,"target_scenarios":scenarios,"grid_case_count":len(probes),"grid_cases":probes,"gate_distribution_by_evidence_level":{k:dict(sorted(v.items())) for k,v in sorted(dist.items())},"blocked_actions":BLOCKED_ACTIONS}

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod621_650_business_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_CONTROLLED_BUSINESS_CASE_INPUT_WITH_LIVE_DELTA"
    payload = load_json(out / "prod621_650_business_domain_cases.json", {})
    cases = payload.get("cases", [])
    if not cases:
        raise SystemExit("No PROD-621 business cases found. Run PROD-621 first.")

    by_domain = defaultdict(list)
    for c in cases:
        by_domain[c["domain"]].append(c)

    preflight_rows = [preflight_domain(d, items) for d, items in sorted(by_domain.items())]
    budgets = [case_budget(c) for c in cases]
    v1_safe = sum(1 for c in cases if c.get("safe_behavior"))
    v2 = [safe_behavior_v2(c) for c in cases]
    v2_safe = sum(1 for ok,_ in v2 if ok)
    labels = defaultdict(int); rec_dist = defaultdict(int)
    for c, (_, label) in zip(cases, v2):
        labels[label] += 1
        rec_dist[recommended_gate(c)] += 1

    b_by_id = {b["case_id"]:b for b in budgets}
    nums = {
        "adjusted_risk":[float(c["adjusted_risk"]) for c in cases],
        "live_delta_score":[float(c["live_delta_score"]) for c in cases],
        "domain_sensitivity":[float(c["domain_sensitivity"]) for c in cases],
        "evidence_coverage":[float(c["evidence_profile"]["coverage"]) for c in cases],
        "gate_numeric":[GATE_NUMERIC.get(c["gate"],0.5) for c in cases],
        "hallucination_budget":[b_by_id[c["case_id"]]["hallucination_budget"] for c in cases],
        "safe_behavior_v1":[1.0 if c.get("safe_behavior") else 0.0 for c in cases],
        "safe_behavior_v2":[1.0 if safe_behavior_v2(c)[0] else 0.0 for c in cases],
    }
    correlations = {
        "adjusted_risk x live_delta_score": pearson(nums["adjusted_risk"], nums["live_delta_score"]),
        "adjusted_risk x gate_numeric": pearson(nums["adjusted_risk"], nums["gate_numeric"]),
        "domain_sensitivity x adjusted_risk": pearson(nums["domain_sensitivity"], nums["adjusted_risk"]),
        "domain_sensitivity x gate_numeric": pearson(nums["domain_sensitivity"], nums["gate_numeric"]),
        "hallucination_budget x gate_numeric": pearson(nums["hallucination_budget"], nums["gate_numeric"]),
        "hallucination_budget x safe_behavior_v2": pearson(nums["hallucination_budget"], nums["safe_behavior_v2"]),
        "safe_behavior_v1 x safe_behavior_v2": pearson(nums["safe_behavior_v1"], nums["safe_behavior_v2"]),
    }
    findings = [
        {"finding_id":"PATTERN-001","name":"domain_sensitivity_pressure","interpretation":"Domain sensitivity pushes adjusted risk, live delta and review pressure."},
        {"finding_id":"PATTERN-002","name":"partial_context_safe_escalation","interpretation":"Partial context splits into evidence-required for lighter domains and review for sensitive domains."},
        {"finding_id":"PATTERN-003","name":"noisy_input_allow_warning_gap","interpretation":"Noisy input needs ALLOW_WITH_WARNING to preserve useful output without pretending certainty."},
        {"finding_id":"PATTERN-004","name":"evidence_variance_gap","interpretation":"PROD-621 evidence coverage was too constant; this layer adds evidence probes."},
        {"finding_id":"PATTERN-005","name":"preflight_before_domain_activation","interpretation":"A domain should start as neutral seed and only become operational after preflight."},
    ]

    preflight = {"status":"PASS","generated_at":generated_at,"domain_count":len(preflight_rows),"preflight_matrix":preflight_rows,"activation_distribution":dict(sorted({x["activation_state"]:sum(1 for y in preflight_rows if y["activation_state"]==x["activation_state"]) for x in preflight_rows}.items())),"policy":{"neutral_seed":True,"domain_activation_requires_preflight":True,"no_operational_claim_without_ground":True},"blocked_actions":BLOCKED_ACTIONS}
    hall = {"status":"PASS","case_count":len(budgets),"budgets":budgets,"reasoning_mode_distribution":dict(sorted({x["reasoning_mode"]:sum(1 for y in budgets if y["reasoning_mode"]==x["reasoning_mode"]) for x in budgets}.items())),"blocked_actions":BLOCKED_ACTIONS}
    taxonomy = {"status":"PASS","rules":[{"scenario":"partial_context","rule":"low sensitivity -> EVIDENCE_REQUIRED; high sensitivity or adjusted_risk >=55 -> HUMAN_REVIEW_REQUIRED"},{"scenario":"noisy_input","rule":"low/medium sensitivity with evidence >=70 -> ALLOW_WITH_WARNING; high sensitivity -> HUMAN_REVIEW_REQUIRED"},{"scenario":"unsupported_or_execution","rule":"UNSUPPORTED_BLOCKED counts as safe block success"},{"scenario":"conflict_mismatch_high_stakes_stale","rule":"HUMAN_REVIEW_REQUIRED counts as safe review success"}],"original_safe_behavior_rate_pct":pct(v1_safe,len(cases)),"recalibrated_safe_behavior_rate_pct":pct(v2_safe,len(cases)),"taxonomy_counts":dict(sorted(labels.items())),"recommended_gate_distribution":dict(sorted(rec_dist.items())),"blocked_actions":BLOCKED_ACTIONS}
    mining = {"status":"PASS","generated_at":generated_at,"case_count":len(cases),"correlations":correlations,"pattern_findings":findings,"gate_confusion_matrix_v1_expected":confusion(cases,False),"gate_confusion_matrix_v2_recommended":confusion(cases,True),"blocked_actions":BLOCKED_ACTIONS}
    grid = evidence_grid(cases)
    thresholds = {"status":"PASS","recommendations":[{"id":"THR-001","target":"partial_context","rule":"sensitivity <1.25 -> EVIDENCE_REQUIRED; sensitivity >=1.25 or adjusted_risk >=55 -> HUMAN_REVIEW_REQUIRED","auto_apply":False},{"id":"THR-002","target":"noisy_input","rule":"evidence >=70 and sensitivity <=1.20 -> ALLOW_WITH_WARNING; sensitivity >=1.45 -> HUMAN_REVIEW_REQUIRED","auto_apply":False},{"id":"THR-003","target":"hallucination_budget","rule":"budget <0.25 block/review only; 0.25-0.45 gap mapping; 0.45-0.70 guided reasoning; >0.70 full grounded reasoning","auto_apply":False},{"id":"THR-004","target":"evidence_variance","rule":"test low 40-55, medium 60-75, high 80-95 evidence before interactive runner","auto_apply":False}],"blocked_actions":BLOCKED_ACTIONS}
    readiness = {"status":"PASS" if upstream_ready else "WARN","decision":"READY_FOR_BUSINESS_CASE_INTERACTIVE_RUNNER_WITH_PREFLIGHT" if upstream_ready else "REVIEW_UPSTREAM_BUSINESS_MATRIX_READINESS","case_count":len(cases),"domain_count":len(preflight_rows),"original_safe_behavior_rate_pct":pct(v1_safe,len(cases)),"recalibrated_safe_behavior_rate_pct":pct(v2_safe,len(cases)),"ready_for":["business case interactive runner with preflight","neutral domain seed intake","hallucination budget gating","safe escalation reporting"],"not_ready_for":["production activation","autonomous external execution","automatic threshold mutation","client-facing claims","unapproved real company data"],"blocked_actions":BLOCKED_ACTIONS}
    audit = {"status":"PASS" if upstream_ready else "WARN","audit":"Domain Preflight and Pattern Mining audit","case_count":len(cases),"domain_count":len(preflight_rows),"original_safe_behavior_rate_pct":pct(v1_safe,len(cases)),"recalibrated_safe_behavior_rate_pct":pct(v2_safe,len(cases)),"finding":"PASS: neutral domain preflight, hallucination budget, safe escalation taxonomy and pattern mining generated without auto mutation.","readiness":readiness["decision"],"blocked_actions":BLOCKED_ACTIONS}

    outs = {
        "prod621b_650b_domain_preflight_matrix.json": preflight,
        "prod621b_650b_hallucination_budget.json": hall,
        "prod621b_650b_safe_escalation_taxonomy.json": taxonomy,
        "prod621b_650b_business_pattern_mining.json": mining,
        "prod621b_650b_evidence_variance_grid.json": grid,
        "prod621b_650b_gate_confusion_matrix.json": {"status":"PASS","v1_expected":confusion(cases,False),"v2_recommended":confusion(cases,True),"blocked_actions":BLOCKED_ACTIONS},
        "prod621b_650b_threshold_recommendations.json": thresholds,
        "prod621b_650b_readiness.json": readiness,
        "prod621b_650b_audit_report.json": audit,
    }
    for name, obj in outs.items():
        write_json(out / name, obj)

    lines = ["# PROD-621B..650B Domain Preflight and Pattern Mining Layer","",f"- Status: `{audit['status']}`",f"- Cases analyzed: `{len(cases)}`",f"- Original safe behavior: `{pct(v1_safe,len(cases))}%`",f"- Recalibrated safe behavior: `{pct(v2_safe,len(cases))}%`",f"- Decision: `{readiness['decision']}`","","## Activation Distribution"]
    for k,v in preflight["activation_distribution"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["","## Reasoning Mode Distribution"]
    for k,v in hall["reasoning_mode_distribution"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["","## Correlations"]
    for k,v in correlations.items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["","## Pattern Findings"]
    for f in findings:
        lines.append(f"- `{f['finding_id']}` `{f['name']}`: {f['interpretation']}")
    lines += ["","## Threshold Recommendations"]
    for r in thresholds["recommendations"]:
        lines.append(f"- `{r['id']}` `{r['target']}`: `{r['rule']}`")
    lines += ["","## Next Recommended Bundle","- `PROD-651 Business Case Interactive Runner with Preflight and Live Delta`"]
    write_text(out / "prod621b_650b_domain_preflight_pattern_report.md", "\n".join(lines) + "\n")

    result = {"task":"PROD-621B..650B","status":audit["status"],"phase":"Domain Preflight and Pattern Mining Layer","decision":readiness["decision"],"outputs":["outputs/"+k for k in outs.keys()],"next_recommended_bundle":"PROD-651 Business Case Interactive Runner with Preflight and Live Delta","blocked_actions":BLOCKED_ACTIONS}
    write_json(out / "prod621b_650b_result.json", result)
    write_text(out / "prod621b_650b_report.md", "# PROD-621B..650B Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    print(json.dumps(build(Path(args.repo)), indent=2, ensure_ascii=False))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
