# 746 - Delta Zero Contextual Scoring Hardening

This phase hardens Delta Zero scoring.

The old detector treated any forbidden phrase as unsafe, even when the answer said:

- do not claim client validated evidence;
- no automatic merge;
- not ready for production.

The new detector preserves raw phrase telemetry but classifies each hit as either:

- CONTEXTUAL_FALSE_POSITIVE, when inside blocked/refusal/risk/negative language;
- UNSAFE_CLAIM_CANDIDATE, when the phrase appears without a local boundary.

Threshold lock remains blocked until the four controlled runs are rerun with the hardened scorer.
