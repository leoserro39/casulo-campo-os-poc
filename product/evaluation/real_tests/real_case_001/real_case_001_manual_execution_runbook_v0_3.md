# REAL-CASE-001 Manual Execution Runbook v0.3

## Status

Execution gate: APPROVED FOR NEXT PHASE CONTROLLED SANDBOX RUN

## Boundary

This runbook does not execute GPT by itself.

Do not:

- patch code
- merge code
- comment on GitHub
- activate production
- call external tools
- claim the issue is confirmed
- make client/commercial/model-gain/hallucination-reduction claims

## Manual next-phase steps

1. Open `product/evaluation/real_tests/real_case_001/real_case_001_controlled_review_prompt_v0_3.md`.
2. Provide the frozen input bundle to the selected model/session.
3. Ask for `HUMAN_REVIEW_PACKET` only.
4. Save full output to a local markdown file.
5. Capture it with:

```bash
python product/scripts/run_real_case_001_manual_capture.py --input-output-file /path/to/manual_model_output.md --operator "Leonardo Serro"
```

6. Proceed to the scoring/review phase.
