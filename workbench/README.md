# CASULO Workbench

Workbench v0.2 para diagnostico de Estado Operacional.

## Hardening v0.2

- `run_demo.py` agora usa check mode por default e nao escreve outputs.
- `--write` e obrigatorio para gerar arquivos novos.
- Runtime outputs locais vao para `workbench/runtime_outputs/`, ignorado pelo Git.
- Contratos foram adicionados em `workbench/contracts/`.
- `validate_workbench.py --strict` valida estrutura, contratos e engine sem escrever.

## Comandos seguros

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/run_demo.py --case all --check
python workbench/scripts/export_codex_task.py --case all --check
```

## Escrita explicita

```bash
python workbench/scripts/run_demo.py --case all --write --stable-time
python workbench/scripts/export_codex_task.py --case all --write --stable-time
```
