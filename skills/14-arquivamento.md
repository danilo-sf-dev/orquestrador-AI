---
name: arquivamento
role: memory_archive
preferred_model_role: ECONOMICAL
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md_if_exists
  - 01-requirements.md_if_exists
  - 01-quality-review.md_if_exists
  - 02-design.md_if_exists
  - 02-solution.md_if_exists
  - 03-prd.md_if_exists
  - 04-implementation-plan.md_if_exists
  - 05-red-tests.md
  - 06-implementation-summary.md
  - 07-green-evidence.md
  - 08-judgement.md
  - 09-qa-tests.md_if_exists
  - 10-qa-guide.md_if_exists
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
Transformar a entrega em memória reutilizável para futuras histórias/bugs, preservando apenas decisões,
contratos e padrões que seriam caros de redescobrir.

## Compatibilidade
`11-archive.md` é o nome canônico e estável da memória final. O número não representa fase cronológica.
`13-archive.md` pode ser lido como legado; novas gravações usam `11-archive.md`. Commit/PR ficam em `delivery/`.

## Pré-condições
- Judge aprovado;
- QA resolvido conforme o fluxo (`STANDARD_GATED`: aprovado; QUICK: aprovado ou `QA_NOT_REQUIRED_WITH_REASON`);
- commit concluído, externo ou dispensado explicitamente; `COMMIT_STATUS=DEFERRED` mantém archive bloqueado;
- PR resolvido como `DESCRIPTION_READY`, `NOT_REQUESTED` ou `SKIPPED_BY_USER` conforme política vigente;
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
REQUIREMENTS_SUMMARY:
DESIGN_DECISIONS:
BUSINESS_RULES:
CONTRACTS:
TESTS:
QA_ASSETS:
COMMITS:
PULL_REQUESTS:
RISKS/LIMITATIONS:
RELATED_FEATURES:
SEARCH_TAGS:
```

Não copiar `01-requirements.md`, `02-design.md` ou SPEC integralmente. Extrair somente conhecimento
reutilizável: decisão material, contrato, boundary, regra de negócio ou padrão comprovado.

## `STATE.md`
Manter checkpoint final mínimo: `LIFECYCLE=DONE`, estados finais de Judge/QA/Commit/PR e referências
curtas. Decisões, contratos, riscos e histórico útil ficam em `11-archive.md`.

## `FEATURE_INDEX.md`
Adicionar entrada pequena pesquisável por Jira, endpoint, classe, domínio, integração, repo e tag.

## Regra
O archive é memória, não diário. Não guardar transcript, logs gigantes, assumptions descartadas ou
tentativas de implementação. Nunca inventar SHA, número ou URL de PR.
