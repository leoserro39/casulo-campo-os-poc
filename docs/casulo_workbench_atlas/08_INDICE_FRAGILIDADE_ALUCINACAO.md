# Indice de Fragilidade e Risco de Alucinacao Operacional

Mede se uma recomendacao esta fraca, contraditoria, sem evidencia suficiente ou baseada em contexto insuficiente.

## Entradas

data_quality_score, support_ratio, missing_ratio, contradiction_count, source_trust, sync_coverage, domain_agreement, evidence_independence, decision_impact, state_confidence.

## Saidas

ALLOW_SOLUTION, RECOMMEND_SMALLER_DELTA, NEED_MORE_EVIDENCE, HUMAN_REVIEW_REQUIRED, BLOCK_SOLUTION.

O CASULO nao so recomenda. Ele mede se existe condicao de recomendar.
