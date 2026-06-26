# CASULO Workbench

Workbench v0.1 para diagnostico de Estado Operacional.

## O que existe neste bootstrap

- Atlas em `docs/casulo_workbench_atlas/`.
- Estrutura `workbench/`.
- Engine base em Python puro.
- Tres casos demo.
- Geracao de snapshots, grafo, ledger, relatorio e task Codex.
- Stub de cockpit Cubo/Cupula.
- Docker/cloud-ready stub.

## Rodar demos

```bash
python workbench/scripts/validate_workbench.py
python workbench/scripts/run_demo.py --case all
python workbench/scripts/export_codex_task.py --case all
```
