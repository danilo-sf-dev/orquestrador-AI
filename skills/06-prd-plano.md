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

> O nome físico `03-prd.md` é mantido por compatibilidade. Semanticamente, o arquivo passa a ser a
> **SPEC canônica** da feature: o contrato vivo que RED, implementação, GREEN e Judge devem seguir.

## Pré-condições

```yaml
SOLUTION_APPROVED: true
REQUIREMENT_ANALYSIS_STATUS: COMPLETE
BLOCKING_OPEN_QUESTIONS: 0
```

## Princípio da SPEC

A SPEC descreve comportamento observável e decisões aprovadas. Ela não é um resumo narrativo do chat
nem um documento de produto genérico.

```text
Jira + evidence + human decisions
            ↓
          SPEC
      /     |      \
    RED   PLAN    JUDGE
```

Nenhuma fase posterior pode redefinir silenciosamente requisito, assumption material ou decisão de
design. Delta material volta à fase responsável.

## Estrutura obrigatória de `03-prd.md`

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

Transformar requisitos `R-*` em critérios testáveis/observáveis sem alterar significado. Quando um
requisito não for demonstrável por teste unitário, declarar a evidência esperada (`integration`,
`config`, `static verification`, `QA`, `external validation`).

Antes de concluir, verificar somente lacunas aplicáveis ao tipo de mudança:

- origem e formato dos dados;
- exemplo concreto para cálculo ou transformação;
- duplicidade/idempotência e ordem para eventos;
- timeout, retry, fallback e erro de dependência externa;
- dados existentes e migração para mudanças persistentes;
- compatibilidade para contratos consumidos por outros repos.

Se aparecer nova `OPEN_QUESTION` material, **não decidir aqui**: voltar para `REQUIREMENT_ANALYSIS` com
o delta. Lacuna que não muda implementação ou aceite deve ser risco/limitação, não pergunta infinita.

## Plano
Deve conter:
- sequência de implementação;
- repos impactados;
- arquivos/componentes esperados;
- contratos;
- migrações/configs, se houver;
- estratégia de backward compatibility;
- testes unitários necessários, incluindo happy path e edge cases aplicáveis;
- matriz inicial de edge cases/riscos a transformar em testes;
- testes integrados/QA necessários;
- ordem de deploy quando cross-repo;
- rollback/mitigação quando relevante.

Organizar o trabalho em unidades implementáveis:

```text
PLAN_ID: PLAN-<N>
OUTCOME: <resultado observável, não atividade genérica>
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

As dependências devem formar ordem executável, sem ciclos. Não criar unidade "investigar" sem decisão
ou artefato verificável como saída. Arquivos descobertos entram como `FILES_CONFIRMED`; caminhos ainda
não existentes/inferidos ficam em `FILES_EXPECTED`.

## Rastreabilidade bidirecional

Construir matriz compacta:

```text
R-* -> AC-* -> DD-* -> PLAN-* -> arquivo/componente -> teste/evidência
```

Validar nos dois sentidos:

- todo requisito/AC/decisão material possui unidade de plano e verificação;
- toda unidade, arquivo esperado e teste planejado tem origem em requisito, AC, risco ou decisão;
- alteração de contrato inclui consumidores, compatibilidade e ordem cross-repo;
- risco material inclui mitigação, rollback ou validação;
- item sem origem justificável sai do plano ou fica como melhoria opcional fora de escopo.

## SPEC freeze

Ao aprovar, a versão de `03-prd.md` vira contrato para RED. Mudança material posterior exige delta
explícito e roteamento à fase responsável; executor não pode alterar SPEC para acomodar implementação.

## Gate
Parar e solicitar `APROVAR PRD/PLANO`.

> O texto do gate é preservado por compatibilidade de UX; o que está sendo aprovado é a **SPEC canônica
> + plano**.

Após aprovação:

```yaml
PRD_PLAN_APPROVED: true
SPEC_STATUS: APPROVED
CURRENT_STATE: RED_REVIEW
NEXT_ACTION: DESIGN_RED
```

## Relação com memória anterior

Quando a história altera comportamento já documentado em outra feature, registrar `EXTENDS`,
`OVERRIDES`, `DEPRECATES` ou `RELATED`. A relação serve para busca/delta analysis; comportamento atual é
definido pela SPEC mais nova aprovada, sem duplicar documentos antigos.
