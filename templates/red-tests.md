# Testes RED — <JIRA-ID>

## Mechanical readiness

```text
SPEC_APPROVED:
BLOCKING_OPEN_QUESTIONS:
AC_TOTAL:
AC_WITH_VERIFICATION:
UNTRACED_TESTS:
```

## Matriz de rastreabilidade

| Requisito | AC | PLAN | DD | Evidência planejada | Teste/artefato | Status |
|---|---|---|---|---|---|---|
| R-01 | AC-01 | PLAN-1 | | UNIT_TEST | | COVERED_PLANNED |

## Testes RED

| Teste | R-* | AC | Tipo | Arquivo | Motivo esperado do RED | Resultado real | Evidência |
|---|---|---|---|---|---|---|---|
| | R-01 | AC-01 | HAPPY_PATH | | | EXPECTED_FAIL / UNEXPECTED_PASS / WRONG_FAILURE | |

## Matriz de edge cases

| Cenário | Origem | Status | Teste associado / Justificativa |
|---|---|---|---|
| | AC/regra/contrato/risco | COVERED / NOT_APPLICABLE / DEFERRED_WITH_REASON | |

> Considerar somente quando aplicável: boundaries, `null`/ausência, vazio, inválidos, branches/estados,
> erros de dependência, exceções, duplicidade/idempotência, mapping/serialização e regressões adjacentes.

## Evidência não unitária planejada

| AC | Tipo | Justificativa | Fase responsável |
|---|---|---|---|
| | INTEGRATION / STATIC_VERIFICATION / QA / EXTERNAL_VALIDATION | | |

## Ponte de risco para QA

| Risco QA/E2E | AC/Regra | Teste unitário surrogate | `QA_SURROGATE` | Risco se não coberto |
|---|---|---|---|---|
| | | | true / false | |

## Regras
- cada AC precisa de evidência planejada; não necessariamente teste unitário artificial;
- cada teste deve ter origem em requisito/AC/risco/decisão aprovada;
- RED só é válido quando falha pelo motivo esperado;
- edge case relevante não pode ser omitido silenciosamente;
- nenhuma alteração de produção nesta fase;
- após aprovação/execução válida, arquivos entram em `red-tests.lock`;
- mudança posterior de teste lockado exige recovery + `REOPEN RED`.
