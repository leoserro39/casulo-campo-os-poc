# AGENTS.md - CASULO Campo OS POC

## Missao

Construir e operar uma prova de conceito repo-native onde documentos soltos viram uma malha operacional versionada com dominios, casos, evidencias, problemas, solucoes e deltas.

## Regras obrigatorias

1. Git e a fonte da verdade.
2. Nao apagar ou mover arquivos de `00_inbox/raw_docs`.
3. Nao criar dominio novo automaticamente. Dominios permitidos: atendimento, vendas, operacao, financeiro, marketing, gestao, tecnologia, impacto.
4. Toda proposta de mudanca precisa aparecer como arquivo, manifest ou delta.
5. Toda alteracao estrutural precisa passar por `python 04_scripts/validate_mesh.py`.
6. `05_outputs/graph/*` e `05_outputs/rag/*` sao derivados, nao fonte canonica.
7. Nao usar API externa, segredo, token ou dependencia paga nesta POC.
8. Nao criar produto web nesta fase.
9. O chat local pode sugerir; nao pode persistir estado canonico sozinho.
10. Antes de promover solucao, verificar evidencia minima e revisao humana.

## Definition of Done

- scripts rodam com Python standard library;
- validacao PASS;
- grafo exportado;
- indice RAG exportado;
- relatorio de status gerado;
- nenhum arquivo fora da pasta da POC e necessario.
