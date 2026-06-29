# PROD-721..760 Controlled 20-Case Business Pilot Pack

- Status: `PASS`
- Case count: `20`
- Decision: `READY_FOR_HUMAN_REVIEWED_20_CASE_BUSINESS_PILOT`
- External execution allowed: `False`
- Automatic threshold mutation allowed: `False`

## Gate Distribution
- `ALLOW_WITH_WARNING`: `1`
- `ANSWER_ALLOWED`: `3`
- `EVIDENCE_REQUIRED`: `2`
- `HUMAN_REVIEW_REQUIRED`: `8`
- `UNSUPPORTED_BLOCKED`: `6`

## Output Mode Distribution
- `ALLOW_WITH_WARNING`: `1`
- `ANSWER`: `3`
- `BLOCKED`: `6`
- `EVIDENCE_REQUEST`: `2`
- `HUMAN_REVIEW_PACKET`: `8`

## Risk Band Distribution
- `CRITICAL`: `6`
- `HIGH`: `6`
- `LOW`: `3`
- `MEDIUM`: `5`

## Feedback Distribution
- `BLOCK_APPROPRIATE`: `6`
- `NEEDS_MORE_EVIDENCE`: `2`
- `OUTPUT_USEFUL`: `4`
- `OVER_CONSERVATIVE_CANDIDATE`: `2`
- `REVIEW_APPROPRIATE`: `6`

## Calibration Recommendations
- `PILOT-CAL-001` `over_conservative_review`: Inspect medium-risk controlled active domain review packets for possible ALLOW_WITH_WARNING or EVIDENCE_REQUEST split. / auto_apply `False`
- `PILOT-CAL-002` `block_policy`: Maintain external execution and unsupported-domain block policy unless false block candidates appear in reviewed feedback. / auto_apply `False`
- `PILOT-CAL-003` `allow_policy`: No threshold relaxation without human-reviewed false allow scan. / auto_apply `False`
- `PILOT-CAL-004` `pilot_expansion`: After human review of this 20-case pack, expand to 50 controlled cases only if no false allow candidates are confirmed. / auto_apply `False`

## Next Recommended Bundle
- `PROD-761 Human Review Pilot Board and Decision Ledger`
