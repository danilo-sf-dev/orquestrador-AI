---
name: implementacao-go
role: implementation
preferred_model_role: EXECUTOR
writes: [source_code, 06-implementation-summary.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 03-prd.md
  - 04-implementation-plan.md
  - 05-red-tests.md
  - red-tests.lock
  - source_code_relevant_only
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - rejected_hypotheses_history
  - all_feature_artifacts
forbidden_writes:
  - locked_red_tests
  - approved_prd
  - approved_plan
  - acceptance_criteria
---

# Skill — Implementação GO

## Pré-condições
- solução aprovada;
- PRD/plano aprovados;
- RED aprovado e selado;
- usuário disse `GO` ou equivalente.

## Objetivo
Implementar o mínimo necessário para satisfazer o plano e levar os testes selados a GREEN.

## Regras
1. Ler `red-tests.lock` antes de editar.
2. Não modificar testes RED selados.
3. Seguir padrões do projeto e arquitetura existente.
4. Evitar refactor fora de escopo salvo necessidade comprovada.
5. Em cross-repo, preservar contrato e ordem de deploy definida.
6. Registrar decisões emergentes em `STATE.md`.
7. Se surgir decisão arquitetural nova que muda o plano, parar e escalar ao `HEAD_STRONG`.
8. Se um teste RED estiver incorreto, parar e pedir `REOPEN RED`.

## `06-implementation-summary.md`
Guardar somente:
- arquivos alterados;
- comportamento implementado;
- decisões novas aprovadas;
- desvios do plano;
- pendências;
- riscos.

Não guardar transcript detalhado de tentativas, greps ou erros já resolvidos.
