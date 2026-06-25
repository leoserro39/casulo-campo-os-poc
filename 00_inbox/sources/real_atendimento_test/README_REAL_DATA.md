# Real atendimento data - local use only

## Rule

Do not commit raw real atendimento exports.

Use this folder for local testing only.

## Local raw input example

Place the real raw export locally as:

raw_atendimento_export.csv

This file is ignored by Git.

## Sanitized output example

Generate:

atendimento_real_sanitized.csv

This file is also ignored by Git by default.

## Safe fixture files

The committed sample files are synthetic fixtures only:

- raw_atendimento_export_SAMPLE.csv
- atendimento_real_sanitized_FROM_RAW_SAMPLE.csv

## Real cycle command

After sanitizing local data, run:

python 04_scripts/run_real_test_cycle.py \
  --source 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv \
  --source-name real_atendimento_cycle_002 \
  --cycle-name real_atendimento_cycle_002 \
  --reviewer leoserro39 \
  --min-measurements 3
