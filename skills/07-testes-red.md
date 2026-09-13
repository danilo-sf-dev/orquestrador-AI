---
name: testes-red
role: test-design
preferred_model_role: EXECUTOR
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-requirements.md
  - 03-spec.md
  - 04-implementation-plan.md
  - source_code_relevant_read_only
  - existing_tests_relevant_only
writes:
  - 05-red-tests.md
  - STATE.md
  - test_files_only_when_state_is_RED_EXECUTION
  - red-tests.lock_only_when_state_is_RED_EXECUTION
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - unrelated_source_files
forbidden_writes:
  - production_code
  - approved_spec
  - approved_plan
---

# Skill — Testes RED

## Princípio

```text
RED_REVIEW
= desenhar/revisar contrato RED + pedir aprovação

RED_EXECUTION
= materializar testes aprovados + comprovar falha esperada + gerar lock
```

`RED_REVIEW` não cria/altera testes do repositório. `RED_EXECUTION` só começa após `RED_APPROVED=true`.

## Estado `RED_REVIEW`

### Pré-condição

```yaml
SOLUTION_APPROVED: true
SPEC_PLAN_APPROVED: true
SPEC_STATUS: APPROVED
BLOCKING_OPEN_QUESTIONS: 0
```

### Objetivo
Produzir o plano executável do RED em `05-red-tests.md`, cobrindo happy path e edge cases aplicáveis.

### Mechanical readiness gate

```text
SPEC_APPROVED = true
BLOCKING_OPEN_QUESTIONS = 0
AC_TOTAL = <N>
AC_WITH_VERIFICATION = <N>
UNTRACED_TESTS = 0
```

Cada AC deve ter evidência planejada: `UNIT_TEST | INTEGRATION | STATIC_VERIFICATION | QA | EXTERNAL_VALIDATION`.
`AC_WITH_VERIFICATION < AC_TOTAL` bloqueia o gate.

### Regras
1. Ler somente código/testes relevantes em read-only.
2. Mapear teste para `R-*`, `AC-*`, risco, `PLAN-*` e `DD-*` quando aplicável.
3. Cobrir edge cases aplicáveis sem criar casos artificiais.
4. Não criar `red-tests.lock` em revisão.
5. Teste sem origem aprovada não entra silenciosamente.

### Gate
Solicitar `APROVAR RED`.

Após aprovação:

```yaml
RED_APPROVED: true
CURRENT_STATE: RED_EXECUTION
NEXT_ACTION: EXECUTE_RED
```

### Reabertura já autorizada
Se `NEXT_ACTION=APPLY_APPROVED_RED_REOPEN_DELTA`, aplicar somente delta do recovery aprovado por `REOPEN RED`,
sem pedir segundo `APROVAR RED`; depois executar novo RED e gerar novo lock.

## Estado `RED_EXECUTION`

```yaml
RED_APPROVED: true
CURRENT_STATE: RED_EXECUTION
```

Criar/alterar somente testes necessários ao RED aprovado. Cada teste deve corresponder a requisito/AC/plano.
RED válido falha pelo motivo esperado. `UNEXPECTED_PASS` ou `WRONG_FAILURE` não contam como RED comprovado.

Se surgir descoberta que invalide contrato:

```text
RED_EXECUTION_BLOCKED
REASON=NEW_DISCOVERY_OR_CONTRACT_MISMATCH
NEXT_STATE=JUDGE_RECOVERY
```

Após RED válido, gerar `red-tests.lock` com caminhos e hashes e então:

```yaml
RED_LOCKED: true
CURRENT_STATE: WAITING_GO
NEXT_ACTION: REQUEST_GO
```

## Edge cases
Cobrir quando aplicável boundaries, null/ausência, vazio, inválidos, branches, erro/timeout de dependências,
exceções, duplicidade/idempotência, mapping/serialização e regressões adjacentes.

## Proteção futura
Após `RED_LOCKED=true`, testes protegidos não podem ser alterados por implementação, GREEN ou rework normal.
A única exceção é recovery formal + autorização `REOPEN RED`, que invalida o lock e exige nova execução RED.
