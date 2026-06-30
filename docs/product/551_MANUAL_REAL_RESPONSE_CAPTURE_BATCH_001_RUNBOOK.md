# PROD-1981..2020 - Manual Real Response Capture Batch 001 Runbook

This phase prepares Batch 001 for manual real GPT response capture.

It does not require real responses yet.
It does not connect GPT.
It does not call GPT.
It does not call Codex.
It does not approve thresholds.
It does not approve final weights.
It does not authorize client-facing claims.

## Purpose

Prepare the first real response capture batch with a safe manual process.

Batch 001 is designed to collect:

- 4 pure GPT responses;
- 4 stack-grounded GPT responses;
- 4 prompt pairs;
- explicit provenance;
- anonymization flags;
- review status;
- calibration exclusion until human review.

## Capture principle

The repository prepares the batch structure.

A human operator must manually run the prompts outside the repository and paste responses into a future intake file.

No automatic GPT call is authorized.

## Boundary

This phase stops before real capture.
The next action requires human/manual capture.
