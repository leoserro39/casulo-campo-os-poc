# Minimum Process View for Gain and Real Calibration

## Current position

The CASULO Campo OS calibration cycle now has a minimum auditable process:

1. Controlled scenario matrix.
2. Equal execution across PURE_GPT, STACK_GPT and CASULO_EXOCORTEX_STACK.
3. Hardened capture of full output and parsed JSON.
4. Self-reported behavioral metric aggregation.
5. External evaluator packet.
6. Future external evaluator execution.
7. Future calibration decision gate.
8. Future dataset candidate gate.

## Practical meaning

The process is ready to measure real gain, but the gain has not yet been externally validated.

## Decision boundary

Technical pipeline and capture readiness can be reported internally.

Model gain, hallucination reduction, production readiness, client evidence, commercial value and dataset acceptance remain blocked until external evaluation and human gate approval.

## Recommended next move

Run the external evaluator execution gate and then score the 36 cases independently.
