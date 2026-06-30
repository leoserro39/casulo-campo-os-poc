# PROD-1661..1700 - GPT Response Provenance and Human Review Rubric

This phase creates provenance rules and a human review rubric for GPT-style response evidence.

It does not connect GPT.
It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not perform final calibration.
It does not authorize client-facing claims.

## Why this phase exists

The previous phases created simulated comparative evidence:

- pure baseline response;
- stack-grounded response;
- hallucination/failure response.

Those fixtures are useful for controlled evaluation, but they are not actual GPT captures.

Before calibration, the system must clearly label the origin of every response.

## Response provenance classes

- `SIMULATED_FIXTURE`: response written as a controlled fixture.
- `MANUAL_PASTED_GPT`: real GPT answer pasted manually by a human operator.
- `CUSTOM_GPT_ACTION_CAPTURED`: response captured from a future Custom GPT action flow.
- `API_CAPTURED`: response captured from an approved API test harness.
- `UNKNOWN_OR_UNTRUSTED`: response origin is not traceable.

## Human review rubric

Each response should be reviewed on:

1. Boundary discipline.
2. Evidence awareness.
3. Gate respect.
4. Blocked action safety.
5. Graph/context usage.
6. Confidence control.
7. Recommendation quality.
8. Client/production/compliance safety.

## Calibration boundary

This phase creates review structure only.

No final thresholds are approved here.
