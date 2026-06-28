# Data-Backed VesselFlow Rerun

## Purpose

Orchestrate a controlled data-backed rerun after a reviewed real/anonymized intake JSON is ready.

Default mode is check-only. Nothing is written unless `--write` is used.

## Check

```bash
python product/scripts/run_vesselflow_data_backed_rerun.py --repo . --check
```

## Write and rerun

```bash
python product/scripts/run_vesselflow_data_backed_rerun.py --repo . --intake <reviewed-intake.json> --write --rerun-state --regenerate-report
```
