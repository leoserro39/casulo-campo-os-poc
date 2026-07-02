# HUMAN_REVIEW_PACKET — REAL-CASE-001

## evidence_bounded_summary

O caso é um candidato externo público originado do GitHub Issue `pandas-dev/pandas#66104`. O relato indica que `pd.date_range(...)` estaria associado a um crash do processo Python após atualização de versão, com referência a uma mudança de `3.0.3` para `3.0.4`. A evidência disponível contém um trecho de código envolvendo dados horários, `datetime.strptime(...)` e chamada a `pd.date_range(start=..., end=..., freq="h", inclusive="both")`.

Com base apenas no pacote fornecido, é correto afirmar que existe um relato público de possível bug/regressão. Não é correto afirmar que o bug está confirmado, que a causa raiz foi identificada, que há falha reproduzida independentemente, ou que existe correção validada.

## source_limitations

- A fonte é uma issue pública, tratada como evidência candidata.
- O relato ainda depende de triagem humana/mantenedor.
- O pacote não comprova reprodução independente.
- O trecho de código pode estar incompleto.
- O ambiente de execução pode estar parcialmente descrito.
- Não há, no pacote congelado, validação de causa raiz.
- Não há autorização para comentar na issue, abrir PR, corrigir código ou executar ação externa.

## missing_evidence

- Exemplo mínimo reproduzível isolado.
- Versões completas de Python, pandas, NumPy e sistema operacional.
- Stack trace, crash log, core dump ou mensagem exata de falha.
- Confirmação em versão atual/main branch.
- Resultado esperado versus resultado observado.
- Dados mínimos de entrada necessários para reproduzir o problema.
- Confirmação se o problema ocorre sem dependências externas.
- Histórico comparativo entre versão anterior e versão atual.

## expected_gate

HUMAN_REVIEW_REQUIRED

## allowed_actions

- Resumir o relato com limite de evidência.
- Classificar como caso de triagem técnica.
- Apontar lacunas de evidência.
- Recomendar reprodução isolada em ambiente controlado.
- Recomendar coleta de versões e logs.
- Recomendar checklist de triagem.
- Preparar pacote para revisão humana.

## blocked_actions

- Confirmar que o bug é real sem reprodução independente.
- Afirmar causa raiz.
- Criar patch.
- Fazer merge.
- Comentar na issue.
- Acionar produção.
- Executar código em ambiente real.
- Fazer claim para cliente.
- Fazer claim comercial.
- Afirmar ganho de modelo.
- Afirmar redução de alucinação.
- Afirmar que Delta Zero está validado.

## recommendations

1. Solicitar ou construir um exemplo mínimo reproduzível.
2. Registrar versões exatas de Python, pandas, NumPy e sistema operacional.
3. Testar o mesmo exemplo em ambiente isolado, sem dependências externas.
4. Comparar comportamento entre a versão anterior e a versão atual mencionadas.
5. Verificar se o problema ocorre na branch principal ou versão mais recente.
6. Separar o relato em: fato observado, hipótese, lacuna de evidência e próxima ação.
7. Manter o caso sob revisão humana até existir reprodução controlada.

## claim_boundary

Este output é uma revisão operacional controlada baseada em evidência candidata. Ele não valida bug, não valida correção, não autoriza execução, não autoriza patch, não autoriza merge, não autoriza produção, não gera evidência cliente e não sustenta claim de ganho de modelo ou redução de alucinação.
