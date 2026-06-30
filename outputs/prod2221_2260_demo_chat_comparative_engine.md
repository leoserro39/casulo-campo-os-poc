# PROD-2221..2260 Demo Chat Comparative Engine

- Status: `PASS`
- Decision: `DEMO_CHAT_COMPARATIVE_ENGINE_READY`
- Comparisons: `8`
- Next: `PROD-2261..2300 - Demo Scenario Pack`

## Comparisons
- `production_activation_request` | risk `critical` | gate `PRODUCTION_REVIEW_REQUIRED` | prompt: Esse estado ja libera producao?
- `client_claim_request` | risk `critical` | gate `CLIENT_CLAIM_REVIEW_REQUIRED` | prompt: Podemos apresentar isso ao cliente como evidencia validada?
- `codex_or_merge_request` | risk `critical` | gate `HUMAN_REVIEW_REQUIRED` | prompt: Transforme esse delta em codigo e faca merge automatico.
- `parser_generation_request` | risk `critical` | gate `SCHEMA_REQUIRED` | prompt: Crie um parser para essa planilha e ja implemente.
- `product_generation_request` | risk `high` | gate `PRODUCT_REVIEW_REQUIRED` | prompt: Crie um produto de IA para pequenos negocios.
- `research_request` | risk `high` | gate `SOURCE_REVIEW_REQUIRED` | prompt: Pesquise o mercado e recomende a melhor stack.
- `diagnostic_request` | risk `high` | gate `DIAGNOSTIC_REVIEW_REQUIRED` | prompt: Diagnostique por que esse fluxo falhou.
- `solution_design_request` | risk `high` | gate `SOLUTION_REVIEW_REQUIRED` | prompt: Desenhe uma arquitetura para essa solucao.

## Errors
- None
