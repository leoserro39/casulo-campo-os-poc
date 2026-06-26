"""Canonical model names for the CASULO Workbench v0.1."""

CANONICAL_NODES = [
    "Company", "Case", "Domain", "ComputableBranch", "Source", "Evidence",
    "DataQualityScore", "OperationalState", "Intersection", "Delta", "Gate",
    "Solution", "ExecutorTask", "MonitoringCycle", "Snapshot", "LedgerEvent",
]

CANONICAL_EDGES = [
    "HAS_DOMAIN", "HAS_BRANCH", "CONSUMES_SOURCE", "PRODUCES_EVIDENCE",
    "SUPPORTS_STATE", "CONTRADICTS_STATE", "INTERSECTS_WITH", "GENERATES_DELTA",
    "HAS_GATE", "ALLOWS_SOLUTION", "BLOCKS_SOLUTION", "IMPLEMENTED_BY",
    "UPDATES_STATE", "RECORDED_IN_LEDGER",
]
