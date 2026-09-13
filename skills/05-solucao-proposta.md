---
name: solucao-proposta
role: decision
preferred_model_role: HEAD_STRONG
writes: [02-solution.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 01-requirements.md
  - 02-design.md
  - 01-quality-review.md # somente quando presente
  - related_feature_memory_selected_only
  - approved_human_decisions
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - rejected_hypotheses_history
forbidden_writes:
  - source_code
  - tests
---

# Skill — Solução proposta

## Objetivo
Revisar e consolidar o design técnico em uma solução mínima, coerente com Jira, requisitos e arquitetura,
apresentando ao usuário somente decisões materiais para o gate `APROVAR SOLUÇÃO`.

A análise técnica detalhada ocorre em `04b-design-solucao.md`; esta skill não refaz design do zero.

## Pré-condições

```yaml
REQUIREMENT_ANALYSIS_STATUS: COMPLETE
SOLUTION_DESIGN_STATUS: COMPLETE
BLOCKING_OPEN_QUESTIONS: 0
```

## Inputs
- `00-jira.md`;
- `01-discovery.md`;
- `01-requirements.md`;
- `02-design.md`;
- memórias relevantes revalidadas;
- respostas humanas aprovadas;
- `01-quality-review.md`, somente quando ativada.

## Validar antes do gate
1. todo requisito material está atendido ou explicitamente fora de escopo;
2. nenhuma `OPEN_QUESTION BLOCKING=YES` permanece;
3. assumptions de alto impacto têm evidência/mitigação;
4. `OPTIONAL_IMPROVEMENT` não entrou silenciosamente no escopo;
5. boundaries, contratos e consumidores materiais estão explícitos;
6. solução não contradiz discovery/decisões humanas;
7. alternativa materialmente melhor foi tratada;
8. mudança proposta é a menor suficiente.

## Produzir `02-solution.md`
Registrar problema, comportamento atual/desejado, requisitos cobertos, solução recomendada, impacto por
repo, contratos/boundaries, riscos/mitigação, assumptions materiais, alternativas descartadas e itens fora de escopo.

## Decisão arquitetural proporcional

```text
DECISION_ID: DD-<N>
SOURCE_DESIGN: SD-<N>
REQUIREMENTS: [R-...]
CONTEXT:
CONSTRAINTS:
SELECTED_OPTION:
ALTERNATIVES_CONSIDERED:
TRADE_OFFS_ACCEPTED:
CONSEQUENCES:
VALIDATION:
CONFIDENCE: HIGH | MEDIUM | LOW
```

Não criar `DD-*` para detalhe trivial.

## Gate
Parar e solicitar `APROVAR SOLUÇÃO`.

Somente após aprovação:

```yaml
SOLUTION_APPROVED: true
CURRENT_STATE: SPEC_PLAN_REVIEW
NEXT_ACTION: BUILD_SPEC_AND_PLAN
```
