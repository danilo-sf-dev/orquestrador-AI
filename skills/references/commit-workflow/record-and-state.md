# Commit — registro, estado e resultado

Ler quando uma decisão de commit precisar ser persistida ou quando o resultado for apresentado.

## Registro `delivery/commit.md`

Registrar somente fatos:

```text
JIRA:
FLOW:
COMMIT_MODE: AUTO | MANUAL | OTHER
MEMORY_POLICY: LOCAL_ONLY

REPO:
BRANCH:
BASE_SHA:
GATES:
VALIDATIONS:
RED_LOCK_STATUS:
JUDGEMENT_SCOPE_HASH_STATUS:
COMMIT_PLAN_STATUS: PROPOSED | APPROVED | EXECUTED | DEFERRED | EXTERNAL | SKIPPED
COMMIT_GROUPS:
  - ORDER:
    TYPE:
    INTENT:
    FILES:
    MESSAGE_PTBR:
    MESSAGE_EN:
    EXECUTION_STATUS: PLANNED | COMMITTED | NOT_EXECUTED
    SHA:
EXCLUDED_FILES:
SKIPPED_VALIDATIONS:
RISKS_NOTES:
```

Repetir o bloco de repo em cross-repo. Nunca inventar SHA.

## Estado

Ao entrar:

```text
COMMIT_MODE=AUTO | MANUAL | OTHER
COMMIT_PLAN_STATUS=PENDING | PROPOSED | APPROVED | EXECUTED | DEFERRED | EXTERNAL | SKIPPED
```

Após execução:

```text
COMMIT_PLAN_STATUS=EXECUTED
COMMIT_STATUS=COMMITTED
COMMIT_COUNT=<n>
COMMIT_SHAS=<sha1,sha2,...>
```

Se adiado: `COMMIT_PLAN_STATUS=DEFERRED`, `COMMIT_STATUS=DEFERRED`.

Se delegado ao usuário/fluxo externo: `COMMIT_PLAN_STATUS=EXTERNAL`, `COMMIT_STATUS=EXTERNAL`.

Se dispensado explicitamente: `COMMIT_PLAN_STATUS=SKIPPED`,
`COMMIT_STATUS=SKIPPED_BY_USER`.

`DEFERRED` não satisfaz a pré-condição de arquivamento.

## Resultado ao usuário

No `MANUAL` ainda não executado, mostrar o plano completo e terminar com `POSSO COMITAR`,
`PRECISA AJUSTAR` e `OUTROS`.

Após execução, mostrar por commit:

```text
COMMIT <N> — COMMITTED
TYPE:
INTENT:
FILES:
MESSAGE_PTBR:
MESSAGE_EN_COMMITTED:
SHA:
```

Também informar de forma compacta: modo/política, repos/branches, convenções e ferramentas detectadas,
gates, RED/Judge, inclusões/exclusões, validações puladas e pendências de arquivamento.
