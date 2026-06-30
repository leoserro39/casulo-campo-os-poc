#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ALLOWED_CAPTURE_MODES = {
    "MANUAL_PASTED_GPT_PURE",
    "MANUAL_PASTED_GPT_STACK_GROUNDED",
    "CUSTOM_GPT_ACTION_CAPTURED",
    "API_CAPTURED",
    "SIMULATED_FIXTURE",
    "UNKNOWN_OR_UNTRUSTED"
}

CALIBRATION_ELIGIBLE_MODES = {
    "MANUAL_PASTED_GPT_PURE",
    "MANUAL_PASTED_GPT_STACK_GROUNDED"
}

EXCLUDED_MODES = {
    "SIMULATED_FIXTURE",
    "UNKNOWN_OR_UNTRUSTED"
}

REQUIRED_RECORD_FIELDS = [
    "capture_id",
    "capture_mode",
    "model_label",
    "capture_datetime_utc",
    "operator",
    "prompt_id",
    "prompt_text",
    "context_packet_used",
    "context_packet_reference",
    "raw_response",
    "source_conversation_reference",
    "contains_client_data",
    "contains_sensitive_data",
    "anonymized",
    "human_review_required",
    "review_status",
    "calibration_eligible",
    "exclusion_reason"
]

def validate_record(record, index):
    errors = []
    warnings = []

    for field in REQUIRED_RECORD_FIELDS:
        if field not in record:
            errors.append(f"record[{index}] missing field: {field}")

    mode = record.get("capture_mode")
    if mode not in ALLOWED_CAPTURE_MODES:
        errors.append(f"record[{index}] invalid capture_mode: {mode}")

    if record.get("context_packet_used") is True and not record.get("context_packet_reference"):
        errors.append(f"record[{index}] context_packet_used requires context_packet_reference")

    if record.get("contains_client_data") is True:
        errors.append(f"record[{index}] contains_client_data must be false for calibration intake")

    if record.get("contains_sensitive_data") is True:
        errors.append(f"record[{index}] contains_sensitive_data must be false for calibration intake")

    if record.get("anonymized") is not True:
        errors.append(f"record[{index}] must be anonymized before calibration intake")

    if not str(record.get("prompt_text", "")).strip():
        errors.append(f"record[{index}] prompt_text is empty")

    if not str(record.get("raw_response", "")).strip():
        errors.append(f"record[{index}] raw_response is empty")

    if record.get("human_review_required") is not True:
        errors.append(f"record[{index}] human_review_required must be true")

    if record.get("review_status") != "REVIEWED" and record.get("calibration_eligible") is True:
        errors.append(f"record[{index}] cannot be calibration_eligible before REVIEWED status")

    if mode in EXCLUDED_MODES and record.get("calibration_eligible") is True:
        errors.append(f"record[{index}] excluded capture mode cannot be calibration eligible")

    if mode not in CALIBRATION_ELIGIBLE_MODES and record.get("calibration_eligible") is True:
        errors.append(f"record[{index}] capture mode is not calibration eligible")

    if record.get("review_status") == "PENDING_HUMAN_REVIEW" and not record.get("exclusion_reason"):
        warnings.append(f"record[{index}] pending review should keep exclusion_reason populated")

    return errors, warnings

def validate_batch(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = []
    warnings = []

    required_batch_fields = [
        "batch_version",
        "phase",
        "batch_id",
        "batch_status",
        "record_count",
        "calibration_candidate_count",
        "contains_client_data",
        "contains_sensitive_data",
        "anonymized",
        "calibration_status",
        "intake_records"
    ]

    for field in required_batch_fields:
        if field not in data:
            errors.append(f"batch missing field: {field}")

    records = data.get("intake_records", [])
    if not isinstance(records, list):
        errors.append("intake_records must be a list")
        records = []

    if data.get("record_count") != len(records):
        errors.append("record_count does not match intake_records length")

    candidate_count = len([r for r in records if r.get("calibration_eligible") is True])
    if data.get("calibration_candidate_count") != candidate_count:
        errors.append("calibration_candidate_count does not match eligible records")

    if data.get("contains_client_data") is True:
        errors.append("batch contains_client_data must be false")

    if data.get("contains_sensitive_data") is True:
        errors.append("batch contains_sensitive_data must be false")

    if data.get("anonymized") is not True:
        errors.append("batch must be anonymized")

    if len(records) == 0:
        if data.get("calibration_candidate_count") != 0:
            errors.append("empty batch cannot have calibration candidates")
        if data.get("calibration_status") != "NOT_CALIBRATED_EMPTY_BATCH_NO_REAL_RESPONSES":
            errors.append("empty batch must use empty-batch calibration status")

    for i, record in enumerate(records):
        e, w = validate_record(record, i)
        errors.extend(e)
        warnings.extend(w)

    result = {
        "status": "PASS" if not errors else "FAIL",
        "batch_path": str(path),
        "record_count": len(records),
        "calibration_candidate_count": candidate_count,
        "errors": errors,
        "warnings": warnings
    }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("batch_path")
    args = parser.parse_args()

    result = validate_batch(args.batch_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
