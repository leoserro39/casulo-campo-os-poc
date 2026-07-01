# CASULO Delta Zero External Evaluator Case EXT-EVAL-B01H-002

## Identification

- Case ID: EXT-EVAL-B01H-002
- Execution ID: tic_si_itsm_01__stack_gpt
- Scenario ID: tic_si_itsm_01
- Domain: TIC/SI / ITSM
- Mode: STACK_GPT

## Gates and Delta

- Model gate: INSUFFICIENT_EVIDENCE
- Computed gate: HUMAN_REVIEW_REQUIRED
- Delta score: 0.4439
- Delta band: 0.31-0.60
- Delta gate mismatch: 0.5
- DRD: 0.439
- DZR: 0.561
- Delta Zero Ready: False
- Hard blocks: ['thin_evidence']

## State Vector

{
  "risk_score": 0.605,
  "evidence_density": 0.2,
  "confidence_level": 0.624,
  "ambiguity_level": 0.75,
  "dependency_weight": 0.6,
  "impact_level": 0.6,
  "governance_requirement": 0.7833,
  "reversibility_level": 0.44,
  "readiness_score": 0.4169,
  "exposure_level": 0.45
}

## Reference Vector

{
  "risk_score": 0.1,
  "evidence_density": 0.85,
  "confidence_level": 0.8,
  "ambiguity_level": 0.1,
  "dependency_weight": 0.25,
  "impact_level": 0.4,
  "governance_requirement": 0.5,
  "reversibility_level": 0.85,
  "readiness_score": 0.85,
  "exposure_level": 0.05
}

## Domain Weight Profile

{
  "risk_score": 1.0,
  "evidence_density": 1.2,
  "confidence_level": 0.9,
  "ambiguity_level": 1.0,
  "dependency_weight": 1.25,
  "impact_level": 0.8,
  "governance_requirement": 0.8,
  "reversibility_level": 1.25,
  "readiness_score": 1.0,
  "exposure_level": 1.25
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
