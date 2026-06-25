# CASULO Campo OS Proposal

- status: PROPOSED
- generated_utc: 20260625_175958Z
- question: sugira uma melhoria para atendimento whatsapp
- inferred_domain: atendimento
- graph_nodes: 20
- graph_relationships: 19
- chunks_used: 5
- estimated_tokens: 623

## Sources
- 01_domains/atendimento/problems/demora_resposta_whatsapp.md
- 00_inbox/raw_docs/demo_business_notes.md
- 02_cases/case_demo_001/evidence_ledger.jsonl
- 02_cases/case_demo_001/intake.md
- 02_cases/case_demo_001/solution_packet.md

## Controlled proposal
- Criar roteiro minimo de atendimento WhatsApp com respostas base.
- Separar mensagens em: novo contato, aguardando confirmacao e resolvido.
- Medir tempo de primeira resposta ou mensagens sem resposta por dia.
- Rodar por 7 dias antes de promover mudanca para estado canonico.

## Gates
- do not change canonical state automatically
- require human review before updating solution_packet.md
- require measured evidence before promoting return_delta.json

## Suggested next action
- Review and decide: approve, adjust, reject, or ask for more evidence.
