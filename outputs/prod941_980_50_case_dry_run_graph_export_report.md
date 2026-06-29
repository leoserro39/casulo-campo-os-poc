# PROD-941..980 Controlled 50-Case Dry-Run Simulation and Graph Export Stub

- Status: `PASS`
- Case count: `50`
- Graph node count: `313`
- Graph relationship count: `350`
- Decision: `READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY`
- External execution allowed: `False`
- Graph write allowed: `False`
- Neo4j connection allowed: `False`
- Automatic threshold mutation allowed: `False`

## Gate Distribution
- `ANSWER_ALLOWED`: `19`
- `HUMAN_REVIEW_REQUIRED`: `30`
- `UNSUPPORTED_BLOCKED`: `1`

## Risk Band Distribution
- `CRITICAL`: `11`
- `HIGH`: `24`
- `MEDIUM`: `15`

## Risk Telemetry
- Adjusted risk min/avg/max: `33.75` / `63.734` / `100.0`
- Live delta min/avg/max: `0.2481` / `0.5705` / `0.8225`

## Graph Export Stub
- Nodes JSONL: `outputs/prod941_980_graph_export_nodes.jsonl`
- Relationships JSONL: `outputs/prod941_980_graph_export_relationships.jsonl`
- Node count: `313`
- Relationship count: `350`

## Diagnostic Cases
- `EXP50-045` `fleet_maintenance_ops` `clean_controlled_answer` gate `ANSWER_ALLOWED` risk `55.9` band `HIGH`
- `EXP50-047` `fleet_maintenance_ops` `conflicting_information` gate `HUMAN_REVIEW_REQUIRED` risk `96.95` band `CRITICAL`
- `EXP50-049` `ecommerce_order_ops` `direct_execution_block` gate `UNSUPPORTED_BLOCKED` risk `100.0` band `CRITICAL`

## Next Recommended Bundle
- `PROD-981 Business Diagnostic Report Pack and Graph Adapter Boundary`
