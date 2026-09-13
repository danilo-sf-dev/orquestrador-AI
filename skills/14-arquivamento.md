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
  - 03-spec.md_if_exists
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
Transformar entrega em memória reutilizável, preservando apenas decisões, contratos e padrões caros de redescobrir.

## Compatibilidade
`11-archive.md` é canônico. `13-archive.md` pode ser lido como legado. Commit/PR ficam em `delivery/`.
Ao ler features antigas, `03-prd.md` representa o predecessor histórico da atual `03-spec.md`; usar seu conteúdo
somente como memória revalidável, sem propagar nomenclatura PRD para novas features.

## Pré-condições
- Judge aprovado;
- QA resolvido conforme fluxo;
- commit concluído, externo ou dispensado; `DEFERRED` bloqueia archive;
- PR resolvido conforme política;
- usuário autorizou `ARQUIVAR`.

## `11-archive.md`
Guardar Jira, título, status, data, repos, endpoints, classes principais, resumo de fluxo/requisitos,
decisões, regras, contratos, testes, QA, commits, PRs, riscos/limitações, relacionadas e tags.

Não copiar requirements/design/SPEC integralmente. Extrair somente conhecimento reutilizável.

## `STATE.md`
Manter checkpoint final mínimo com `LIFECYCLE=DONE` e estados finais.

## `FEATURE_INDEX.md`
Adicionar entrada pequena pesquisável por Jira, endpoint, classe, domínio, integração, repo e tag.

## Regra
Archive é memória, não diário. Não guardar transcript, logs gigantes, assumptions descartadas ou tentativas.
Nunca inventar SHA, número ou URL de PR.
