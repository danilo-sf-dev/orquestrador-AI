---
name: scenario-cross-repo
load_mode: on_demand
context_loading: lazy
reads:
  - STATE.md
  - scenario_signal_only
forbidden_reads:
  - chat_transcript
  - unrelated_feature_artifacts
writes:
  - STATE.md
---

# Cenário — Mudança cross-repo

## Quando usar
Uma história/bug altera ou depende de dois ou mais repositórios que se chamam ou compartilham contrato.

## Regra principal
Este cenário **não define pipeline próprio**. Estados, gates, papéis e transições vêm exclusivamente do
`orquestrador.md` e da skill atual.

## Memória canônica
Criar uma única pasta canônica:

```text
.ai/features/<JIRA-ID>/
```

Nos demais repos, quando um ponteiro local for necessário, usar somente:

```text
.ai/FEATURE-LINK.md
```

Nunca criar `FEATURE-LINK.md` versionado fora de `.ai/` por padrão.

No `STATE.md`, manter apenas checkpoint curto:

```text
CANONICAL_HOME:
REPOSITORIES: []
```

Não duplicar schemas, erros, auth, compatibilidade ou detalhes de contrato no STATE.

## Contrato cross-repo
Detalhes pertencem à SPEC/plano:

```text
SOURCE_REPO:
TARGET_REPO:
INTERACTION: REST|EVENT|DB|OTHER
ENDPOINT/TOPIC:
REQUEST_SCHEMA:
RESPONSE_SCHEMA:
ERRORS:
AUTH/HEADERS:
COMPATIBILITY:
DEPLOY_ORDER:
ROLLBACK:
```

## Delta deste cenário
- Discovery rastreia ambos os lados do contrato antes de fechar requisitos/design.
- Requirement Analysis verifica compatibilidade, consumidores e deploy coupling aplicáveis.
- RED cria verificações dos dois lados quando tecnicamente possível.
- Implementação pode alternar repos, preservando um único `STATE.md` canônico.
- Judge avalia compatibilidade/end-to-end conceitual, não apenas testes isolados de um repo.
- Para risco alto, usar `JUDGE_SECONDARY` como reforço independente.
- Commit trata cada repo separadamente, preservando contrato, compatibilidade e ordem.
- Archive indexa endpoints/contratos/classes de ambos na memória canônica; ponteiros locais continuam em `.ai/`.

## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes
não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com
critérios, regras, contratos ou riscos.
