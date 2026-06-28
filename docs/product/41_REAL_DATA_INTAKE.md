# Real / Anonymized VesselFlow Data Intake

## Purpose

Prepare a controlled intake path for real or anonymized VesselFlow data.

This bundle does not require real data at apply time. It installs the intake contract, template and validator.

## Main script

```bash
python product/scripts/prepare_vesselflow_real_data_intake.py --repo . --check
```

To write a reviewed intake:

```bash
python product/scripts/prepare_vesselflow_real_data_intake.py --repo . --intake <filled-json> --write --rerun-state
```
