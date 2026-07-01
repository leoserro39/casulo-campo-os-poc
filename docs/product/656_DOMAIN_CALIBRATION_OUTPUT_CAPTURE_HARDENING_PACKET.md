# PROD-6101..6140 - Domain Calibration Output Capture Hardening Packet

Prepares hardening for the Domain Calibration Batch 01 rerun.

This phase does not call GPT.

## Problem being fixed

The previous Batch 01 technical execution passed, but behavioral calibration entered HOLD because content capture was insufficient.

Observed source values:

- Empty output count: 27
- Full output present count: 0
- JSON parseable from preview count: 0

## Hardening introduced

- full_output_text
- parsed_output_json
- json_parse_status
- output_capture_status
- behavioral_capture_status
- review_ready
- expected_behavior_fields_present
- expected_behavior_fields_missing
- technical_status separated from behavioral capture status

## Rule

Technical PASS does not equal behavioral PASS.

## Next

PROD-6141..6180 - Domain Calibration Hardened Rerun Execution Gate
