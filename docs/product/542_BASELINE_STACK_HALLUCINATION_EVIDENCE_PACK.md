# PROD-1621..1660 - Baseline vs Stack vs Hallucination Evidence Pack

This phase materializes comparative evidence between:

- baseline/pure responses before stack grounding;
- stack-grounded responses using CASULO graph context semantics;
- hallucinating/failure responses that ignore evidence, gates and blocked actions.

It does not perform final calibration.
It does not set final thresholds.
It does not connect GPT.
It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not authorize client-facing claims.

## Purpose

Show materially how CASULO stack changes response behavior.

The report must make visible:

- response patterns;
- boundary discipline;
- graph behavior;
- hallucination risk proxy;
- violation patterns;
- confidence differences;
- why stack-grounded responses are safer than pure or hallucinating responses.

## Calibration Boundary

This is comparative evidence only.

Final calibration requires larger datasets, real or anonymized data, actual GPT responses and human review thresholds.
