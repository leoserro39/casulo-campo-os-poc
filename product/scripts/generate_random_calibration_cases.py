#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Any


CASE_FAMILIES = ["parser_documental", "audit_documental", "rule_extraction", "software_review"]
DOC_TYPES = {
    "parser_documental": ["service_intake", "invoice_receipt", "form_record", "email_request", "checklist"],
    "audit_documental": ["contract_checklist", "policy_audit", "compliance_packet", "evidence_dossier"],
    "rule_extraction": ["procedure", "policy", "acceptance_criteria", "business_rule_sheet"],
    "software_review": ["repo_summary", "incident_log", "release_notes", "test_report"],
}
RISK_BY_FAMILY = {
    "parser_documental": ["low", "medium"],
    "audit_documental": ["medium", "high"],
    "rule_extraction": ["medium", "high"],
    "software_review": ["medium", "high"],
}


def pick(rng: random.Random, items: List[str]) -> str:
    return items[rng.randrange(len(items))]


def make_case(idx: int, rng: random.Random, family: str | None = None) -> Dict[str, Any]:
    case_family = family or pick(rng, CASE_FAMILIES)
    ambiguity = rng.randint(0, 100)
    missingness = rng.randint(0, 100)
    noise = rng.randint(0, 100)
    conflict = rng.randint(0, 100)
    complexity = rng.randint(1, 5)
    evidence_strength = max(0, min(100, 100 - int((missingness * 0.45 + ambiguity * 0.25 + noise * 0.15 + conflict * 0.15))))
    domain_risk = pick(rng, RISK_BY_FAMILY[case_family])
    doc_type = pick(rng, DOC_TYPES[case_family])

    return {
        "case_id": f"STOCH-{idx:04d}-{case_family.upper()}",
        "case_family": case_family,
        "document_type": doc_type,
        "ambiguity_level": ambiguity,
        "missingness_level": missingness,
        "noise_level": noise,
        "conflict_level": conflict,
        "document_complexity": complexity,
        "domain_risk": domain_risk,
        "evidence_strength": evidence_strength,
        "synthetic_profile": "randomized_controlled_no_real_company_data",
        "blocked_outputs": [
            "production claim",
            "deployment",
            "automatic merge",
            "credential handling",
            "client-facing final decision"
        ],
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, cases: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(cases[0].keys()) if cases else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(cases)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--out-json", default="outputs/prod201_220_random_cases.json")
    parser.add_argument("--out-csv", default="outputs/prod201_220_random_cases.csv")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    cases: List[Dict[str, Any]] = []
    # Ensure each family appears at least several times.
    for i in range(1, args.count + 1):
        forced_family = CASE_FAMILIES[(i - 1) % len(CASE_FAMILIES)] if i <= len(CASE_FAMILIES) * 5 else None
        cases.append(make_case(i, rng, forced_family))

    repo = Path(args.repo)
    data = {
        "status": "PASS",
        "generator": "casulo.random_case_generator.v0.1",
        "seed": args.seed,
        "count": len(cases),
        "cases": cases,
    }
    write_json(repo / args.out_json, data)
    write_csv(repo / args.out_csv, cases)
    print(json.dumps({"status": "PASS", "count": len(cases), "seed": args.seed, "json": args.out_json, "csv": args.out_csv}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
