# CASULO Delta Zero Assisted Scoring Review Guide

This packet creates suggested/candidate scores only.

Do not treat suggested_* fields as external/manual validation.

Review process:
1. Open product/evaluation/casulo_delta_zero_assisted_scoring_draft_v0_3.csv.
2. Review each suggested_* score against the case packet.
3. Fill product/evaluation/casulo_delta_zero_human_acceptance_sheet_v0_3.csv.
4. Only accepted/adjusted human scores may be converted into external_* fields in a later ingestion gate.

Hard rule:
- Do not auto-copy suggested_* into external_*.
- Do not claim validated model gain.
- Do not claim hallucination reduction.
- Do not validate Delta Zero Ready.
- Do not accept dataset, client, production or commercial claims.

T0 trajectory:
- velocity_ready=false means not measured.
- acceleration_ready=false means not measured.
- They must not be interpreted as zero.
