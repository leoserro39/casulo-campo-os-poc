# CASULO Campo OS - State Timeline

- generated_utc: 2026-06-25T19:28:26.904721+00:00
- source_intake_count: 1
- source_mapping_count: 1
- source_trust_report_count: 1
- intake_delta_count: 1
- mesh_delta_count: 3
- proposal_count: 3

## Current operational reading

- Legacy/source intake is active.
- Mesh delta computation is active.
- Delta-gated proposal generation is active.

## Human review required

- 05_outputs/source_intake/manifests/legacy_whatsapp_export_20260625_191922Z_manifest.json | gate=ALLOW_WITH_HUMAN_REVIEW | hallucination_risk=MEDIUM

## Events

- type=source_intake | path=05_outputs/source_intake/manifests/legacy_whatsapp_export_20260625_191922Z_manifest.json | source_id=legacy_whatsapp_export_20260625_191922Z | target_branch=atendimento | gate=ALLOW_WITH_HUMAN_REVIEW | trust_score=0.899 | hallucination_risk=MEDIUM
- type=mesh_delta | path=05_outputs/deltas/mesh_delta_computar_malha_para_melhoria_atendimento_whatsapp_20260625_184005Z.json | question=computar malha para melhoria de atendimento whatsapp | domain=atendimento | gate=ALLOW_PROPOSAL | Delta_L=0.244 | H_pre=0.194
- type=mesh_delta | path=05_outputs/deltas/mesh_delta_delta_atendimento_whatsapp_20260625_184014Z.json | question=delta atendimento whatsapp | domain=atendimento | gate=ALLOW_PROPOSAL | Delta_L=0.389 | H_pre=0.339
- type=mesh_delta | path=05_outputs/deltas/mesh_delta_propor_melhoria_para_atendimento_whatsapp_20260625_184859Z.json | question=propor melhoria para atendimento whatsapp | domain=atendimento | gate=ALLOW_PROPOSAL | Delta_L=0.389 | H_pre=0.339
- type=proposal | path=05_outputs/proposals/proposal_sugira_uma_melhoria_para_atendimento_whatsapp_20260625_175958Z.json | question=sugira uma melhoria para atendimento whatsapp | domain=atendimento | status=PROPOSED
- type=proposal | path=05_outputs/proposals/proposal_propor_melhoria_para_atendimento_whatsapp_20260625_182513Z.json | question=propor melhoria para atendimento whatsapp | domain=atendimento | status=PROPOSED
- type=proposal | path=05_outputs/proposals/proposal_propor_melhoria_para_atendimento_whatsapp_20260625_184859Z.json | question=propor melhoria para atendimento whatsapp | domain=atendimento | status=PROPOSED | gate=ALLOW_PROPOSAL | Delta_L=0.389 | H_pre=0.339
