# PROD-201..220 Stochastic Calibration and Anomaly Study

- Status: `PASS`
- Cases: `500`
- Avg direct hallucination: `84.09`
- Avg CASULO hallucination: `27.73`
- Avg hallucination reduction: `56.35`
- Avg delta control: `85.97`
- Avg residual delta: `53.44`
- Avg evidence coverage: `45.48`

## Interpretation

Synthetic randomized study confirms the correct next phase: study fluctuation by ambiguity, missingness, conflict, noise and family before touching real company processes. Calibration should focus on anomaly clusters and behavior curves, not isolated cases.

## Ambiguity Behavior
- `A0_very_low` count `107` | CASULO hallucination `22.5` | reduction `50.04` | delta control `88.33` | residual delta `43.09`
- `A1_low` count `92` | CASULO hallucination `24.78` | reduction `53.72` | delta control `86.97` | residual delta `49.07`
- `A2_medium` count `104` | CASULO hallucination `27.5` | reduction `57.48` | delta control `86.06` | residual delta `53.83`
- `A3_high` count `89` | CASULO hallucination `31.55` | reduction `59.91` | delta control `84.71` | residual delta `59.15`
- `A4_extreme` count `108` | CASULO hallucination `32.51` | reduction `60.84` | delta control `83.76` | residual delta `62.32`

## Anomaly Summary
- total anomalies: `95`
- `STOCH-0014-AUDIT_DOCUMENTAL` `casulo_hallucination` value `49` reason `z_score_outlier`
- `STOCH-0119-SOFTWARE_REVIEW` `casulo_hallucination` value `49` reason `z_score_outlier`
- `STOCH-0165-RULE_EXTRACTION` `casulo_hallucination` value `47` reason `z_score_outlier`
- `STOCH-0166-RULE_EXTRACTION` `casulo_hallucination` value `47` reason `z_score_outlier`
- `STOCH-0324-RULE_EXTRACTION` `casulo_hallucination` value `47` reason `z_score_outlier`
- `STOCH-0342-RULE_EXTRACTION` `casulo_hallucination` value `47` reason `z_score_outlier`
- `STOCH-0353-SOFTWARE_REVIEW` `casulo_hallucination` value `46` reason `z_score_outlier`
- `STOCH-0391-RULE_EXTRACTION` `casulo_hallucination` value `49` reason `z_score_outlier`
- `STOCH-0045-PARSER_DOCUMENTAL` `hallucination_reduction` value `30` reason `z_score_outlier`
- `STOCH-0089-PARSER_DOCUMENTAL` `hallucination_reduction` value `32` reason `z_score_outlier`
- `STOCH-0094-PARSER_DOCUMENTAL` `hallucination_reduction` value `25` reason `z_score_outlier`
- `STOCH-0120-PARSER_DOCUMENTAL` `hallucination_reduction` value `25` reason `z_score_outlier`
- `STOCH-0142-PARSER_DOCUMENTAL` `hallucination_reduction` value `31` reason `z_score_outlier`
- `STOCH-0168-PARSER_DOCUMENTAL` `hallucination_reduction` value `32` reason `z_score_outlier`
- `STOCH-0224-PARSER_DOCUMENTAL` `hallucination_reduction` value `31` reason `z_score_outlier`
- `STOCH-0227-AUDIT_DOCUMENTAL` `hallucination_reduction` value `32` reason `z_score_outlier`
- `STOCH-0273-PARSER_DOCUMENTAL` `hallucination_reduction` value `25` reason `z_score_outlier`
- `STOCH-0409-PARSER_DOCUMENTAL` `hallucination_reduction` value `31` reason `z_score_outlier`
- `STOCH-0417-PARSER_DOCUMENTAL` `hallucination_reduction` value `31` reason `z_score_outlier`
- `STOCH-0429-PARSER_DOCUMENTAL` `hallucination_reduction` value `29` reason `z_score_outlier`
- `STOCH-0432-PARSER_DOCUMENTAL` `hallucination_reduction` value `27` reason `z_score_outlier`
- `STOCH-0120-PARSER_DOCUMENTAL` `residual_delta_index` value `12` reason `z_score_outlier`
- `STOCH-0273-PARSER_DOCUMENTAL` `residual_delta_index` value `10` reason `z_score_outlier`
- `STOCH-0293-RULE_EXTRACTION` `residual_delta_index` value `5` reason `z_score_outlier`
- `STOCH-0304-RULE_EXTRACTION` `residual_delta_index` value `10` reason `z_score_outlier`

## Calibration Decision

- Do not change core weights from a single run.
- Inspect anomaly clusters first.
- Build separate curves by case family.
- Treat residual delta as real missing evidence, not as failure by itself.
- Tune only when repeated batch-level pattern appears.
- Next phase: run repeated seeds and compare stability/drift.
