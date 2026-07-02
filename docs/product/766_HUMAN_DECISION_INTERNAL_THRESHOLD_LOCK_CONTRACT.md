# 766 - Human Decision Record and Internal Threshold Lock Contract

This phase records a human decision over the graph-backed threshold proposal.

Possible decisions:
- APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY
- REQUEST_MORE_EVIDENCE
- REJECT_THRESHOLD_LOCK

Approval creates an internal-only threshold lock contract.

This does not allow:
- client-facing validation claims;
- production activation;
- commercial claims;
- validated hallucination reduction claims;
- production Neo4j writes.
