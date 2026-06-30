# PROD-1301..1340 - Graph Retrieval Gain Evaluation

This phase evaluates whether the Neo4j sandbox projection improves operational retrieval compared with flat repository exports.

It is sandbox-only.

It does not authorize production graph writes, client-facing claims, automatic decisions, credential handling, or threshold mutation.

## Evaluation Focus

- Confirm imported graph counts.
- Measure case-to-context reachability.
- Measure reachability from cases to Evidence, RiskSignal, Gate, OutputMode, HallucinationBudget, and Domain.
- Produce a controlled internal report.
- Prepare the next decision: whether graph-backed retrieval is useful enough for the next controlled agent/runtime step.
