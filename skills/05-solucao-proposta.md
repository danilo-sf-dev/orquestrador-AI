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
Transformar fatos da investigação em uma solução mínima, coerente com o Jira e com a arquitetura atual.

## Inputs
- `00-jira.md`;
- memórias relevantes revalidadas;
- `01-discovery.md`;
- respostas de entrevista, se houver.

## Produzir
1. entendimento do problema/feature;
2. comportamento atual;
3. comportamento desejado;
4. gap;
5. solução recomendada;
6. impacto por repo;
7. contratos alterados ou preservados;
8. riscos/regressões;
9. alternativas descartadas;
10. itens fora de escopo;
11. questões ainda abertas.

## Não fazer
- não editar código;
- não criar testes ainda;
- não escrever plano detalhado antes da aprovação da solução.

## Gate
Parar e solicitar `APROVAR SOLUÇÃO`.

Somente após aprovação marcar:
```text
SOLUTION_APPROVED=true
```
