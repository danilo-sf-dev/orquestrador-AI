# HANDOFF PACKET — <JIRA-ID>

> Artefato preferencialmente efêmero. Persistir somente quando necessário para retomada/auditoria.

```yaml
JIRA:
CURRENT_STATE:
NEXT_STATE:
EXECUTION_LEVEL:
ROLE:
OBJECTIVE:
CONTEXT_MODE: SAME_CHAT | COMPACT_CONTEXT | FRESH_CONTEXT

READ:
  -

DO_NOT_READ:
  - documentacao-usuario/**
  - chat_transcript_as_evidence
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

- `SAME_CHAT` é o padrão: trocar modelo/papel dentro da mesma conversa.
- `COMPACT_CONTEXT` mantém a mesma sessão, mas compacta/resume o histórico para reduzir contexto quando o runtime suportar (no VS Code, `/compact`).
- `FRESH_CONTEXT` é explícito e excepcional; inicia nova sessão/contexto e não é consequência automática de mudar de modelo.
- `/clear` no VS Code equivale a iniciar uma nova sessão; não usar como sinônimo de compactação.
- Apontar para artefatos; não copiar conteúdos longos sem necessidade.
- Nunca incluir `documentacao-usuario/**`; o path é HUMAN_ONLY global.
- Em `FRESH_CONTEXT`, não incluir transcript do agente anterior.
- Em `SAME_CHAT`/`COMPACT_CONTEXT`, o transcript pode existir no harness, mas não deve ser tratado como evidência quando a skill o proíbe.
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
CONTEXT_MODE: SAME_CHAT | COMPACT_CONTEXT | FRESH_CONTEXT
CONFIRMATION_PHRASE:
```

`MODEL_HANDOFF_REQUIRED=true` significa **trocar para o papel/modelo exigido**. Sozinho, não significa abrir novo chat.

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
