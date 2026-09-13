---
name: spec-plano
role: planning
preferred_model_role: HEAD_STRONG
writes: [03-spec.md, 04-implementation-plan.md, STATE.md]
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 01-requirements.md
  - 02-design.md
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

# Skill — SPEC canônica + plano de implementação

## Pré-condições

```yaml
SOLUTION_APPROVED: true
REQUIREMENT_ANALYSIS_STATUS: COMPLETE
BLOCKING_OPEN_QUESTIONS: 0
```

## Princípio da SPEC
A SPEC descreve comportamento observável e decisões aprovadas. Ela não é resumo narrativo do chat nem
documento genérico de produto.

```text
Jira + evidence + human decisions
            ↓
          SPEC
      /     |      \
    RED   PLAN    JUDGE
```

Nenhuma fase posterior pode redefinir silenciosamente requisito, assumption material ou decisão de design.

## Estrutura obrigatória de `03-spec.md`

```text
SPEC_ID: <JIRA>
OBJECTIVE:
SCOPE:
OUT_OF_SCOPE:
OBSERVABLE_BEHAVIOR:

AC-01:
SOURCE: <Jira/R-/human decision>
GIVEN:
WHEN:
THEN:
ERRORS_OR_EDGE_BEHAVIOR:

CONSTRAINTS:
ASSUMPTIONS_ACCEPTED:
OPEN_QUESTIONS: []
CONTRACTS:
NON_FUNCTIONAL_REQUIREMENTS:
DESIGN_DECISIONS: [DD-...]
RISKS_AND_VALIDATION:
RELATED_FEATURES:
```

Cada AC precisa de origem. Não criar AC para `OPTIONAL_IMPROVEMENT` não aprovado.

## Normalização de critérios
Transformar `R-*` em critérios testáveis/observáveis sem alterar significado. Quando um requisito não for
demonstrável por teste unitário, declarar evidência esperada (`integration`, `config`, `static verification`, `QA`, `external validation`).

Antes de concluir, verificar somente lacunas aplicáveis: origem/formato de dados, cálculos, duplicidade/idempotência,
timeout/retry/fallback, persistência/migração e compatibilidade de contratos.

Se aparecer `OPEN_QUESTION` material, voltar para `REQUIREMENT_ANALYSIS`; não decidir aqui.

## Plano
Deve conter sequência de implementação, repos, arquivos/componentes, contratos, migrações/configs,
compatibilidade, testes unitários, edge cases, QA, ordem de deploy e rollback/mitigação quando relevante.

```text
PLAN_ID: PLAN-<N>
OUTCOME:
DEPENDS_ON: []
AC_LINKS: []
REQUIREMENT_LINKS: []
DESIGN_DECISIONS: []
FILES_CONFIRMED: []
FILES_EXPECTED: []
TESTS_REQUIRED: []
VERIFICATION:
RISK: LOW | MEDIUM | HIGH
```

## Rastreabilidade bidirecional

```text
R-* -> AC-* -> DD-* -> PLAN-* -> arquivo/componente -> teste/evidência
```

Todo requisito/AC/decisão material precisa de unidade de plano/verificação; todo item do plano precisa ter origem justificável.

## SPEC freeze
Ao aprovar, `03-spec.md` vira contrato para RED. Mudança material posterior exige delta explícito e
roteamento à fase responsável; executor não altera SPEC para acomodar implementação.

## Gate
Parar e solicitar exatamente:

```text
APROVAR SPEC/PLANO
```

Após aprovação:

```yaml
SPEC_PLAN_APPROVED: true
SPEC_STATUS: APPROVED
CURRENT_STATE: RED_REVIEW
NEXT_ACTION: DESIGN_RED
```

## Relação com memória anterior
Quando a história altera comportamento anterior, registrar `EXTENDS`, `OVERRIDES`, `DEPRECATES` ou `RELATED`.
O comportamento atual é definido pela SPEC mais nova aprovada.
