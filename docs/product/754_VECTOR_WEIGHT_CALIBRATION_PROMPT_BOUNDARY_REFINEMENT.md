# 754 - Vector Weight Calibration and Prompt Boundary Refinement

This phase calibrates the vector scorer after the contextual rerun.

Reason:
- Delta Zero contextual score reached a safe structural result.
- Raw forbidden strings remained contextual false positives.
- No unsafe forbidden claim was observed.
- Vector v2 was still too strict because lexical density had too much influence.

Change:
- Vector scoring now blends contextual Delta Zero score, claim-boundary preservation, sections, gate, evidence, risk, prompt boundary and lexical telemetry.
- Prompt variants now enforce explicit section headings and explicit blocked-action language.

Boundary:
- No threshold lock yet.
- No client claim.
- No production activation.
