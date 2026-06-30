# PROD-2101..2140 - OHRI Governance Correction and Dual Ranking Model

This phase corrects the previous OHRI v0.1 governance issue.

The previous phase was committed and tagged even though the generated output was FAIL.

This is treated as useful operational evidence:

A process without a hard commit gate can allow failed analytical artifacts to be versioned.

## Correction

The correction is not to force parser grounding to be top five in operational risk.

The better model separates two rankings:

1. Operational Hallucination Risk Index (OHRI)
   - Measures operational danger.
   - High risk includes unsafe merge, production readiness leakage, repo mismatch, API contract hallucination and missing contract.

2. Operational Benchmark Priority Index (OBPI)
   - Measures which benchmark should be built first.
   - Parser grounding can rank first because it is measurable, recurring, demonstrable and low-side-effect.

## Boundary

This phase is corrective and heuristic.

It does not calibrate thresholds.
It does not use real client data.
It does not call GPT.
It does not call Codex.
It does not authorize merge, production activation or client-facing claims.
