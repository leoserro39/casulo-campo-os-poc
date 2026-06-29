# PROD-601B..620B Telemetry Correlation Calibration

- Status: `PASS`
- Case count: `1200`
- Metric count: `14`
- Strong correlations: `29`
- Adjustment candidates: `4`
- Decision: `READY_FOR_TELEMETRY_GUIDED_CALIBRATION_NOT_AUTO_MUTATION`

## Strong Correlations
- `unsupported_numeric` x `safe_block_success` = `1.0` (positive, strong)
- `stress_score` x `useful_output_rate` = `-0.936` (negative, strong)
- `cubo_risk` x `delta_control` = `-0.9151` (negative, strong)
- `stress_score` x `direct_risk` = `0.8899` (positive, strong)
- `stress_score` x `cubo_risk` = `0.873` (positive, strong)
- `cubo_risk` x `useful_output_rate` = `-0.8639` (negative, strong)
- `direct_risk` x `useful_output_rate` = `-0.8604` (negative, strong)
- `cubo_risk` x `relative_risk_reduction_pct` = `-0.8372` (negative, strong)
- `relative_risk_reduction_pct` x `evidence_coverage` = `0.8313` (positive, strong)
- `human_review_numeric` x `safe_review_success` = `0.8264` (positive, strong)
- `stress_score` x `delta_control` = `-0.7837` (negative, strong)
- `direct_risk` x `cubo_risk` = `0.7716` (positive, strong)
- `delta_control` x `useful_output_rate` = `0.7635` (positive, strong)
- `relative_risk_reduction_pct` x `delta_control` = `0.7548` (positive, strong)
- `direct_risk` x `delta_control` = `-0.7089` (negative, moderate)
- `delta_control` x `anomaly_numeric` = `-0.7075` (negative, moderate)
- `direct_risk` x `anomaly_numeric` = `0.7024` (positive, moderate)
- `cubo_risk` x `anomaly_numeric` = `0.6877` (positive, moderate)
- `risk_reduction` x `relative_risk_reduction_pct` = `0.6758` (positive, moderate)
- `risk_reduction` x `evidence_coverage` = `0.6723` (positive, moderate)
- `stress_score` x `anomaly_numeric` = `0.6619` (positive, moderate)
- `cubo_risk` x `evidence_coverage` = `-0.6584` (negative, moderate)
- `relative_risk_reduction_pct` x `useful_output_rate` = `0.5791` (positive, moderate)
- `anomaly_numeric` x `human_review_numeric` = `0.5789` (positive, moderate)
- `useful_output_rate` x `anomaly_numeric` = `-0.5667` (negative, moderate)

## Adjustment Candidates
- `ADJ-001` `safe_block_reclassification` -> UNSUPPORTED_BLOCKED on unsupported input should count as safe_block_success, not true failure.
- `ADJ-002` `safe_review_reclassification` -> HUMAN_REVIEW_REQUIRED for high-risk profiles should count as safe_review_success when gate/evidence trace exists.
- `ADJ-003` `threshold_split` -> If cubo_risk >= 45 or evidence_coverage < 70, require evidence/context justification or review.
- `ADJ-004` `family_freeze_candidate` -> Freeze parser/extraction as strong candidate family while preserving review/block profiles.

## Operating Zones
- `allow_zone` cases `640` cubo_risk `[10.0, 53.0]` mean `38.2656`
- `review_zone` cases `440` cubo_risk `[32.0, 64.0]` mean `50.0909`
- `block_zone` cases `120` cubo_risk `[51.0, 72.0]` mean `59.25`
