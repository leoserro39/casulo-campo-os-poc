# VesselFlow Real / Anonymized Data Intake

Use this folder to prepare a controlled replacement for the sample placeholder.

Start from:

```text
product/verticals/vesselflow/real_data_intake/vesselflow_real_data_intake_template.json
```

Copy it to a new file, fill the dataset reference and classification, then run:

```bash
python product/scripts/prepare_vesselflow_real_data_intake.py --repo . --intake <your-intake-json> --check
python product/scripts/prepare_vesselflow_real_data_intake.py --repo . --intake <your-intake-json> --write --rerun-state
```

Do not use unredacted confidential data unless approved for internal controlled processing.
