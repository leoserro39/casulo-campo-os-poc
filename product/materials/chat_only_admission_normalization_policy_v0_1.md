# Chat-Only Admission Normalization Policy v0.1

Chat-only input with `source_authority=UNVERIFIED_USER_SIGNAL` is not documentary evidence.

Runtime rule:

- downgrade chat-only `EVIDENCE`, `ARTIFACT`, `METRIC`, or `RULE` to `INFERENCE/unverified_chat_signal`;
- force `can_support_claim=false`;
- cap evidence density, confidence and traceability;
- preserve production, client claim, commercial claim and threshold locks.
