# PROD-321..340 Human Review Pack

This pack is review-only. It does not create GitHub issues, activate production, merge code, or make client-facing claims.

## Priority Review Queue
### REAL-GRAPH-001-ONBOARDING-ISSUE-CANDIDATE-002 — [P0_BLOCKER] REAL-GRAPH-001-ONBOARDING: evidence required for delta_evidence
- Case: `REAL-GRAPH-001-ONBOARDING`
- Priority: `P0_BLOCKER`
- Delta: `delta_evidence`
- Review route: `evidence_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Attach source/evidence before committing graph relation.

### REAL-GRAPH-002-DOCUMENT-AUDIT-ISSUE-CANDIDATE-002 — [P0_BLOCKER] REAL-GRAPH-002-DOCUMENT-AUDIT: evidence required for delta_evidence
- Case: `REAL-GRAPH-002-DOCUMENT-AUDIT`
- Priority: `P0_BLOCKER`
- Delta: `delta_evidence`
- Review route: `evidence_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Attach source/evidence before committing graph relation.

### REAL-GRAPH-003-SOFTWARE-REVIEW-ISSUE-CANDIDATE-001 — [P0_BLOCKER] REAL-GRAPH-003-SOFTWARE-REVIEW: evidence required for delta_evidence
- Case: `REAL-GRAPH-003-SOFTWARE-REVIEW`
- Priority: `P0_BLOCKER`
- Delta: `delta_evidence`
- Review route: `evidence_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Attach source/evidence before committing graph relation.

### REAL-GRAPH-004-RULE-POLICY-ISSUE-CANDIDATE-003 — [P0_BLOCKER] REAL-GRAPH-004-RULE-POLICY: evidence required for delta_evidence
- Case: `REAL-GRAPH-004-RULE-POLICY`
- Priority: `P0_BLOCKER`
- Delta: `delta_evidence`
- Review route: `evidence_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Attach source/evidence before committing graph relation.

### REAL-GRAPH-001-ONBOARDING-ISSUE-CANDIDATE-001 — [P0_BLOCKER] REAL-GRAPH-001-ONBOARDING: domain_owner required for delta_domain
- Case: `REAL-GRAPH-001-ONBOARDING`
- Priority: `P0_BLOCKER`
- Delta: `delta_domain`
- Review route: `domain_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Assign domain owner for sensitive decision.

### REAL-GRAPH-002-DOCUMENT-AUDIT-ISSUE-CANDIDATE-001 — [P0_BLOCKER] REAL-GRAPH-002-DOCUMENT-AUDIT: arbitration required for delta_conflict
- Case: `REAL-GRAPH-002-DOCUMENT-AUDIT`
- Priority: `P0_BLOCKER`
- Delta: `delta_conflict`
- Review route: `human_arbitrator`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Resolve conflicting sources/states/rules.

### REAL-GRAPH-004-RULE-POLICY-ISSUE-CANDIDATE-001 — [P0_BLOCKER] REAL-GRAPH-004-RULE-POLICY: arbitration required for delta_conflict
- Case: `REAL-GRAPH-004-RULE-POLICY`
- Priority: `P0_BLOCKER`
- Delta: `delta_conflict`
- Review route: `human_arbitrator`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Resolve conflicting sources/states/rules.

### REAL-GRAPH-004-RULE-POLICY-ISSUE-CANDIDATE-002 — [P0_BLOCKER] REAL-GRAPH-004-RULE-POLICY: domain_owner required for delta_domain
- Case: `REAL-GRAPH-004-RULE-POLICY`
- Priority: `P0_BLOCKER`
- Delta: `delta_domain`
- Review route: `domain_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Assign domain owner for sensitive decision.

### REAL-GRAPH-003-SOFTWARE-REVIEW-ISSUE-CANDIDATE-002 — [P0_BLOCKER] REAL-GRAPH-003-SOFTWARE-REVIEW: production_readiness required for delta_production
- Case: `REAL-GRAPH-003-SOFTWARE-REVIEW`
- Priority: `P0_BLOCKER`
- Delta: `delta_production`
- Review route: `production_readiness_owner`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Provide auth, audit, rollback, monitoring and support plan.

### REAL-GRAPH-002-DOCUMENT-AUDIT-ISSUE-CANDIDATE-003 — [P0_BLOCKER] REAL-GRAPH-002-DOCUMENT-AUDIT: human_review required for delta_human_review
- Case: `REAL-GRAPH-002-DOCUMENT-AUDIT`
- Priority: `P0_BLOCKER`
- Delta: `delta_human_review`
- Review route: `human_reviewer`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Route to human owner or reviewer.

### REAL-GRAPH-003-SOFTWARE-REVIEW-ISSUE-CANDIDATE-003 — [P0_BLOCKER] REAL-GRAPH-003-SOFTWARE-REVIEW: test_plan required for delta_execution
- Case: `REAL-GRAPH-003-SOFTWARE-REVIEW`
- Priority: `P0_BLOCKER`
- Delta: `delta_execution`
- Review route: `technical_reviewer`
- Recommended decision: `APPROVE_FOR_HUMAN_REVIEW_ISSUE`
- Human approval required: `True`

#### Required action
Provide runtime, dependency and test context before execution.

### REAL-GRAPH-003-SOFTWARE-REVIEW-ISSUE-CANDIDATE-004 — [P1_REVIEW] REAL-GRAPH-003-SOFTWARE-REVIEW: calibration_review required for delta_model_behavior
- Case: `REAL-GRAPH-003-SOFTWARE-REVIEW`
- Priority: `P1_REVIEW`
- Delta: `delta_model_behavior`
- Review route: `calibration_owner`
- Recommended decision: `APPROVE_FOR_REVIEW_QUEUE`
- Human approval required: `True`

#### Required action
Review anomaly pattern against calibration history.

