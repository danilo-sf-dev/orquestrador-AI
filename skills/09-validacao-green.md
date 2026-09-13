---
name: validacao-green
role: verification
preferred_model_role: EXECUTOR
writes: [07-green-evidence.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 01-requirements.md
  - 03-prd.md
  - 04-implementation-plan.md
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
Demonstrar com evidência mecânica que a implementação atende a SPEC/testes selados sem alterar o contrato
para induzir aprovação.

## Ordem
1. Validar hashes do `red-tests.lock` antes dos testes.
2. Compilar.
3. Rodar os testes unitários RED aprovados, incluindo happy path e edge cases selados.
4. Conferir que a matriz de edge cases aprovada continua representada pelos testes lockados.
5. Confirmar rastreabilidade `R/AC -> DD/PLAN -> teste/evidência -> resultado` para o escopo implementado.
6. Rodar testes relacionados/regressão proporcional ao risco.
7. Coletar contagens reais de execução quando a ferramenta fornecer.
8. Validar hashes novamente.
9. Verificar `git diff` dos arquivos de teste selados.

## Mechanical GREEN gate

`GREEN_STATUS=PASS` somente quando todos os checks obrigatórios aplicáveis estiverem satisfeitos:

```text
LOCK_BEFORE: VALID
COMPILE: PASS | NOT_APPLICABLE_WITH_REASON
RED_TESTS: PASS
RELATED_REGRESSION: PASS | NOT_APPLICABLE_WITH_REASON
UNEXPECTED_FAILURES: 0
UNEXPECTED_SKIPPED: 0
AC_WITH_EVIDENCE: <N>/<TOTAL>
LOCK_AFTER: VALID
LOCKED_TEST_DIFF: CLEAN
```

Não inferir números ausentes. Se a ferramenta não fornecer contagem, registrar `NOT_REPORTED` e usar a
evidência disponível sem fabricar precisão.

Um AC que dependa de evidência não unitária pode usar `QA`, `INTEGRATION`, `STATIC_VERIFICATION` ou
`EXTERNAL_VALIDATION`, mas deve ficar explicitamente `PENDING_EXTERNAL` até a fase responsável. Isso
pode resultar em GREEN técnico `PASS` com limitação registrada; não transforma evidência futura em prova atual.

## Resultado inválido
Se qualquer teste selado tiver sido modificado sem reabertura RED:

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

## Se o teste realmente precisar mudar
Voltar à skill RED:

```text
REOPEN_RED_REQUIRED=true
```

Explicar motivo, obter aprovação via recovery, gerar novo lock, então retomar.

## `07-green-evidence.md`
Registrar:

```text
GREEN_STATUS:
LOCK_BEFORE:
COMPILE:
TEST_COMMANDS:
TESTS_REPORTED:
FAILURES:
ERRORS:
SKIPPED:
UNEXPECTED_FAILURES:
UNEXPECTED_SKIPPED:
AC_EVIDENCE_MATRIX:
RELATED_REGRESSION:
LOCK_AFTER:
LOCKED_TEST_DIFF:
LIMITATIONS:
QA_PENDING:
```

Na `AC_EVIDENCE_MATRIX`, usar:

```text
AC-* -> TEST/EVIDENCE -> RESULT -> SOURCE
```

Sem evidência verificável, usar `MISSING` ou `PENDING_EXTERNAL`; nunca `PASS` por interpretação.
