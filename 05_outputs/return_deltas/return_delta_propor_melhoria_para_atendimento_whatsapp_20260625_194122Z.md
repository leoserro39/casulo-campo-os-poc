# CASULO Campo OS - Return Delta Proposal

- status: RETURN_DELTA_PROPOSED
- generated_utc: 20260625_194122Z
- source_review: 05_outputs/reviews/review_proposal_propor_melhoria_para_atendimento_whatsapp_20260625_193823Z.json
- source_proposal: 05_outputs/proposals/proposal_propor_melhoria_para_atendimento_whatsapp_20260625_184859Z.json
- target_branch: atendimento
- canonical_effect: PROPOSED_ONLY
- requires_final_apply: true

## Approved by

- Leonardo Serro

## Proposed changes

- Criar roteiro minimo de atendimento WhatsApp com respostas base.
- Separar mensagens em: novo contato, aguardando confirmacao e resolvido.
- Medir tempo de primeira resposta ou mensagens sem resposta por dia.
- Rodar por 7 dias antes de promover mudanca para estado canonico.

## Mesh Delta Reference

- Delta_L: 0.389
- H_pre: 0.339
- gate: ALLOW_PROPOSAL
- support_ratio: 0.556
- missing_ratio: 0.444

## Safety rules

- Do not modify canonical state automatically.
- Apply only after explicit final approval.
- Keep original proposal, review and return delta traceable.
- Measure pilot result before promoting long-term state.

## Next action

- Run final apply gate if the operator wants to promote this return delta.
