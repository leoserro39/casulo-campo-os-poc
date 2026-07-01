# CASULO Delta Zero External Evaluator Review Guide

Fill all external_* fields for all 36 cases.

Scores: 0 to 5.

Boolean fields: true or false.

external_false_memory_risk: LOW, MEDIUM, HIGH or NOT_APPLICABLE.

Important:
- T0_ONLY means no trajectory yet.
- velocity_ready=false must not be interpreted as zero velocity.
- acceleration_ready=false must not be interpreted as zero acceleration.
- Delta Zero Ready remains unvalidated.
- Candidate tokens remain non-canonical.
- Do not approve dataset, production, client evidence, commercial claim, validated model gain or hallucination reduction.

After scoring, run:

python product/scripts/score_casulo_delta_zero_external_evaluator.py --input product/evaluation/casulo_delta_zero_external_evaluator_workbench_v0_3.csv --output outputs/prod6501_6540_casulo_delta_zero_external_score_result.json
