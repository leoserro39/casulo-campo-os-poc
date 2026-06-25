# Legacy Intake Delta

- source_id: legacy_whatsapp_export_20260625_191922Z
- target_branch: atendimento
- status: PROPOSED_INTAKE_DELTA
- hallucination_risk: MEDIUM
- gate: ALLOW_WITH_HUMAN_REVIEW

## Supported dimensions
- whatsapp
- cliente
- resposta
- tempo
- resolvido
- evidencia
- metrica

## Canonical effect
- No canonical branch state was changed.
- This intake only proposes evidence and mapping.
- Human review is required before promotion to long-term state.

## Artifacts
- manifest: 05_outputs/source_intake/manifests/legacy_whatsapp_export_20260625_191922Z_manifest.json
- mapping: 05_outputs/source_intake/mappings/legacy_whatsapp_export_20260625_191922Z_mapping.json
- trust_report: 05_outputs/source_intake/trust_reports/legacy_whatsapp_export_20260625_191922Z_trust_report.md
- raw_snapshot: 05_outputs/source_intake/raw_snapshots/legacy_whatsapp_export_20260625_191922Z.csv
