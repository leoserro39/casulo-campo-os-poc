# Grafo, Dominios e Sincronizacoes

O grafo e a malha computavel do CASULO Workbench.

## Nos

Company, Case, Domain, ComputableBranch, Source, Evidence, DataQualityScore, StateArtifact, OperationalState, Intersection, Delta, Gate, Solution, ExecutorTask, MonitoringCycle, Snapshot, LedgerEvent.

## Arestas

HAS_DOMAIN, HAS_BRANCH, CONSUMES_SOURCE, PRODUCES_EVIDENCE, SUPPORTS_STATE, CONTRADICTS_STATE, INTERSECTS_WITH, GENERATES_DELTA, HAS_GATE, ALLOWS_SOLUTION, BLOCKS_SOLUTION, IMPLEMENTED_BY, UPDATES_STATE, RECORDED_IN_LEDGER.

## Sincronizacoes

entrada -> dados computaveis -> dominios -> ramificacoes -> grafo -> estado -> deltas -> gates -> solucoes -> novo estado.

## Regra

Grafo nao e enfeite. Grafo e a malha onde o estado operacional se torna computavel.
