# PROD-1901..1940 - Real Response Capture Plan and Manual Evidence Intake

This phase creates a controlled plan for real GPT response capture and manual evidence intake.

It does not connect GPT.
It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not approve thresholds.
It does not approve final weights.
It does not authorize client-facing claims.

## Purpose

Previous response evidence was simulated fixture evidence.

Before final calibration, CASULO must capture or receive real GPT responses with explicit provenance.

This phase prepares:

- manual response capture format;
- prompt pack for pure GPT response;
- prompt pack for stack-grounded response;
- manual evidence intake schema;
- review and exclusion rules;
- provenance labels;
- calibration eligibility rules.

## Capture modes

- `MANUAL_PASTED_GPT_PURE`: user manually pastes a GPT answer without CASULO stack context.
- `MANUAL_PASTED_GPT_STACK_GROUNDED`: user manually pastes a GPT answer produced with CASULO context packet.
- `CUSTOM_GPT_ACTION_CAPTURED`: future controlled capture through approved Custom GPT action.
- `API_CAPTURED`: future approved API capture.
- `SIMULATED_FIXTURE`: synthetic fixture; useful for harness, not real calibration.
- `UNKNOWN_OR_UNTRUSTED`: excluded from calibration.

## Boundary

Manual capture is allowed.

Automatic GPT call is not allowed.
Custom GPT connection is not approved.
Final threshold calibration remains blocked.
