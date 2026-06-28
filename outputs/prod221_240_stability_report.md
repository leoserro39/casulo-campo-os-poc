# PROD-221..240 Multi-Seed Stability and Drift Report

- Status: `PASS`
- Seeds: `[101, 202, 303, 404, 505]`
- Cases per seed: `300`
- Total cases: `1500`
- Decision: `STABLE_ENOUGH_FOR_PROVISIONAL_SYNTHETIC_THRESHOLDS`

## Stability
- `avg_direct_hallucination` mean `83.95` std `1.2503` cv `0.0149` range `3.81`
- `avg_casulo_hallucination` mean `27.51` std `0.5896` cv `0.0214` range `1.85`
- `avg_hallucination_reduction` mean `56.44` std `0.7129` cv `0.0126` range `1.96`
- `avg_delta_control` mean `86.07` std `0.1003` cv `0.0012` range `0.26`
- `avg_residual_delta` mean `52.06` std `0.8255` cv `0.0159` range `2.35`
- `avg_evidence_coverage` mean `46.83` std `0.7966` cv `0.017` range `2.3`
- `anomaly_rate` mean `0.17` std `0.0107` cv `0.062` range `0.03`

## Drift

- Status: `PASS`
- Flags: `[]`

## Anomaly Clusters

- Total anomalies: `260`
- By metric: `{'low_ambiguity_high_hallucination': 100, 'hallucination_reduction': 57, 'casulo_hallucination': 27, 'evidence_coverage': 26, 'delta_control_score': 25, 'residual_delta_index': 20, 'ambiguity_delta_control_interaction': 5}`
- By family: `{'rule_extraction': 81, 'parser_documental': 78, 'software_review': 65, 'audit_documental': 36}`
- By ambiguity bucket: `{'A0_very_low': 177, 'A4_extreme': 40, 'A3_high': 17, 'A1_low': 16, 'A2_medium': 10}`

## Recommendations

- status: `PROVISIONAL`
- hallucination_attention_threshold: `35`
- hallucination_review_threshold: `45`
- delta_control_attention_threshold: `82`
- delta_control_review_threshold: `80`
- evidence_coverage_attention_threshold: `45`
- anomaly_rate_attention_threshold: `0.25`
- note: `Synthetic thresholds only. Confirm with anonymized real documents before external claims.`
