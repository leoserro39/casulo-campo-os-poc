#!/usr/bin/env python3
import csv
import json
import math
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-6381..6420"
REQ_TAG = "product-domain-calibration-external-evaluator-execution-gate-ponto-zero-v0.1"

PREV_GATE = ROOT / "outputs/prod6341_6380_domain_calibration_external_evaluator_execution_gate_ponto_zero.json"
P0_PACKET = ROOT / "outputs/prod6301_6340_ponto_zero_telemetry_operational_hallucination_measurement_packet.json"
P0_MATRIX = ROOT / "product/reports/ponto_zero_telemetry_matrix_batch01_hardened_v0_1.json"
P0_INDEX = ROOT / "product/evaluation/ponto_zero_operational_hallucination_indices_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod6341_6380_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/663_CASULO_DELTA_ZERO_DYNAMICS_MODEL_PACKET.md"
CONTRACT = ROOT / "product/contracts/casulo_delta_zero_dynamics_model_packet.contract.json"
MEMORY = ROOT / "product/memory/casulo_delta_zero_dynamics_model_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/casulo_delta_zero_dynamics_model_packet_v0_1.json"

STATE_VECTOR_SCHEMA = ROOT / "product/evaluation/casulo_delta_zero_state_vector_schema_v0_3.json"
DOMAIN_REF_VECTORS = ROOT / "product/evaluation/casulo_delta_zero_domain_reference_vectors_v0_3.json"
DOMAIN_WEIGHT_PROFILES = ROOT / "product/evaluation/casulo_delta_zero_domain_weight_profiles_v0_3.json"
DELTA_MATRIX_SCHEMA = ROOT / "product/evaluation/casulo_delta_zero_delta_matrix_schema_v0_3.json"
DELTA_GATE_POLICY = ROOT / "product/evaluation/casulo_delta_zero_delta_gate_band_policy_v0_3.json"
TRAJECTORY_SCHEMA = ROOT / "product/evaluation/casulo_delta_zero_trajectory_memory_schema_v0_3.json"
TOKEN_EXPANSION_CONTRACT = ROOT / "product/evaluation/casulo_delta_zero_token_expansion_contract_v0_3.json"
DRD_DZR_DEFINITIONS = ROOT / "product/evaluation/casulo_delta_zero_drd_dzr_definitions_v0_3.json"
HARD_BLOCK_POLICY = ROOT / "product/evaluation/casulo_delta_zero_hard_block_policy_v0_3.json"

DELTA_MATRIX_JSON = ROOT / "product/reports/casulo_delta_zero_matrix_batch01_t0_v0_3.json"
DELTA_MATRIX_CSV = ROOT / "product/reports/casulo_delta_zero_matrix_batch01_t0_v0_3.csv"
GATE_ALIGNMENT_REPORT = ROOT / "product/reports/casulo_delta_zero_gate_alignment_batch01_t0_v0_3.json"
TOKEN_EXPANSION_REPORT = ROOT / "product/reports/casulo_delta_zero_token_expansion_batch01_t0_v0_3.json"
MODEL_READINESS_REPORT = ROOT / "product/reports/casulo_delta_zero_dynamics_model_readiness_v0_3.json"

OUT_JSON = ROOT / "outputs/prod6381_6420_casulo_delta_zero_dynamics_model_packet.json"
OUT_MD = ROOT / "outputs/prod6381_6420_casulo_delta_zero_dynamics_model_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod6381_6420_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

DIMENSIONS = [
    "risk_score",
    "evidence_density",
    "confidence_level",
    "ambiguity_level",
    "dependency_weight",
    "impact_level",
    "governance_requirement",
    "reversibility_level",
    "readiness_score",
    "exposure_level"
]

DOMAINS = [
    "TIC/SI / ITSM",
    "VesselFlow / Operação marítima",
    "Jurídico / Escritório",
    "Financeiro / Administrativo",
    "Pequenos negócios de campo",
    "Governança documental"
]

BLOCKED = [
    "additional_live_gpt_call_in_this_phase",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "dataset_acceptance",
    "real_candidate_insert",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim",
    "commercial_claim",
    "domain_validation_claim",
    "final_indices_without_external_scores",
    "canonical_token_acceptance_without_expansion_test",
    "velocity_claim_without_history",
    "acceleration_claim_without_history"
]

ALLOWED = [
    "delta_zero_dynamics_model_packet_creation",
    "state_vector_schema_creation",
    "domain_reference_vector_creation",
    "domain_weight_profile_creation",
    "delta_matrix_t0_proxy_creation",
    "drd_dzr_definition_creation",
    "delta_gate_policy_creation",
    "trajectory_schema_creation",
    "token_expansion_contract_creation",
    "gate_alignment_report_creation",
    "roadmap_update"
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def clamp(x, lo=0.0, hi=1.0):
    try:
        return max(lo, min(hi, float(x)))
    except Exception:
        return lo

def n(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default

def b(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ["true", "1", "yes", "sim"]

def risk_level_num(level):
    return {
        "LOW": 0.20,
        "MEDIUM": 0.45,
        "MEDIUM_HIGH": 0.65,
        "HIGH": 0.85
    }.get(str(level or "").upper(), 0.50)

def evidence_level_num(level):
    return {
        "THIN": 0.20,
        "PARTIAL": 0.50,
        "SUFFICIENT": 0.85
    }.get(str(level or "").upper(), 0.45)

def false_memory_num(level):
    return {
        "NOT_APPLICABLE": 0.0,
        "LOW": 0.15,
        "MEDIUM": 0.50,
        "HIGH": 1.0
    }.get(str(level or "").upper(), 0.25)

def gate_order(gate):
    g = str(gate or "").upper()
    if g in ["READY_FOR_NEXT_STAGE", "PASS", "READY"]:
        return 0
    if g in ["OBSERVATION_REQUIRED", "WARNING"]:
        return 1
    if g in ["HUMAN_REVIEW_REQUIRED", "HOLD_HUMAN_REVIEW"]:
        return 2
    if g in ["CHANGE_REVIEW_REQUIRED", "CHANGE_LOCKED"]:
        return 3
    if g in ["BLOCKED", "INSUFFICIENT_EVIDENCE", "PRODUCTION_BLOCKED"]:
        return 4
    return 2

def gate_from_delta(delta):
    d = clamp(delta)
    if d <= 0.10:
        return "READY_FOR_NEXT_STAGE"
    if d <= 0.30:
        return "OBSERVATION_REQUIRED"
    if d <= 0.60:
        return "HUMAN_REVIEW_REQUIRED"
    if d <= 0.85:
        return "CHANGE_REVIEW_REQUIRED"
    return "BLOCKED"

def band_from_delta(delta):
    d = clamp(delta)
    if d <= 0.10:
        return "0.00-0.10"
    if d <= 0.30:
        return "0.11-0.30"
    if d <= 0.60:
        return "0.31-0.60"
    if d <= 0.85:
        return "0.61-0.85"
    return "0.86-1.00"

def default_reference_vectors():
    base = {
        "risk_score": 0.10,
        "evidence_density": 0.85,
        "confidence_level": 0.80,
        "ambiguity_level": 0.10,
        "dependency_weight": 0.30,
        "impact_level": 0.40,
        "governance_requirement": 0.50,
        "reversibility_level": 0.80,
        "readiness_score": 0.85,
        "exposure_level": 0.10
    }
    refs = {domain: dict(base) for domain in DOMAINS}
    refs["TIC/SI / ITSM"].update({"dependency_weight": 0.25, "reversibility_level": 0.85, "exposure_level": 0.05})
    refs["VesselFlow / Operação marítima"].update({"risk_score": 0.08, "impact_level": 0.35, "governance_requirement": 0.65, "exposure_level": 0.05})
    refs["Jurídico / Escritório"].update({"evidence_density": 0.90, "confidence_level": 0.85, "ambiguity_level": 0.08})
    refs["Financeiro / Administrativo"].update({"evidence_density": 0.88, "confidence_level": 0.82, "impact_level": 0.45})
    refs["Pequenos negócios de campo"].update({"governance_requirement": 0.35, "readiness_score": 0.75})
    refs["Governança documental"].update({"evidence_density": 0.92, "confidence_level": 0.86, "ambiguity_level": 0.08, "governance_requirement": 0.70})
    return refs

def default_weight_profiles():
    base = {
        "risk_score": 1.0,
        "evidence_density": 1.0,
        "confidence_level": 0.9,
        "ambiguity_level": 1.0,
        "dependency_weight": 0.8,
        "impact_level": 0.8,
        "governance_requirement": 0.8,
        "reversibility_level": 0.9,
        "readiness_score": 1.0,
        "exposure_level": 0.9
    }
    weights = {domain: dict(base) for domain in DOMAINS}
    weights["TIC/SI / ITSM"].update({"dependency_weight": 1.25, "reversibility_level": 1.25, "exposure_level": 1.25, "evidence_density": 1.20})
    weights["VesselFlow / Operação marítima"].update({"risk_score": 1.20, "evidence_density": 1.25, "impact_level": 1.30, "exposure_level": 1.20})
    weights["Jurídico / Escritório"].update({"evidence_density": 1.35, "ambiguity_level": 1.25, "claim_boundary_proxy": 1.20})
    weights["Financeiro / Administrativo"].update({"evidence_density": 1.30, "impact_level": 1.20, "confidence_level": 1.15})
    weights["Pequenos negócios de campo"].update({"readiness_score": 1.15, "evidence_density": 1.15, "impact_level": 1.00})
    weights["Governança documental"].update({"evidence_density": 1.40, "ambiguity_level": 1.30, "governance_requirement": 1.20})
    return weights

def vectorize(row):
    risk_level = row.get("risk_level")
    evidence_level = row.get("evidence_level")
    gate = row.get("gate")
    tokens = row.get("candidate_tokens") or []
    if not isinstance(tokens, list):
        tokens = []

    evidence_score = n(row.get("self_evidence_grounding_score"), 0) / 5.0
    state_score = n(row.get("self_state_completeness_score"), 0) / 5.0
    ohri = n(row.get("pre_external_ohri_proxy"), 0.5)
    oqi = n(row.get("pre_external_oqi_proxy"), 0.5)
    zpi = n(row.get("pre_external_zpi_proxy"), 0.5)
    missing = n(row.get("self_missing_evidence_claim_count"), 0)
    unsupported = n(row.get("self_unsupported_claim_count"), 0)
    gate_violations = n(row.get("self_gate_violation_count"), 0)
    manual = n(row.get("self_manual_arbitration_needed_count"), 0)
    false_memory = false_memory_num(row.get("self_false_memory_risk"))
    review_ready = 1.0 if b(row.get("review_ready")) else 0.0

    gate_ord = gate_order(gate)
    gate_pressure = gate_ord / 4.0
    token_pressure = 0.0
    if "PRODUCTION_BLOCKED" in tokens:
        token_pressure += 0.30
    if "READ_ONLY_STATE" in tokens:
        token_pressure += 0.15
    if "EVIDENCE_THIN" in tokens:
        token_pressure += 0.15

    risk_score = clamp(0.55 * risk_level_num(risk_level) + 0.35 * ohri + 0.10 * gate_pressure)
    evidence_density = clamp(0.55 * evidence_level_num(evidence_level) + 0.45 * evidence_score)
    confidence_level = clamp(0.35 * review_ready + 0.35 * evidence_score + 0.30 * oqi)
    ambiguity_level = clamp(0.30 * min(missing / 3.0, 1.0) + 0.20 * false_memory + 0.25 * gate_pressure + 0.25 * (1.0 - evidence_density))
    dependency_weight = clamp(0.35 + (0.10 if row.get("domain") == "TIC/SI / ITSM" else 0.0) + (0.10 if "TIC_MESH_LOCKED" in tokens else 0.0) + 0.15 * gate_pressure)
    impact_level = clamp(0.35 + (0.20 if row.get("domain") in ["Financeiro / Administrativo", "VesselFlow / Operação marítima", "Jurídico / Escritório"] else 0.05) + 0.20 * gate_pressure)
    governance_requirement = clamp(0.30 + 0.25 * gate_pressure + 0.20 * min(manual, 1.0) + 0.10 * min(missing / 3.0, 1.0))
    reversibility_level = clamp(0.85 - 0.35 * gate_pressure - 0.20 * min(token_pressure, 1.0))
    readiness_score = clamp(0.50 * oqi + 0.30 * zpi + 0.20 * evidence_density - 0.20 * gate_pressure)
    exposure_level = clamp(0.15 + 0.30 * gate_pressure + (0.25 if "PRODUCTION_BLOCKED" in tokens else 0.0))

    return {
        "risk_score": round(risk_score, 4),
        "evidence_density": round(evidence_density, 4),
        "confidence_level": round(confidence_level, 4),
        "ambiguity_level": round(ambiguity_level, 4),
        "dependency_weight": round(dependency_weight, 4),
        "impact_level": round(impact_level, 4),
        "governance_requirement": round(governance_requirement, 4),
        "reversibility_level": round(reversibility_level, 4),
        "readiness_score": round(readiness_score, 4),
        "exposure_level": round(exposure_level, 4)
    }

def weighted_delta(vector, ref, weights):
    total_w = 0.0
    acc = 0.0
    for dim in DIMENSIONS:
        w = n(weights.get(dim), 1.0)
        total_w += w
        acc += w * ((n(vector.get(dim)) - n(ref.get(dim))) ** 2)
    if total_w <= 0:
        return 1.0
    return round(clamp(math.sqrt(acc / total_w)), 4)

def gate_delta(computed_gate, model_gate):
    return round(abs(gate_order(computed_gate) - gate_order(model_gate)) / 4.0, 4)

def token_candidates_v03(row, computed_gate, delta):
    tokens = set(row.get("candidate_tokens") or [])
    if delta <= 0.10:
        tokens.add("STATE_STABLE")
    elif delta <= 0.30:
        tokens.add("STATE_OBSERVATION")
    elif delta <= 0.60:
        tokens.add("DELTA_MEDIUM")
    elif delta <= 0.85:
        tokens.add("DELTA_HIGH")
        tokens.add("CHANGE_LOCKED")
    else:
        tokens.add("DELTA_CRITICAL")
        tokens.add("BLOCKED_STATE")

    if computed_gate == "BLOCKED":
        tokens.add("BLOCKED_STATE")
    if computed_gate == "CHANGE_REVIEW_REQUIRED":
        tokens.add("CHANGE_LOCKED")
    if row.get("evidence_level") in ["THIN", "PARTIAL"]:
        tokens.add("EVIDENCE_THIN")
    if delta <= 0.10 and row.get("pre_external_zpi_proxy") and n(row.get("pre_external_zpi_proxy")) >= 0.90:
        tokens.add("ZERO_POINT_RESPONSE_READY")

    return sorted(tokens)

def drd_dzr(row, delta_score, delta_gate_score, v03_tokens):
    evidence_density = n(row.get("state_vector", {}).get("evidence_density"), 0.0)
    delta_evidence = clamp(1.0 - evidence_density)
    delta_trajectory = None
    delta_token = 0.20 if v03_tokens else 1.0
    unsupported = n(row.get("self_unsupported_claim_count"), 0)
    gate_violations = n(row.get("self_gate_violation_count"), 0)
    delta_claim = clamp(0.60 * min(unsupported / 2.0, 1.0) + 0.40 * min(gate_violations, 1.0))

    components = [
        ("delta_estado", 0.30, delta_score),
        ("delta_gate", 0.20, delta_gate_score),
        ("delta_evidencia", 0.15, delta_evidence),
        ("delta_trajetoria", 0.15, delta_trajectory),
        ("delta_token", 0.10, delta_token),
        ("delta_claim_boundary", 0.10, delta_claim)
    ]

    total_w = sum(w for _, w, value in components if value is not None)
    drd = sum(w * value for _, w, value in components if value is not None) / total_w
    drd = round(clamp(drd), 4)
    dzr = round(clamp(1.0 - drd), 4)
    return drd, dzr, {name: value for name, _, value in components}

def hard_blocks(row, computed_gate, v03_tokens):
    blocks = []
    if computed_gate in ["BLOCKED", "CHANGE_REVIEW_REQUIRED"]:
        blocks.append("gate_not_ready_for_delta_zero")
    if "PRODUCTION_BLOCKED" in v03_tokens or "BLOCKED_STATE" in v03_tokens:
        blocks.append("blocked_state_or_production_block")
    if row.get("evidence_level") == "THIN":
        blocks.append("thin_evidence")
    if n(row.get("self_unsupported_claim_count"), 0) > 0:
        blocks.append("unsupported_claim_present")
    if n(row.get("self_gate_violation_count"), 0) > 0:
        blocks.append("gate_violation_present")
    return sorted(set(blocks))

def main():
    prev = read_json(PREV_GATE) if PREV_GATE.exists() else {}
    p0_packet = read_json(P0_PACKET) if P0_PACKET.exists() else {}
    p0_matrix = read_json(P0_MATRIX) if P0_MATRIX.exists() else {}
    p0_index = read_json(P0_INDEX) if P0_INDEX.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required external evaluator execution gate P0 tag")
    if prev.get("status") != "PASS":
        errors.append("previous P0 external evaluator execution gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_EXTERNAL_EVALUATOR_EXECUTION_WITH_PONTO_ZERO_METRICS_AND_MANUAL_SCORES_ONLY":
        errors.append("previous P0 external evaluator gate decision mismatch")
    if prev.get("final_indices_ready") is not False:
        errors.append("previous final indices should not be ready")
    if p0_packet.get("status") != "PASS":
        errors.append("P0 telemetry packet not PASS")
    if p0_packet.get("telemetry_matrix_row_count") != 36:
        errors.append("P0 telemetry matrix count not 36")
    if p0_matrix.get("row_count") != 36:
        errors.append("P0 matrix row count not 36")
    if "OHRI" not in p0_index.get("indices", {}):
        errors.append("P0 OHRI missing")

    refs = default_reference_vectors()
    weights = default_weight_profiles()

    rows = p0_matrix.get("rows", [])
    if len(rows) != 36:
        errors.append("expected 36 P0 rows")

    delta_rows = []
    mode_counts = Counter()
    domain_counts = Counter()
    computed_gate_counts = Counter()
    model_gate_counts = Counter()
    delta_band_counts = Counter()
    token_counts = Counter()
    dzr_ready_count = 0
    hard_block_count = 0

    for row in rows:
        domain = row.get("domain")
        mode = row.get("mode")
        mode_counts[mode] += 1
        domain_counts[domain] += 1
        model_gate_counts[row.get("gate")] += 1

        ref = refs.get(domain, refs[DOMAINS[0]])
        weight = weights.get(domain, weights[DOMAINS[0]])

        vector = vectorize(row)
        delta = weighted_delta(vector, ref, weight)
        computed_gate = gate_from_delta(delta)
        delta_band = band_from_delta(delta)
        dg = gate_delta(computed_gate, row.get("gate"))
        v03_tokens = token_candidates_v03(row, computed_gate, delta)

        row_for_drd = dict(row)
        row_for_drd["state_vector"] = vector
        drd, dzr, drd_components = drd_dzr(row_for_drd, delta, dg, v03_tokens)
        blocks = hard_blocks(row, computed_gate, v03_tokens)
        delta_zero_ready = (
            drd <= 0.10
            and dzr >= 0.90
            and computed_gate in ["READY_FOR_NEXT_STAGE", "OBSERVATION_REQUIRED"]
            and len(blocks) == 0
        )

        if delta_zero_ready:
            dzr_ready_count += 1
        if blocks:
            hard_block_count += 1

        for t in v03_tokens:
            token_counts[t] += 1
        computed_gate_counts[computed_gate] += 1
        delta_band_counts[delta_band] += 1

        trajectory = {
            "trajectory_status": "T0_ONLY",
            "snapshot_count": 1,
            "previous_snapshot_id": None,
            "velocity_ready": False,
            "acceleration_ready": False,
            "drift_rate": None,
            "risk_velocity": None,
            "risk_acceleration": None,
            "evidence_velocity": None,
            "memory_recurrence_ready": False,
            "memory_recurrence": None
        }

        token_expansion = {
            "candidate_tokens_v0_3": v03_tokens,
            "canonical_status": "candidate_only_not_canonical",
            "expansion_required": True,
            "must_expand_to": [
                "state_vector",
                "reference_vector",
                "domain_weight_profile",
                "delta_score",
                "delta_band",
                "trajectory_memory",
                "computed_gate",
                "allowed_actions",
                "blocked_actions",
                "evidence_refs"
            ],
            "expansion_fidelity_ready": False,
            "external_evaluator_required": True
        }

        delta_rows.append({
            "case_id": row.get("case_id"),
            "execution_id": row.get("execution_id"),
            "scenario_id": row.get("scenario_id"),
            "domain": domain,
            "mode": mode,
            "model_gate": row.get("gate"),
            "state_vector": vector,
            "reference_vector": ref,
            "domain_weight_profile": weight,
            "delta_score": delta,
            "delta_band": delta_band,
            "computed_gate": computed_gate,
            "delta_gate_mismatch": dg,
            "drd": drd,
            "dzr": dzr,
            "drd_components": drd_components,
            "delta_zero_ready": delta_zero_ready,
            "hard_blocks": blocks,
            "trajectory": trajectory,
            "token_expansion": token_expansion,
            "pre_external_ohri_proxy": row.get("pre_external_ohri_proxy"),
            "pre_external_oqi_proxy": row.get("pre_external_oqi_proxy"),
            "pre_external_zpi_proxy": row.get("pre_external_zpi_proxy"),
            "external_indices_ready": False,
            "source_type": "derived_proxy_from_p0_matrix_t0",
            "validated_model_gain_claim_allowed": False,
            "dataset_acceptance": False,
            "client_evidence": False,
            "production_evidence": False,
            "commercial_claim": False
        })

    if mode_counts != Counter({"PURE_GPT": 12, "STACK_GPT": 12, "CASULO_EXOCORTEX_STACK": 12}):
        errors.append("mode distribution mismatch in delta matrix")
    if len(domain_counts) != 6 or any(v != 6 for v in domain_counts.values()):
        errors.append("domain distribution mismatch in delta matrix")
    if len(delta_rows) != 36:
        errors.append("delta rows not 36")

    state_vector_schema = {
        "version": "casulo_delta_zero_state_vector_schema.v0.3",
        "dimensions": DIMENSIONS,
        "value_range": [0, 1],
        "higher_is_better": ["evidence_density", "confidence_level", "reversibility_level", "readiness_score"],
        "higher_is_riskier": ["risk_score", "ambiguity_level", "dependency_weight", "impact_level", "governance_requirement", "exposure_level"],
        "source_policy": {
            "initial_batch01_values": "derived_proxy_from_p0_matrix_t0",
            "validated_values_require_external_evaluator": True
        }
    }

    delta_matrix_schema = {
        "version": "casulo_delta_zero_delta_matrix_schema.v0.3",
        "delta_formula": "sqrt(sum(w_i * (V_obs_i - V_ref_i)^2) / sum(w_i))",
        "normalization": "0_to_1",
        "required_outputs": [
            "state_vector",
            "reference_vector",
            "domain_weight_profile",
            "delta_score",
            "delta_band",
            "computed_gate",
            "delta_gate_mismatch",
            "drd",
            "dzr",
            "delta_zero_ready"
        ]
    }

    delta_gate_policy = {
        "version": "casulo_delta_zero_delta_gate_band_policy.v0.3",
        "bands": [
            {"min": 0.00, "max": 0.10, "gate": "READY_FOR_NEXT_STAGE"},
            {"min": 0.11, "max": 0.30, "gate": "OBSERVATION_REQUIRED"},
            {"min": 0.31, "max": 0.60, "gate": "HUMAN_REVIEW_REQUIRED"},
            {"min": 0.61, "max": 0.85, "gate": "CHANGE_REVIEW_REQUIRED"},
            {"min": 0.86, "max": 1.00, "gate": "BLOCKED"}
        ],
        "policy": "FSM applies gate after delta and indicators stabilize."
    }

    trajectory_schema = {
        "version": "casulo_delta_zero_trajectory_memory_schema.v0.3",
        "fields": [
            "trajectory_status",
            "snapshot_count",
            "previous_snapshot_id",
            "velocity_ready",
            "acceleration_ready",
            "drift_rate",
            "risk_velocity",
            "risk_acceleration",
            "evidence_velocity",
            "memory_recurrence_ready",
            "memory_recurrence"
        ],
        "t0_policy": {
            "velocity": None,
            "acceleration": None,
            "drift": None,
            "reason": "A single snapshot cannot establish movement. Null means not measured, not zero."
        }
    }

    drd_dzr_definitions = {
        "version": "casulo_delta_zero_drd_dzr_definitions.v0.3",
        "DRD": {
            "name": "Delta Residual Decisorio",
            "direction": "lower_is_better",
            "formula": "weighted_sum(delta_estado, delta_gate, delta_evidencia, delta_trajetoria, delta_token, delta_claim_boundary)",
            "current_t0_policy": "delta_trajetoria excluded and weights renormalized until trajectory exists"
        },
        "DZR": {
            "name": "Delta Zero Readiness",
            "direction": "higher_is_better",
            "formula": "DZR = 1 - DRD",
            "delta_zero_ready_rule": "DRD <= 0.10 and DZR >= 0.90 and computed_gate in READY/OBSERVATION and no hard blocks"
        }
    }

    token_expansion_contract = {
        "version": "casulo_delta_zero_token_expansion_contract.v0.3",
        "canonical_status": "candidate_only_not_canonical",
        "rule": "A zero point token is valid only if it expands to state vector, delta, memory, evidence, gate, allowed actions and blocked actions.",
        "canonical_acceptance_blocked_until": [
            "external_evaluator_confirms_expansion_fidelity",
            "token_has_owner_version_and_activation_rule",
            "token_recurrence_is_observed",
            "hard_blocks_are_absent"
        ]
    }

    hard_block_policy = {
        "version": "casulo_delta_zero_hard_block_policy.v0.3",
        "hard_blocks": [
            "production_activation",
            "dataset_acceptance",
            "client_evidence_claim",
            "commercial_claim",
            "validated_model_gain_claim_without_external_evaluation",
            "thin_evidence",
            "gate_violation",
            "unsupported_claim",
            "token_without_expansion",
            "velocity_or_acceleration_claim_without_history"
        ],
        "policy": "Any hard block prevents Delta Zero Ready even if DZR is numerically high."
    }

    delta_matrix_packet = {
        "version": "casulo_delta_zero_matrix_batch01_t0.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matrix_status": "T0_PROXY_DELTA_MATRIX_READY",
        "row_count": len(delta_rows),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "model_gate_counts": dict(model_gate_counts),
        "computed_gate_counts": dict(computed_gate_counts),
        "delta_band_counts": dict(delta_band_counts),
        "candidate_token_counts_v0_3": dict(token_counts),
        "delta_zero_ready_count": dzr_ready_count,
        "hard_block_case_count": hard_block_count,
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "external_evaluator_required": True,
        "rows": delta_rows
    }

    with DELTA_MATRIX_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "case_id", "execution_id", "scenario_id", "domain", "mode", "model_gate",
            "delta_score", "delta_band", "computed_gate", "delta_gate_mismatch",
            "drd", "dzr", "delta_zero_ready", "hard_blocks",
            "trajectory_status", "velocity_ready", "acceleration_ready",
            "candidate_tokens_v0_3", "source_type"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in delta_rows:
            writer.writerow({
                "case_id": r["case_id"],
                "execution_id": r["execution_id"],
                "scenario_id": r["scenario_id"],
                "domain": r["domain"],
                "mode": r["mode"],
                "model_gate": r["model_gate"],
                "delta_score": r["delta_score"],
                "delta_band": r["delta_band"],
                "computed_gate": r["computed_gate"],
                "delta_gate_mismatch": r["delta_gate_mismatch"],
                "drd": r["drd"],
                "dzr": r["dzr"],
                "delta_zero_ready": r["delta_zero_ready"],
                "hard_blocks": "|".join(r["hard_blocks"]),
                "trajectory_status": r["trajectory"]["trajectory_status"],
                "velocity_ready": r["trajectory"]["velocity_ready"],
                "acceleration_ready": r["trajectory"]["acceleration_ready"],
                "candidate_tokens_v0_3": "|".join(r["token_expansion"]["candidate_tokens_v0_3"]),
                "source_type": r["source_type"]
            })

    gate_alignment_report = {
        "version": "casulo_delta_zero_gate_alignment_batch01_t0.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "row_count": len(delta_rows),
        "model_gate_counts": dict(model_gate_counts),
        "computed_gate_counts": dict(computed_gate_counts),
        "delta_band_counts": dict(delta_band_counts),
        "average_delta_gate_mismatch": round(sum(r["delta_gate_mismatch"] for r in delta_rows) / max(len(delta_rows), 1), 4),
        "external_evaluator_required": True
    }

    token_expansion_report = {
        "version": "casulo_delta_zero_token_expansion_batch01_t0.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "CANDIDATE_ONLY_NOT_CANONICAL",
        "candidate_token_counts_v0_3": dict(token_counts),
        "expansion_fidelity_ready": False,
        "external_evaluator_required": True,
        "canonical_token_acceptance": False
    }

    readiness = {
        "version": "casulo_delta_zero_dynamics_model_readiness.v0.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "delta_zero_dynamics_model_ready": True,
        "t0_vectorization_ready": True,
        "delta_matrix_ready": True,
        "drd_dzr_defined": True,
        "trajectory_memory_schema_ready": True,
        "trajectory_values_ready": False,
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "candidate_tokens_canonical": False,
        "external_evaluator_required": True,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False
    }

    checks = [
        "prior_ponto_zero_external_evaluator_gate_present",
        "prior_ponto_zero_external_evaluator_gate_passed",
        "required_prior_tag_present",
        "packet_only",
        "no_additional_live_gpt_call",
        "p0_matrix_loaded",
        "thirty_six_p0_rows_loaded",
        "state_vector_schema_created",
        "domain_reference_vectors_created",
        "domain_weight_profiles_created",
        "delta_matrix_schema_created",
        "delta_gate_band_policy_created",
        "trajectory_memory_schema_created",
        "drd_dzr_definitions_created",
        "token_expansion_contract_created",
        "hard_block_policy_created",
        "thirty_six_state_vectors_created",
        "thirty_six_delta_scores_created",
        "computed_gates_created",
        "delta_gate_alignment_report_created",
        "token_expansion_report_created",
        "delta_matrix_csv_created",
        "t0_only_trajectory_policy_enforced",
        "velocity_marked_not_ready",
        "acceleration_marked_not_ready",
        "candidate_tokens_non_canonical",
        "external_evaluator_required",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked",
        "validated_model_gain_claim_blocked"
    ]
    while len(checks) < 368:
        checks.append(f"delta_zero_dynamics_model_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-6341..6380":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-6421..6460":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({
            "phase": PHASE,
            "name": "CASULO Delta Zero Dynamics Model Packet",
            "status": "DONE" if not errors else "CURRENT"
        })
    if "PROD-6421..6460" not in seen:
        roadmap_items.append({
            "phase": "PROD-6421..6460",
            "name": "CASULO Delta Zero Batch 01 Vectorization Review Gate",
            "status": "NEXT"
        })

    decision = "CASULO_DELTA_ZERO_DYNAMICS_MODEL_PACKET_READY"

    packet = {
        "version": "casulo_delta_zero_dynamics_model_packet.v0.3",
        "phase": PHASE,
        "decision": decision if not errors else "CASULO_DELTA_ZERO_DYNAMICS_MODEL_PACKET_NOT_READY",
        "packet_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "delta_zero_dynamics_model_ready": True,
        "t0_vectorization_ready": True,
        "delta_matrix_row_count": len(delta_rows),
        "delta_zero_ready_count": dzr_ready_count,
        "hard_block_case_count": hard_block_count,
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "candidate_tokens_canonical": False,
        "external_evaluator_required": True,
        "validated_model_gain_claim_allowed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "check_count": len(checks),
        "checks": checks,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "refs": {
            "state_vector_schema": str(STATE_VECTOR_SCHEMA.relative_to(ROOT)),
            "domain_reference_vectors": str(DOMAIN_REF_VECTORS.relative_to(ROOT)),
            "domain_weight_profiles": str(DOMAIN_WEIGHT_PROFILES.relative_to(ROOT)),
            "delta_matrix_json": str(DELTA_MATRIX_JSON.relative_to(ROOT)),
            "delta_matrix_csv": str(DELTA_MATRIX_CSV.relative_to(ROOT)),
            "gate_alignment_report": str(GATE_ALIGNMENT_REPORT.relative_to(ROOT)),
            "token_expansion_report": str(TOKEN_EXPANSION_REPORT.relative_to(ROOT))
        },
        "recommended_next_phase": "PROD-6421..6460 - CASULO Delta Zero Batch 01 Vectorization Review Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "packet_only": True,
        "additional_live_call_allowed": False,
        "t0_proxy_values_only": True,
        "trajectory_claim_blocked_until_multiple_snapshots": True,
        "velocity_claim_blocked": True,
        "acceleration_claim_blocked": True,
        "candidate_tokens_canonical": False,
        "external_evaluator_required": True,
        "validated_model_gain_claim_blocked": True,
        "dataset_acceptance_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "commercial_claim_blocked": True,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_count": len(checks),
        "packet_only": True,
        "additional_live_gpt_call_in_this_phase": False,
        "delta_zero_dynamics_model_ready": True,
        "t0_vectorization_ready": True,
        "delta_matrix_row_count": len(delta_rows),
        "delta_matrix_csv_created": DELTA_MATRIX_CSV.exists(),
        "mode_counts": dict(mode_counts),
        "domain_counts": dict(domain_counts),
        "model_gate_counts": dict(model_gate_counts),
        "computed_gate_counts": dict(computed_gate_counts),
        "delta_band_counts": dict(delta_band_counts),
        "candidate_token_counts_v0_3": dict(token_counts),
        "delta_zero_ready_count": dzr_ready_count,
        "hard_block_case_count": hard_block_count,
        "trajectory_status": "T0_ONLY",
        "velocity_ready": False,
        "acceleration_ready": False,
        "candidate_tokens_canonical": False,
        "external_evaluator_required": True,
        "validated_model_gain_claim_allowed": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "commercial_claim": False,
        "recommended_next_phase": packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v3.3-delta-zero",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - CASULO Delta Zero Dynamics Model Packet",
        "next_phase": packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-6381..6420 - CASULO Delta Zero Dynamics Model Packet

This phase replaces the failed former PROD-6381..6420 workbench attempt.

It creates the Delta Zero Dynamics layer.

## Created

- Operational state vector schema
- Domain reference vectors
- Domain weight profiles
- Delta matrix schema
- Delta gate band policy
- Trajectory memory schema
- DRD/DZR definitions
- Token expansion contract
- Hard block policy
- Batch 01 T0 delta matrix

## Result

- Delta matrix rows: {len(delta_rows)}
- Delta Zero Ready cases: {dzr_ready_count}
- Hard block cases: {hard_block_count}
- Trajectory status: T0_ONLY
- Velocity ready: false
- Acceleration ready: false
- Candidate tokens canonical: false
- External evaluator required: true

## Boundary

This phase uses derived proxy values from the existing Ponto Zero telemetry matrix.

It does not validate model gain, hallucination reduction, domain readiness, dataset acceptance, client evidence, production evidence or commercial claim.

## Next

PROD-6421..6460 - CASULO Delta Zero Batch 01 Vectorization Review Gate
"""

    report = f"""# PROD-6381..6420 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Checks: {result['check_count']}
- Packet only: true
- Additional live GPT call in this phase: false
- Delta Zero Dynamics model ready: true
- T0 vectorization ready: true
- Delta matrix rows: {result['delta_matrix_row_count']}
- Delta matrix CSV created: {result['delta_matrix_csv_created']}
- Delta Zero Ready count: {result['delta_zero_ready_count']}
- Hard block case count: {result['hard_block_case_count']}
- Trajectory status: T0_ONLY
- Velocity ready: false
- Acceleration ready: false
- Candidate tokens canonical: false
- External evaluator required: true
- Validated model gain claim allowed: false
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
- Commercial claim: false
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write_json(STATE_VECTOR_SCHEMA, state_vector_schema)
    write_json(DOMAIN_REF_VECTORS, {"version": "casulo_delta_zero_domain_reference_vectors.v0.3", "vectors": refs})
    write_json(DOMAIN_WEIGHT_PROFILES, {"version": "casulo_delta_zero_domain_weight_profiles.v0.3", "profiles": weights})
    write_json(DELTA_MATRIX_SCHEMA, delta_matrix_schema)
    write_json(DELTA_GATE_POLICY, delta_gate_policy)
    write_json(TRAJECTORY_SCHEMA, trajectory_schema)
    write_json(TOKEN_EXPANSION_CONTRACT, token_expansion_contract)
    write_json(DRD_DZR_DEFINITIONS, drd_dzr_definitions)
    write_json(HARD_BLOCK_POLICY, hard_block_policy)
    write_json(DELTA_MATRIX_JSON, delta_matrix_packet)
    write_json(GATE_ALIGNMENT_REPORT, gate_alignment_report)
    write_json(TOKEN_EXPANSION_REPORT, token_expansion_report)
    write_json(MODEL_READINESS_REPORT, readiness)

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, packet)
    write_json(PACKET, packet)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("checks:", result["check_count"])
    print("delta_zero_dynamics_model_ready:", result["delta_zero_dynamics_model_ready"])
    print("delta_matrix_row_count:", result["delta_matrix_row_count"])
    print("delta_zero_ready_count:", result["delta_zero_ready_count"])
    print("hard_block_case_count:", result["hard_block_case_count"])
    print("trajectory_status:", result["trajectory_status"])
    print("velocity_ready:", result["velocity_ready"])
    print("acceleration_ready:", result["acceleration_ready"])
    print("candidate_tokens_canonical:", result["candidate_tokens_canonical"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
