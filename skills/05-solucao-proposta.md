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
  - recovery/judge-recovery-<N>.md_if_recovery_in_progress
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

Revisar e consolidar o design técnico em uma solução mínima, coerente com o Jira, com o contrato de
requisitos e com a arquitetura atual, apresentando ao usuário somente decisões materiais para o gate
`APROVAR SOLUÇÃO`.

A análise técnica detalhada ocorre em `04b-design-solucao.md`; esta skill não deve refazer o design do
zero nem ampliar escopo por preferência arquitetural.

## Pré-condições

```yaml
REQUIREMENT_ANALYSIS_STATUS: COMPLETE
SOLUTION_DESIGN_STATUS: COMPLETE
BLOCKING_OPEN_QUESTIONS: 0
```

Se qualquer condição falhar, não pedir aprovação de solução.

## Inputs
- `00-jira.md`;
- `01-discovery.md`;
- `01-requirements.md`;
- `02-design.md`;
- memórias relevantes revalidadas;
- respostas humanas já aprovadas;
- `01-quality-review.md`, somente quando a revisão opcional tiver sido ativada;
- recovery atual, somente quando `RECOVERY_STATUS=IN_PROGRESS`.

## Modo recovery

Quando a solução foi invalidada por recovery, consolidar **somente o delta material** documentado no
recovery sobre a solução existente. Não reabrir decisões que continuem válidas.

O gate `APROVAR SOLUÇÃO` continua obrigatório porque a solução anterior ficou stale.

## Entrada opcional de qualidade arquitetural

Uma recomendação `TQ-*` não é uma decisão aprovada nem obrigação de implementação. Ela só pode entrar
na solução se resolver requisito atual ou risco técnico material reconhecido no design.

Não introduzir pattern, camada ou arquitetura apenas porque a revisão os listou. `NO_CHANGE` e
`LOCAL_REFACTOR` são resultados válidos. Se uma recomendação for selecionada, registrar seu `TQ-*`
como evidência no `DD-*`; se for rejeitada, resumir o motivo quando isso evitar reabertura da decisão.

## Validar antes do gate

1. todo requisito `R-*` relevante está atendido pela abordagem proposta ou explicitamente fora do escopo;
2. nenhuma `OPEN_QUESTION BLOCKING=YES` permanece;
3. assumptions com impacto alto estão visíveis e possuem evidência/mitigação;
4. `OPTIONAL_IMPROVEMENT` não entrou silenciosamente no escopo;
5. boundaries, contratos e consumidores materiais estão explícitos;
6. a solução não contradiz fatos do discovery nem decisões humanas aprovadas;
7. alternativa significativamente melhor encontrada pelo Senior Approach Check foi tratada;
8. a mudança proposta é a menor capaz de satisfazer o contrato.

## Produzir `02-solution.md`

1. entendimento do problema/feature;
2. comportamento atual e desejado;
3. requisitos `R-*` cobertos;
4. solução recomendada;
5. impacto por repo;
6. contratos alterados ou preservados;
7. boundaries afetados;
8. riscos/regressões e mitigação;
9. assumptions materiais aceitas;
10. alternativas materiais descartadas;
11. itens fora de escopo e melhorias opcionais não selecionadas.

## Decisão arquitetural proporcional

Promover decisões materiais do design para ADR-lite:

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

Não criar `DD-*` para detalhe sintático ou escolha trivial. Quando a arquitetura atual for suficiente,
a decisão correta é preservá-la.

## Não fazer
- não editar código;
- não criar testes ainda;
- não escrever plano detalhado antes da aprovação da solução;
- não inventar requisito para "melhorar" o sistema;
- não reabrir discovery sem evidência de fato novo.

## Gate
Parar e solicitar `APROVAR SOLUÇÃO`.

Ao apresentar o gate, mostrar de forma compacta:

```text
REQUIREMENTS_COVERED: <N>/<N>
BLOCKING_OPEN_QUESTIONS: 0
DESIGN: <resumo>
MATERIAL_DECISIONS: <DD-* ou NONE>
RISKS_ACCEPTED: <resumo>
OUT_OF_SCOPE: <resumo>
```

Somente após aprovação marcar:

```yaml
SOLUTION_APPROVED: true
CURRENT_STATE: SPEC_PLAN_REVIEW
NEXT_MODEL_ROLE: HEAD_STRONG
```

Se `RECOVERY_STATUS=IN_PROGRESS` e `SPEC_STATUS=STALE`:

```yaml
NEXT_ACTION: APPLY_RECOVERY_SPEC_PLAN_DELTA
```

Caso contrário:

```yaml
NEXT_ACTION: BUILD_SPEC_AND_PLAN
```
