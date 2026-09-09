---
name: arquivamento
role: memory_archive
preferred_model_role: ECONOMICAL
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 02-solution.md
  - 03-prd.md
  - 04-implementation-plan.md
  - 05-red-tests.md
  - 06-implementation-summary.md
  - 07-green-evidence.md
  - 08-judgement.md
  - 09-qa-tests.md
  - 10-qa-guide.md
  - delivery/commit.md_if_exists
  - delivery/pull-request.md_if_exists
  - legacy_11-commit.md_if_exists
  - legacy_12-pull-request.md_if_exists
writes:
  - 11-archive.md
  - STATE.md
  - .ai/FEATURE_INDEX.md
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - implementation_attempt_history
  - unrelated_feature_artifacts
forbidden_writes:
  - source_code
  - tests
  - approved_specs
---

# Skill — Arquivamento de feature

## Objetivo
Transformar a entrega em memória reutilizável para futuras histórias/bugs.

## Compatibilidade
`11-archive.md` é o nome canônico e estável da memória final. O número **não representa a fase cronológica**; ele é preservado para compatibilidade com features antigas.

- nunca renumerar o archive porque Commit/PR foram adicionados;
- `13-archive.md` pode ser lido como legado transitório, mas novas gravações usam somente `11-archive.md`;
- Commit e PR ficam em `delivery/`.

## Pré-condições
- Judge aprovado;
- QA resolvido conforme o fluxo:
  - `STANDARD_GATED`: QA aprovado;
  - `QUICK_AUTOGO`: QA aprovado **ou** `QA_NOT_REQUIRED_WITH_REASON`;
- commit concluído, delegado externamente ou dispensado explicitamente conforme política; `COMMIT_STATUS=DEFERRED` não satisfaz esta pré-condição e mantém o arquivamento bloqueado;
- PR resolvido como `OPENED`, `EXTERNAL`, `NOT_REQUESTED` ou `SKIPPED_BY_USER`;
- usuário autorizou `ARQUIVAR`.

## `11-archive.md`
Manter conciso e pesquisável:

```text
JIRA:
TITLE:
STATUS:
DATE:
REPOS:
ENDPOINTS:
MAIN_CLASSES:
FLOW_SUMMARY:
BUSINESS_RULES:
DECISIONS:
CONTRACTS:
TESTS:
QA_ASSETS:
COMMITS:
PULL_REQUESTS:
RISKS/LIMITATIONS:
RELATED_FEATURES:
SEARCH_TAGS:
```

## `STATE.md`
Manter como checkpoint final mínimo: `LIFECYCLE=DONE`, estados finais de Judge/QA/Commit/PR e referências curtas necessárias. Decisões, contratos, arquivos, riscos e histórico útil pertencem a `11-archive.md`, não devem inflar o STATE.

## `FEATURE_INDEX.md`
Adicionar entrada pequena pesquisável por:
- Jira;
- endpoint;
- classe;
- domínio;
- integração;
- repo;
- tag.

## Regra
O arquivo final é memória, não diário. Não arquivar transcript, logs gigantes ou tentativas descartadas. Nunca inventar SHA, número ou URL de PR.
