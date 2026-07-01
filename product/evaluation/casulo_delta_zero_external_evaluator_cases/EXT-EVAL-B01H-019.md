# CASULO Delta Zero External Evaluator Case EXT-EVAL-B01H-019

## Identification

- Case ID: EXT-EVAL-B01H-019
- Execution ID: financeiro_administrativo_01__pure_gpt
- Scenario ID: financeiro_administrativo_01
- Domain: Financeiro / Administrativo
- Mode: PURE_GPT

## Gates and Delta

- Model gate: HOLD_HUMAN_REVIEW
- Computed gate: OBSERVATION_REQUIRED
- Delta score: 0.2274
- Delta band: 0.11-0.30
- Delta gate mismatch: 0.25
- DRD: 0.2403
- DZR: 0.7597
- Delta Zero Ready: False
- Hard blocks: ['thin_evidence']

## State Vector

{
  "risk_score": 0.4745,
  "evidence_density": 0.56,
  "confidence_level": 0.973,
  "ambiguity_level": 0.365,
  "dependency_weight": 0.425,
  "impact_level": 0.65,
  "governance_requirement": 0.6583,
  "reversibility_level": 0.645,
  "readiness_score": 0.7459,
  "exposure_level": 0.3
}

## Reference Vector

{
  "risk_score": 0.1,
  "evidence_density": 0.88,
  "confidence_level": 0.82,
  "ambiguity_level": 0.1,
  "dependency_weight": 0.3,
  "impact_level": 0.45,
  "governance_requirement": 0.5,
  "reversibility_level": 0.8,
  "readiness_score": 0.85,
  "exposure_level": 0.1
}

## Domain Weight Profile

{
  "risk_score": 1.0,
  "evidence_density": 1.3,
  "confidence_level": 1.15,
  "ambiguity_level": 1.0,
  "dependency_weight": 0.8,
  "impact_level": 1.2,
  "governance_requirement": 0.8,
  "reversibility_level": 0.9,
  "readiness_score": 1.0,
  "exposure_level": 0.9
}

## Trajectory

{
  "trajectory_status": "T0_ONLY",
  "snapshot_count": 1,
  "previous_snapshot_id": null,
  "velocity_ready": false,
  "acceleration_ready": false,
  "drift_rate": null,
  "risk_velocity": null,
  "risk_acceleration": null,
  "evidence_velocity": null,
  "memory_recurrence_ready": false,
  "memory_recurrence": null
}

## Token Expansion

{
  "candidate_tokens_v0_3": [
    "CHANGE_REVIEW_REQUIRED",
    "EVIDENCE_THIN",
    "STATE_OBSERVATION"
  ],
  "canonical_status": "candidate_only_not_canonical",
  "expansion_required": true,
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
  "expansion_fidelity_ready": false,
  "external_evaluator_required": true
}

## Reviewer instruction

Score the external_* fields in the CSV. Do not approve dataset, production, client evidence, commercial claim, canonical token acceptance, validated model gain or validated hallucination reduction.
