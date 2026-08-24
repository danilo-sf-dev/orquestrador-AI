---
name: prd-plano
role: planning
preferred_model_role: HEAD_STRONG
writes: [03-prd.md, 04-implementation-plan.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 02-solution.md
  - approved_human_decisions
forbidden_reads:
  - chat_transcript
  - raw_discovery_logs
  - unrelated_feature_artifacts
forbidden_writes:
  - source_code
  - tests
---

# Skill — PRD + plano de implementação

## Pré-condição
`SOLUTION_APPROVED=true`.

## Mini-PRD
Deve conter:
- objetivo;
- escopo;
- fora de escopo;
- comportamento atual/desejado;
- critérios de aceite normalizados;
- API/contratos;
- erros/status esperados;
- integrações;
- riscos;
- observabilidade relevante;
- matriz de rastreabilidade AC -> comportamento -> evidência.

## Plano
Deve conter:
- sequência de implementação;
- repos impactados;
- arquivos/componentes esperados;
- contratos;
- migrações/configs, se houver;
- estratégia de backward compatibility;
- testes unitários necessários, incluindo happy path e edge cases aplicáveis;
- matriz inicial de edge cases/riscos a transformar em testes (ex.: boundaries, ausência/null, vazio, inválidos, erros de dependência, estados/branches, duplicidade/idempotência), marcando somente os que fazem sentido para a história;
- testes integrados/QA necessários;
- ordem de deploy quando cross-repo;
- rollback/mitigação quando relevante.

## Regra
Plano descreve intenção; não deve fingir que caminhos/classes inexistentes foram confirmados. Diferenciar `CONFIRMED` de `EXPECTED`.

## Gate
Parar e solicitar `APROVAR PRD/PLANO`.


## Relação com memória anterior

Quando a história altera comportamento já documentado em outra feature, registrar a relação como `EXTENDS`, `OVERRIDES`, `DEPRECATES` ou `RELATED`. Isso serve para busca futura e delta analysis; não duplicar documentos antigos.
