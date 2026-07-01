# CASULO Delta Zero Real Test Input Pack Template v0.3

This is a template only. Do not place secrets, credentials, personal data, client-confidential data or production commands here.

## real_case_001_sanitized_input.md

### Domain
TBD

### Task objective
TBD

### Sanitized real situation
TBD

### Known evidence
- TBD

### Source boundaries
- Allowed source: TBD
- Forbidden source: TBD

### Allowed actions
- Explain state
- Identify gaps
- Recommend safe next step
- Request human review when required

### Blocked actions
- Production activation
- Client-facing validated claim
- Commercial claim
- Dataset acceptance
- Model-gain claim
- Hallucination-reduction claim
- Real-world side effect
- Use of secrets or PII

### Expected gate
TBD

### Human review rubric
Use product/evaluation/casulo_delta_zero_controlled_real_test_rubric_v0_3.json

### Stop criteria
Stop if the input contains PII, secrets, production side effects, missing evidence boundaries or missing blocked actions.
