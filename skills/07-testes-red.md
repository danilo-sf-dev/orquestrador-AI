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

Esta skill possui **dois estados canônicos diferentes** e não pode misturá-los:

```text
RED_REVIEW
= desenhar/revisar o contrato RED + pedir aprovação

RED_EXECUTION
= materializar os testes aprovados + comprovar falha esperada + gerar lock
```

`RED_REVIEW` não cria nem altera arquivos de teste de produção do repositório.
`RED_EXECUTION` só começa após `RED_APPROVED=true`.

---

## Estado `RED_REVIEW`

### Pré-condição

```yaml
SOLUTION_APPROVED: true
SPEC_PLAN_APPROVED: true
SPEC_STATUS: APPROVED
BLOCKING_OPEN_QUESTIONS: 0
```

Papel atual: `EXECUTOR`.

Se a SPEC contiver pergunta aberta bloqueante ou requisito sem origem, parar; RED não deve preencher
lacuna de produto/negócio por inferência.

### Objetivo

Produzir o **plano executável do RED** em `05-red-tests.md`, cobrindo happy path e edge cases aplicáveis,
sem ainda editar os testes do repositório.

### Mechanical readiness gate

Antes de pedir `APROVAR RED`, verificar mecanicamente a rastreabilidade:

```text
SPEC_APPROVED = true
BLOCKING_OPEN_QUESTIONS = 0
AC_TOTAL = <N>
AC_WITH_VERIFICATION = <N>
UNTRACED_TESTS = 0
```

Cada `AC-*` deve ter pelo menos uma evidência planejada:

```text
UNIT_TEST | INTEGRATION | STATIC_VERIFICATION | QA | EXTERNAL_VALIDATION
```

Para comportamento coberto por teste unitário, apontar o teste RED planejado. Para AC não unit-testable,
registrar a evidência alternativa e justificativa; não inventar teste artificial apenas para obter 100%.

`AC_WITH_VERIFICATION < AC_TOTAL` bloqueia o gate.

### Regras

1. Ler somente código/testes relevantes em modo read-only.
2. Mapear cada teste planejado para `R-*`, `AC-*`, risco e `PLAN-*`; incluir `DD-*` quando a decisão
   arquitetural determinar o comportamento verificado.
3. Identificar happy path e edge cases aplicáveis.
4. Não criar edge cases artificiais.
5. Para cada cenário, marcar `COVERED_PLANNED`, `NOT_APPLICABLE` ou `DEFERRED_WITH_REASON`.
6. Mostrar ao usuário o conjunto planejado e a matriz de edge cases.
7. Não escrever código de produção.
8. Não criar `red-tests.lock` neste estado.
9. Não afirmar que RED foi comprovado antes de executar os testes.
10. Teste sem origem em requisito/AC/risco/decisão aprovada não entra silenciosamente no RED.

### Matriz mínima

```text
R-* -> AC-* -> PLAN-* -> TEST/OTHER_EVIDENCE -> STATUS
```

### Gate

No caminho normal, solicitar exatamente:

```text
APROVAR RED
```

Após aprovação:

```yaml
RED_APPROVED: true
CURRENT_STATE: RED_EXECUTION
NEXT_ACTION: EXECUTE_RED
NEXT_MODEL_ROLE: EXECUTOR
```

### Modo de reabertura já autorizado

Se `NEXT_ACTION=APPLY_APPROVED_RED_REOPEN_DELTA` e existir recovery aprovado por `REOPEN RED`:

1. aplicar em `05-red-tests.md` **somente o delta documentado em `recovery/judge-recovery-<N>.md`**;
2. mostrar o delta aplicado de forma resumida;
3. não pedir um segundo `APROVAR RED`;
4. seguir para `RED_EXECUTION`;
5. o lock anterior permanece inválido até a nova execução gerar outro lock.

Não avançar diretamente para `WAITING_GO`.

---

## Estado `RED_EXECUTION`

### Pré-condições

```yaml
RED_APPROVED: true
CURRENT_STATE: RED_EXECUTION
```

### Objetivo

Materializar exatamente o contrato aprovado em `05-red-tests.md`, executar os testes, comprovar a falha
esperada e selar o lock.

### Regras

1. Criar/alterar somente arquivos de teste necessários ao RED aprovado.
2. Não ampliar silenciosamente escopo, critérios ou matriz de testes.
3. Cada teste novo deve corresponder a `R-*`/`AC-*`, `PLAN-*` e uma origem aprovada; teste sem
   rastreabilidade deve ser removido ou voltar para revisão.
4. O RED deve falhar pelo motivo esperado para comportamento ainda não implementado.
5. Se um teste passar inesperadamente, investigar antes de seguir:
   - comportamento já existe;
   - teste não atinge a regra;
   - mock mascara comportamento;
   - critério já está atendido.
6. Nunca enfraquecer assert para fabricar RED/GREEN.
7. Registrar em `05-red-tests.md` a evidência real da execução.
8. Se durante a execução surgir descoberta que invalide ou coloque em dúvida requisito, SPEC/plano ou o próprio contrato RED, **parar**. Não redesenhar RED sozinho.
9. Nesse caso registrar:

```yaml
RECOVERY_STATUS: REQUIRED
RECOVERY_SOURCE: RED_EXECUTION
RECOVERY_CLASS: CONTRACT_MISMATCH
CURRENT_STATE: JUDGE_RECOVERY
NEXT_ACTION: ANALYZE_TARGETED_RECOVERY
NEXT_MODEL_ROLE: HEAD_STRONG
```

10. Somente após RED válido gerar `red-tests.lock`.

### Evidência RED

Registrar por teste material:

```text
TEST_ID:
REQUIREMENT: R-*
AC: AC-*
EXPECTED_RED_REASON:
ACTUAL_RED_REASON:
RESULT: EXPECTED_FAIL | UNEXPECTED_PASS | WRONG_FAILURE
```

`WRONG_FAILURE` e `UNEXPECTED_PASS` não podem ser tratados como RED comprovado.

### Lock

Gerar `red-tests.lock` com:

- caminhos dos testes protegidos;
- hash SHA-256 ou `git hash-object` de cada arquivo;
- timestamp/commit base quando disponível.

Exemplo:

```text
RED_LOCK_VERSION=1
FILE=src/test/.../FooTest.java SHA256=...
FILE=src/test/.../BarTest.java SHA256=...
```

Depois:

```yaml
RED_LOCKED: true
CURRENT_STATE: WAITING_GO
NEXT_ACTION: REQUEST_GO
NEXT_MODEL_ROLE: EXECUTOR
```

---

## Edge cases

Cobrir quando aplicável:

- boundaries;
- `null`, ausência e opcionais;
- strings/coleções vazias;
- inválidos e combinações inválidas;
- branches condicionais;
- erro/timeout/resposta inesperada de dependências mockadas;
- exceções e mapeamento de erro;
- duplicidade/idempotência;
- mapping/serialização/conversões;
- regressões adjacentes.

Para risco de alta visibilidade em QA/E2E, registrar `QA_SURROGATE=true` quando tecnicamente possível. Se
só puder ser provado integrado/E2E, usar `QA_ONLY` com justificativa.

---

## Proteção futura

Após `RED_LOCKED=true`, testes protegidos não podem ser alterados por implementação, GREEN ou rework normal.

A única exceção é fluxo formal de recuperação que termine em autorização humana explícita:

```text
REOPEN RED
```

Essa autorização invalida o lock anterior e exige nova `RED_EXECUTION` + novo lock.
