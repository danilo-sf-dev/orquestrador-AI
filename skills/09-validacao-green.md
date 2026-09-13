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
Demonstrar com evidência mecânica que implementação atende contrato aprovado e testes selados sem alterar o contrato.
No STANDARD, contrato é a SPEC. No QUICK, é o Quick Contract.

## Ordem
1. Validar hashes do lock.
2. Compilar.
3. Rodar RED aprovado.
4. Conferir matriz aprovada.
5. Confirmar rastreabilidade contrato -> evidência -> resultado.
6. Rodar regressão proporcional.
7. Coletar contagens reais.
8. Validar hashes novamente.
9. Verificar diff dos testes selados.

## Mechanical GREEN gate

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

No STANDARD, usar `R/AC`; no QUICK, itens do Quick Contract. Evidência externa permanece `PENDING_EXTERNAL` até a fase responsável.

Se teste selado mudou sem reabertura: `GREEN_STATUS=INVALID_GREEN`. Se check obrigatório falhar: `GREEN_STATUS=FAIL`.

Se RED precisar mudar: `REOPEN_RED_REQUIRED=true` e recovery formal.

## `07-green-evidence.md`
Registrar status, flow mode, lock, compile, comandos, contagens reportadas, failures/errors/skips, matriz de evidência,
regressão, lock final, diff, limitações e QA pendente. Sem evidência, usar `MISSING` ou `PENDING_EXTERNAL`.
