# Testes RED — <JIRA-ID>

| AC/Regra/Risco | PLAN | DD | Tipo | Teste | Arquivo | Motivo do RED | Evidência | Aprovado |
|---|---|---|---|---|---|---|---|---|
| AC1 | PLAN-1 | | HAPPY_PATH | | | | | |
| AC1 | PLAN-1 | DD-1 | EDGE_CASE | | | | | |

## Matriz de edge cases

| Cenário | Origem | Status | Teste associado / Justificativa |
|---|---|---|---|
| | AC/regra/contrato/risco | COVERED / NOT_APPLICABLE / DEFERRED_WITH_REASON | |

> Considerar somente quando aplicável: boundaries, `null`/ausência, vazio, inválidos, branches/estados, erros de dependência, exceções, duplicidade/idempotência, mapping/serialização e regressões adjacentes.

## Ponte de risco para QA

| Risco QA/E2E | AC/Regra | Teste unitário surrogate | `QA_SURROGATE` | Risco se não coberto |
|---|---|---|---|---|
| | | | true / false | |

> `QA_SURROGATE=true` indica que o teste unitário protege antecipadamente um risco importante que também será validado pelo QA. Ele **não substitui** o teste de QA/Postman/Insomnia. Priorizar riscos reais; evitar explosão combinatória de casos.

## Regras
- cada critério deve ter happy path e análise explícita de edge cases;
- edge case relevante não pode ser omitido silenciosamente;
- nenhuma alteração de produção nesta fase;
- após aprovação, os arquivos entram em `red-tests.lock`;
- qualquer mudança posterior exige `REOPEN RED`.
