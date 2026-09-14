# HANDOFF PACKET — <JIRA-ID>

> Artefato preferencialmente efêmero. Persistir somente quando necessário para retomada/auditoria.

```yaml
JIRA:
CURRENT_STATE:
NEXT_STATE:
EXECUTION_LEVEL:
ROLE:
OBJECTIVE:

READ:
  -

DO_NOT_READ:
  - documentacao-usuario/**
  - chat_transcript
  - raw_discovery_logs

CONSTRAINTS:
  -

APPROVED_DECISIONS:
  -

PENDING:
  -

WRITE:
  -

EXPECTED_OUTPUT:

RECOVERY_SOURCE: # somente em recovery
RECOVERY_CLASS: # somente em recovery
RECOVERY_DECISION: # somente em recovery
```

## Regras

- Apontar para artefatos; não copiar conteúdos longos sem necessidade.
- Nunca incluir `documentacao-usuario/**`; o path é HUMAN_ONLY global.
- Não incluir transcript do agente anterior.
- Não incluir hipóteses rejeitadas, logs brutos ou buscas sem valor.
- `READ` é derivado do frontmatter da skill destino.
- `DO_NOT_READ` incorpora `forbidden_reads` da skill destino.
- `WRITE` respeita `writes` e `forbidden_writes`.

## Model routing

```yaml
CURRENT_MODEL_ROLE:
NEXT_MODEL_ROLE:
ROUTING_MODE:
MODEL_HANDOFF_REQUIRED:
CONFIRMATION_PHRASE:
```

## Recovery dirigido

Quando `RECOVERY_STATUS=REQUIRED|IN_PROGRESS`, o handoff deve incluir somente o trigger/finding relevante
e sua classificação.

```yaml
RECOVERY_STATUS:
RECOVERY_SOURCE:
RECOVERY_CLASS:
TRIGGER_OR_FINDING_ID:
RECOVERY_ARTIFACT:
```

Não repassar o histórico completo das tentativas do executor.
