---
name: validacao-green
role: verification
preferred_model_role: EXECUTOR
writes: [07-green-evidence.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 01-requirements.md_if_exists
  - 03-spec.md_if_exists
  - 04-implementation-plan.md_if_exists
  - quick_contract_if_flow_mode_quick
  - 05-red-tests.md
  - red-tests.lock
  - 06-implementation-summary.md
  - source_code_changed_only
  - tests_locked_and_related
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
forbidden_writes:
  - locked_red_tests
  - source_code
  - tests
  - red-tests.lock
---

# Skill — Validação GREEN

## Objetivo
Demonstrar com evidência mecânica que a implementação atende ao contrato aprovado e aos testes selados
sem alterar o contrato para induzir aprovação.

No `STANDARD_GATED`, o contrato é a SPEC. No `QUICK_AUTOGO`, é o Quick Contract aprovado.

## Ordem
1. Validar hashes do `red-tests.lock` antes dos testes.
2. Compilar.
3. Rodar os testes RED aprovados, incluindo happy path e edge cases selados.
4. Conferir que a matriz aprovada continua representada pelos testes lockados.
5. Confirmar rastreabilidade do contrato para teste/evidência/resultado.
6. Rodar regressão proporcional ao risco.
7. Coletar contagens reais quando a ferramenta fornecer.
8. Validar hashes novamente.
9. Verificar `git diff` dos testes selados.

## Mechanical GREEN gate

`GREEN_STATUS=PASS` somente quando todos os checks obrigatórios aplicáveis estiverem satisfeitos:

```text
LOCK_BEFORE: VALID
COMPILE: PASS | NOT_APPLICABLE_WITH_REASON
RED_TESTS: PASS
RELATED_REGRESSION: PASS | NOT_APPLICABLE_WITH_REASON
UNEXPECTED_FAILURES: 0
UNEXPECTED_SKIPPED: 0
CONTRACT_WITH_EVIDENCE: <N>/<TOTAL>
LOCK_AFTER: VALID
LOCKED_TEST_DIFF: CLEAN
```

No STANDARD, `CONTRACT_WITH_EVIDENCE` usa `R/AC`. No QUICK, usa itens/comportamentos do Quick Contract.
Não inferir números ausentes; registrar `NOT_REPORTED` quando a ferramenta não fornecer contagem.

Evidência não unitária (`QA`, `INTEGRATION`, `STATIC_VERIFICATION`, `EXTERNAL_VALIDATION`) deve ficar
`PENDING_EXTERNAL` até a fase responsável. Evidência futura não vira prova atual.

## Resultado inválido
Se teste selado foi modificado sem reabertura RED:

```text
GREEN_STATUS=INVALID_GREEN
REASON=locked test modified
```

Não corrigir o lock para acomodar a alteração.

Se houver falha obrigatória:

```text
GREEN_STATUS=FAIL
```

Não avançar para Judge até corrigir implementação ou acionar recovery apropriado.

## Se RED realmente precisar mudar

```text
REOPEN_RED_REQUIRED=true
```

Parar, passar por recovery, obter autorização explícita, gerar novo RED/lock e só então retomar.

## `07-green-evidence.md`
Registrar:

```text
GREEN_STATUS:
FLOW_MODE:
LOCK_BEFORE:
COMPILE:
TEST_COMMANDS:
TESTS_REPORTED:
FAILURES:
ERRORS:
SKIPPED:
UNEXPECTED_FAILURES:
UNEXPECTED_SKIPPED:
CONTRACT_EVIDENCE_MATRIX:
RELATED_REGRESSION:
LOCK_AFTER:
LOCKED_TEST_DIFF:
LIMITATIONS:
QA_PENDING:
```

Matriz:

```text
STANDARD: R/AC -> TEST/EVIDENCE -> RESULT -> SOURCE
QUICK: CONTRACT_ITEM -> TEST/EVIDENCE -> RESULT -> SOURCE
```

Sem evidência verificável, usar `MISSING` ou `PENDING_EXTERNAL`; nunca `PASS` por interpretação.
