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
Transformar fatos da investigação em uma solução mínima, coerente com o Jira e com a arquitetura atual.

## Inputs
- `00-jira.md`;
- memórias relevantes revalidadas;
- `01-discovery.md`;
- respostas de entrevista, se houver.
- `01-quality-review.md`, somente quando a revisão opcional tiver sido ativada.

## Entrada opcional de qualidade arquitetural

Uma recomendação `TQ-*` não é uma decisão aprovada nem obrigação de implementação. Considerá-la
somente se resolver o requisito atual ou um risco técnico material que a solução local preservaria.
Revalidar aderência às convenções do projeto, custo de migração, compatibilidade e alternativa mais
simples antes de promovê-la a `DD-*`.

Não introduzir pattern, camada ou arquitetura apenas porque a revisão os listou. `NO_CHANGE` e
`LOCAL_REFACTOR` são resultados válidos. Se uma recomendação for selecionada, registrar seu `TQ-*`
como evidência no `DD-*`; se for rejeitada, resumir o motivo quando isso evitar reabertura da decisão.

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

## Decisão arquitetural proporcional

Não transformar toda alteração em exercício de arquitetura. Aplicar análise formal quando houver
decisão material sobre contrato público, persistência/migração, transação, concorrência, segurança,
integração, compatibilidade cross-repo, dependência nova ou mudança difícil de reverter.

Para cada decisão material:

1. declarar problema, restrições e requisitos não funcionais relevantes;
2. priorizar padrões já confirmados no discovery;
3. comparar somente opções realmente viáveis;
4. avaliar aderência ao requisito, complexidade, manutenção, segurança, desempenho, risco e
   reversibilidade;
5. recomendar a opção de menor complexidade que satisfaça as restrições;
6. explicitar trade-offs aceitos e como validar a decisão.

Se houver apenas uma solução razoável, registrar uma recomendação direta. Apresentar duas ou três
opções ao usuário somente quando as consequências forem materialmente diferentes e a escolha não
puder ser inferida das decisões já aprovadas.

Registrar decisões importantes em formato ADR-lite dentro de `02-solution.md`:

```text
DECISION_ID: DD-<N>
CONTEXT:
CONSTRAINTS:
SELECTED_OPTION:
ALTERNATIVES_CONSIDERED:
TRADE_OFFS_ACCEPTED:
CONSEQUENCES:
VALIDATION:
CONFIDENCE: HIGH | MEDIUM | LOW
```

Não escolher um padrão apenas pelo nome nem introduzir abstração, serviço ou camada sem problema
concreto. Quando a arquitetura atual for suficiente, a decisão correta é preservá-la.

Promover para `02-solution.md` somente os padrões do discovery que condicionam a solução. Os demais
permanecem fora do contexto de planejamento, implementação e Judge.

## Não fazer
- não editar código;
- não criar testes ainda;
- não escrever plano detalhado antes da aprovação da solução.

## Gate
Parar e solicitar `APROVAR SOLUÇÃO`.

Ao apresentar o gate, destacar decisões `DD-*`, trade-offs e incertezas que o usuário está
aprovando. Alternativas descartadas sem consequência material podem permanecer resumidas.

Somente após aprovação marcar:
```text
SOLUTION_APPROVED=true
```
