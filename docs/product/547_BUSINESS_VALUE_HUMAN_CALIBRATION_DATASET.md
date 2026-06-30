# PROD-1821..1860 - Business Value Human Calibration Dataset

This phase creates a human calibration dataset for CASULO business value.

It does not perform final calibration.
It does not set final thresholds.
It does not connect GPT.
It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not authorize client-facing claims.

## Purpose

Convert graph-based opportunity ranking and ensemble scores into human-reviewable business value cases.

The dataset is used to review:

- whether the opportunity score makes sense;
- whether the recommended service package is appropriate;
- whether the risk/gate level is correct;
- whether the hallucination reduction potential is credible;
- whether the commercial value proxy is plausible;
- whether the recommended mode is safe;
- whether this case should be prioritized for pilot discovery.

## Human review dimensions

- business fit;
- pain clarity;
- evidence gap clarity;
- service package fit;
- implementation risk realism;
- governance pressure realism;
- monitoring recurrence potential;
- hallucination reduction relevance;
- commercial value plausibility;
- pilot priority.

## Calibration boundary

This dataset is an input to future calibration.

It is not final calibration.
It does not approve final weights or thresholds.
