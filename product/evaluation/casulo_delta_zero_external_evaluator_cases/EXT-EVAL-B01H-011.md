# CASULO Delta Zero External Evaluator Case EXT-EVAL-B01H-011

## Identification

- Case ID: EXT-EVAL-B01H-011
- Execution ID: vesselflow_operacao_maritima_02__stack_gpt
- Scenario ID: vesselflow_operacao_maritima_02
- Domain: VesselFlow / Operação marítima
- Mode: STACK_GPT

## Gates and Delta

- Model gate: BLOCKED
- Computed gate: HUMAN_REVIEW_REQUIRED
- Delta score: 0.3512
- Delta band: 0.31-0.60
- Delta gate mismatch: 0.5
- DRD: 0.3295
- DZR: 0.6705
- Delta Zero Ready: False
- Hard blocks: []

## State Vector

{
  "risk_score": 0.6604,
  "evidence_density": 0.635,
  "confidence_level": 0.888,
  "ambiguity_level": 0.5413,
  "dependency_weight": 0.5,
  "impact_level": 0.75,
  "governance_requirement": 0.7833,
  "reversibility_level": 0.44,
  "readiness_score": 0.627,
  "exposure_level": 0.45
}

## Reference Vector

{
  "risk_score": 0.08,
  "evidence_density": 0.85,
  "confidence_level": 0.8,
  "ambiguity_level": 0.1,
  "dependency_weight": 0.3,
  "impact_level": 0.35,
  "governance_requirement": 0.65,
  "reversibility_level": 0.8,
  "readiness_score": 0.85,
  "exposure_level": 0.05
}

## Domain Weight Profile

{
  "risk_score": 1.2,
  "evidence_density": 1.25,
  "confidence_level": 0.9,
  "ambiguity_level": 1.0,
  "dependency_weight": 0.8,
  "impact_level": 1.3,
  "governance_requirement": 0.8,
  "reversibility_level": 0.9,
  "readiness_score": 1.0,
  "exposure_level": 1.2
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
    "DELTA_MEDIUM",
    "EVIDENCE_THIN",
    "READ_ONLY_STATE"
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
