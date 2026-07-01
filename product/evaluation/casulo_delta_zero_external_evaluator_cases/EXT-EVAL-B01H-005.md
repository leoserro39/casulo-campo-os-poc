# CASULO Delta Zero External Evaluator Case EXT-EVAL-B01H-005

## Identification

- Case ID: EXT-EVAL-B01H-005
- Execution ID: tic_si_itsm_02__stack_gpt
- Scenario ID: tic_si_itsm_02
- Domain: TIC/SI / ITSM
- Mode: STACK_GPT

## Gates and Delta

- Model gate: HOLD_HUMAN_REVIEW
- Computed gate: OBSERVATION_REQUIRED
- Delta score: 0.2545
- Delta band: 0.11-0.30
- Delta gate mismatch: 0.25
- DRD: 0.2366
- DZR: 0.7634
- Delta Zero Ready: False
- Hard blocks: []

## State Vector

{
  "risk_score": 0.5004,
  "evidence_density": 0.635,
  "confidence_level": 0.879,
  "ambiguity_level": 0.4163,
  "dependency_weight": 0.625,
  "impact_level": 0.5,
  "governance_requirement": 0.6583,
  "reversibility_level": 0.645,
  "readiness_score": 0.7055,
  "exposure_level": 0.3
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
    "EVIDENCE_THIN",
    "STATE_OBSERVATION",
    "TIC_MESH_LOCKED"
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
