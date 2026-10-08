# Testes RED — <JIRA-ID>

## Contexto do contrato

```text
FLOW_MODE: STANDARD_GATED | QUICK_AUTOGO
CONTRACT_SOURCE: SPEC | QUICK_CONTRACT
```

## Mechanical readiness

### STANDARD

```text
SPEC_APPROVED:
BLOCKING_OPEN_QUESTIONS:
AC_TOTAL:
AC_WITH_VERIFICATION:
UNTRACED_TESTS:
```

### QUICK

```text
QUICK_CONTRACT_APPROVED:
CONTRACT_ITEMS_TOTAL:
CONTRACT_ITEMS_WITH_VERIFICATION:
UNTRACED_TESTS:
```

## Matriz de rastreabilidade

### STANDARD

| Requisito | AC | PLAN | DD | Evidência planejada | Teste/artefato | Status |
|---|---|---|---|---|---|---|
| R-01 | AC-01 | PLAN-1 | | UNIT_TEST | | COVERED_PLANNED |

### QUICK

| Item do Quick Contract | Evidência planejada | Teste/artefato | Status |
|---|---|---|---|
| QC-01 | UNIT_TEST | | COVERED_PLANNED |

Usar somente a tabela correspondente ao fluxo; não inventar `R-*`, `AC-*` ou `PLAN-*` no QUICK.

## Testes RED

| Teste | Referência do contrato | Tipo | Arquivo | Motivo esperado do RED | Resultado real | Evidência |
|---|---|---|---|---|---|---|
| | R/AC ou QC-* | HAPPY_PATH | | | EXPECTED_FAIL / UNEXPECTED_PASS / WRONG_FAILURE | |

## Matriz de edge cases

| Cenário | Origem | Status | Teste associado / Justificativa |
|---|---|---|---|
| | AC/regra/contrato/risco/QC-* | COVERED / NOT_APPLICABLE / DEFERRED_WITH_REASON | |

> Considerar somente quando aplicável: boundaries, `null`/ausência, vazio, inválidos, branches/estados,
> erros de dependência, exceções, duplicidade/idempotência, mapping/serialização e regressões adjacentes.

## Evidência não unitária planejada

| Referência do contrato | Tipo | Justificativa | Fase responsável |
|---|---|---|---|
| | INTEGRATION / STATIC_VERIFICATION / QA / EXTERNAL_VALIDATION | | |

## Ponte de risco para QA

| Risco QA/E2E | Referência do contrato | Teste unitário surrogate | `QA_SURROGATE` | Risco se não coberto |
|---|---|---|---|---|
| | | | true / false | |

## Regras
- cada item observável do contrato precisa de evidência planejada; não necessariamente teste unitário artificial;
- cada teste deve ter origem no contrato aprovado, risco ou decisão válida;
- RED só é válido quando falha pelo motivo esperado;
- edge case relevante não pode ser omitido silenciosamente;
- nenhuma alteração de produção nesta fase;
- após aprovação/execução válida, arquivos entram em `red-tests.lock`;
- mudança posterior de teste lockado exige recovery + `REOPEN RED`.
