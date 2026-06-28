# CASULO Workbench

Workbench v0.9 runtime evidence audit addition.

## Runtime execution

```bash
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Runtime evidence audit

```bash
python workbench/scripts/audit_runtime_evidence.py --case-id real_controlled_template_001 --runtime-root workbench/runtime_outputs --write-report --output-dir outputs
```

Runtime outputs remain ignored. Only audit reports should be committed.
