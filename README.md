# CASULO Campo OS - Repo-as-Mesh POC v0.1

Esta prova de conceito mostra uma malha operacional simples usando Git como fonte da verdade.

- Pastas representam dominios.
- Markdown/JSON/JSONL representam estado, evidencia, problemas, solucoes e deltas.
- Scripts validam a malha antes de aceitar mudancas.
- `graph.json`, `nodes.csv` e `relationships.csv` sao projecoes derivadas para Neo4j ou outro grafo.
- `chunks.jsonl` e indice derivado para RAG.
- `chat_mesh.py` e um chat local e deterministico para simular perguntas, consumo e saidas sem custo de API.

## Comandos principais

```bash
python 04_scripts/validate_mesh.py
python 04_scripts/triage_inbox.py
python 04_scripts/apply_triage_manifest.py
python 04_scripts/export_graph.py
python 04_scripts/build_rag_index.py
python 04_scripts/chat_mesh.py --ask "qual o estado operacional do caso demo?"
python 04_scripts/run_demo.py
```

## Fluxo recomendado

```bash
python 04_scripts/run_demo.py
python 04_scripts/chat_mesh.py
```

No modo interativo do chat, tente:

```text
estado
problemas
solucoes
grafo
consumo
sair
```

## Regra arquitetural

Git e a fonte da verdade. Grafo, RAG e chat sao projecoes/leituras derivadas. Nenhuma saida do chat muda o estado oficial sem arquivo delta validado.
