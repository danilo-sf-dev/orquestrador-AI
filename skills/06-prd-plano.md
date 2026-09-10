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

Antes de concluir, verificar somente lacunas aplicáveis ao tipo de mudança:

- origem e formato dos dados;
- exemplo concreto para cálculo ou transformação;
- duplicidade/idempotência e ordem para eventos;
- timeout, retry, fallback e erro de dependência externa;
- dados existentes e migração para mudanças persistentes;
- compatibilidade para contratos consumidos por outros repos.

Não perguntar sobre convenções já comprovadas no projeto. Lacuna que não muda implementação ou
aceite deve ser registrada como risco, não usada para prolongar a entrevista.

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

Organizar o trabalho em unidades implementáveis. Cada unidade deve declarar:

```text
PLAN_ID: PLAN-<N>
OUTCOME: <resultado observável, não atividade genérica>
DEPENDS_ON: []
AC_LINKS: []
DESIGN_DECISIONS: []
FILES_CONFIRMED: []
FILES_EXPECTED: []
TESTS_REQUIRED: []
VERIFICATION:
RISK: LOW | MEDIUM | HIGH
```

As dependências devem formar uma ordem executável, sem ciclos. Não criar unidade "investigar" sem
uma decisão ou artefato verificável como saída. Arquivos descobertos no código entram como
`FILES_CONFIRMED`; caminhos ainda não existentes ou inferidos ficam em `FILES_EXPECTED`.

## Rastreabilidade e impacto

Construir uma matriz compacta:

```text
AC/JIRA -> DD -> PLAN_ID -> arquivo/componente -> teste/evidência
```

Validar nos dois sentidos:

- todo critério e decisão relevante possui unidade de plano e verificação;
- toda unidade, arquivo esperado e teste planejado tem justificativa em critério, risco ou decisão;
- alteração de contrato inclui consumidores, compatibilidade e ordem cross-repo;
- risco material inclui mitigação, rollback ou validação correspondente.

Itens sem origem justificável devem sair do plano ou ser apresentados explicitamente como melhoria
opcional fora de escopo.

## Regra
Plano descreve intenção; não deve fingir que caminhos/classes inexistentes foram confirmados. Diferenciar `CONFIRMED` de `EXPECTED`.

O plano não redefine a solução. Se a decomposição revelar uma decisão arquitetural nova ou invalidar
uma `DD-*` aprovada, voltar para `SOLUTION_REVIEW` com o delta, em vez de decidir silenciosamente.

## Gate
Parar e solicitar `APROVAR PRD/PLANO`.


## Relação com memória anterior

Quando a história altera comportamento já documentado em outra feature, registrar a relação como `EXTENDS`, `OVERRIDES`, `DEPRECATES` ou `RELATED`. Isso serve para busca futura e delta analysis; não duplicar documentos antigos.
