# Arquitetura CASULO Workbench Cloud

## Objetivo

O Workbench deve rodar como maquina cloud, nao como conversa solta nem como operacao dependente do PC local.

## Stack v0 sugerida

- Frontend: React/Next.js.
- Backend: FastAPI ou Node API.
- Estado operacional: Postgres/Supabase.
- Grafo: Neo4j Aura ou graph.json inicial com export Cypher.
- Contexto/RAG: pgvector ou indice vetorial.
- Automacao: n8n/Power Automate.
- Executor: Codex/dev/n8n/parceiro.
- Versionamento: GitHub.

## Modos

- Pre-atendimento computa.
- Atendimento opera cockpit.
- Pos-atendimento registra decisao, snapshot e implementacao.
