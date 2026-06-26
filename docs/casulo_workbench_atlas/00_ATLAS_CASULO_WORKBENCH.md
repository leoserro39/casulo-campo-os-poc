# CASULO Workbench Atlas

## Status

TASK-WB-000 — Atlas canonico inicial do CASULO Workbench.

## Finalidade

O CASULO Workbench e a maquina operacional para aplicar o Metodo CASULO em clientes reais.

Ele nao comeca vendendo IA, automacao, dashboard ou sistema. Ele comeca computando Estado Operacional.

## Cadeia canonica

```text
entrada/analise
-> mapa de dados computaveis
-> indice de qualidade de dados
-> dominios
-> ramificacoes computaveis
-> grafo
-> sincronizacoes
-> fragilidade/alucinacao operacional
-> deltas
-> gates
-> cockpit/chat/relatorio
-> solucao liberada
-> novo estado
```

## Regra-mestra

Dado ruim nao vira solucao.
Estado fragil nao vira recomendacao forte.
Delta sem evidencia nao passa pelo gate.
Solucao so nasce quando o estado permite.

## Camadas

1. Metodo CASULO.
2. Workbench.
3. Cubo/Cupula.
4. Grafo.
5. Executor tecnico.
6. Cliente.

## Nao escopo v0

- SaaS multi-tenant completo.
- Billing.
- Producao final com compliance completo.
- Substituicao de especialistas.
- Decisao automatica sem revisao humana.
