---
name: memoria-feature
role: memory
preferred_model_role: ECONOMICAL
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - .ai/FEATURE_INDEX.md
  - related_feature_archives_selected_only
  - source_code_selected_for_revalidation
writes:
  - STATE.md
forbidden_reads:
  - all_features_full_content
  - chat_transcript
  - raw_discovery_logs
forbidden_writes:
  - source_code
  - tests
---

# Skill — Memória de feature

## Objetivo
Evitar reinvestigação do zero e reaproveitar decisões anteriores com validação do estado atual.

## Busca obrigatória
Antes de discovery amplo, pesquisar em `.ai/FEATURE_INDEX.md` e `.ai/features/` por:

1. Jira ID exato;
2. endpoint/URL;
3. controller/use case/service;
4. nomes de DTO/evento/tópico;
5. termos do domínio;
6. features relacionadas citadas no Jira;
7. repositórios envolvidos.

## Arquivo histórico canônico
Ao encontrar uma feature relacionada:

1. preferir `11-archive.md`;
2. se não existir, aceitar `13-archive.md` como legado transitório de versões anteriores;
3. não carregar todos os arquivos da feature por padrão;
4. carregar somente decisões/contratos necessários ao delta atual.

Se existirem registros antigos `11-commit.md` / `12-pull-request.md`, tratá-los como legado. Novas features usam `delivery/commit.md` e `delivery/pull-request.md`.

## Revalidação
Após recuperar memória, verificar se o código atual ainda corresponde a endpoints, classes, contratos e decisões reutilizadas.

## Saída em `STATE.md`

```text
RELATED_FEATURES:
- JIRA-....
MEMORY_REUSED:
- ...
STALE_RISKS:
- ...
DELTA_TO_VALIDATE:
- ...
```

## Regra
Memória reduz investigação; nunca substitui validação do estado atual.
