# PROD-621B..650B Domain Preflight and Pattern Mining Layer

- Status: `PASS`
- Cases analyzed: `120`
- Original safe behavior: `89.17%`
- Recalibrated safe behavior: `100.0%`
- Decision: `READY_FOR_BUSINESS_CASE_INTERACTIVE_RUNNER_WITH_PREFLIGHT`

## Activation Distribution
- `CANDIDATE_DOMAIN_REQUIRE_EVIDENCE`: `12`

## Reasoning Mode Distribution
- `FULL_REASONING_WITH_GROUNDING`: `53`
- `GUIDED_REASONING`: `67`

## Correlations
- `adjusted_risk x live_delta_score`: `0.8732`
- `adjusted_risk x gate_numeric`: `0.8436`
- `domain_sensitivity x adjusted_risk`: `0.4205`
- `domain_sensitivity x gate_numeric`: `0.1253`
- `hallucination_budget x gate_numeric`: `-0.7959`
- `hallucination_budget x safe_behavior_v2`: `0.0`
- `safe_behavior_v1 x safe_behavior_v2`: `0.0`

## Pattern Findings
- `PATTERN-001` `domain_sensitivity_pressure`: Domain sensitivity pushes adjusted risk, live delta and review pressure.
- `PATTERN-002` `partial_context_safe_escalation`: Partial context splits into evidence-required for lighter domains and review for sensitive domains.
- `PATTERN-003` `noisy_input_allow_warning_gap`: Noisy input needs ALLOW_WITH_WARNING to preserve useful output without pretending certainty.
- `PATTERN-004` `evidence_variance_gap`: PROD-621 evidence coverage was too constant; this layer adds evidence probes.
- `PATTERN-005` `preflight_before_domain_activation`: A domain should start as neutral seed and only become operational after preflight.

## Threshold Recommendations
- `THR-001` `partial_context`: `sensitivity <1.25 -> EVIDENCE_REQUIRED; sensitivity >=1.25 or adjusted_risk >=55 -> HUMAN_REVIEW_REQUIRED`
- `THR-002` `noisy_input`: `evidence >=70 and sensitivity <=1.20 -> ALLOW_WITH_WARNING; sensitivity >=1.45 -> HUMAN_REVIEW_REQUIRED`
- `THR-003` `hallucination_budget`: `budget <0.25 block/review only; 0.25-0.45 gap mapping; 0.45-0.70 guided reasoning; >0.70 full grounded reasoning`
- `THR-004` `evidence_variance`: `test low 40-55, medium 60-75, high 80-95 evidence before interactive runner`

## Next Recommended Bundle
- `PROD-651 Business Case Interactive Runner with Preflight and Live Delta`
