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
```

## Regras

- Apontar para artefatos; não copiar conteúdos longos sem necessidade.
- Não incluir transcript do agente anterior.
- Não incluir hipóteses rejeitadas, logs brutos ou buscas sem valor.
- `READ` é derivado do frontmatter da skill destino.
- `DO_NOT_READ` incorpora `forbidden_reads` da skill destino.
- `WRITE` respeita `writes` e `forbidden_writes`.
