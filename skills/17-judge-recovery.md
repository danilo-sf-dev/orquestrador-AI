---
name: judge-recovery
role: recovery-analysis
preferred_model_role: HEAD_STRONG
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md
  - 02-solution.md
  - 03-prd.md
  - 04-implementation-plan.md
  - 05-red-tests.md
  - red-tests.lock
  - 08-judgement.md
  - judge_findings_only
  - source_code_strictly_relevant_to_finding
  - existing_tests_strictly_relevant_to_finding
writes:
  - recovery/judge-recovery-<N>.md
  - STATE.md
forbidden_reads:
  - full_chat_transcript
  - executor_attempt_history
  - unrelated_repository_files
  - unrelated_feature_artifacts
forbidden_writes:
  - production_code
  - test_files
  - red-tests.lock
  - acceptance_criteria_without_human_confirmation
---

# Skill — Judge Recovery

## Objetivo

Tratar `Judge FAIL` quando o problema não é um simples defeito de implementação, sem reiniciar a história inteira e sem deixar o executor improvisar entre Discovery, RED e implementação.

Esta skill é um **micro-fluxo dirigido pelo finding do Judge**.

---

## Entrada obrigatória

```yaml
CURRENT_STATE: JUDGE_RECOVERY
JUDGE_STATUS: FAIL
JUDGE_FAIL_CLASS: DISCOVERY_GAP | RED_CONTRACT_DEFECT | REQUIREMENT_AMBIGUITY
```

`IMPLEMENTATION_DEFECT` não entra nesta skill; vai direto para `REWORK_IMPLEMENTATION`.

---

## Princípio

Investigar **somente o novo fato/questionamento** descoberto pelo Judge.

Não refazer automaticamente:

- Jira intake;
- Discovery completo;
- entrevista inteira;
- solução inteira;
- PRD inteiro;
- RED inteiro.

O objetivo é responder:

```text
O finding revela algo novo?
O que exatamente muda?
A solução aprovada continua válida?
O PRD/plano precisam de patch?
O RED continua válido?
É necessária decisão humana?
```

---

## Classes

### `DISCOVERY_GAP`

Existe comportamento/regra/condição relevante no código ou contrato que não foi descoberta antes.

Executar targeted rediscovery apenas sobre:

- finding do Judge;
- código diretamente ligado ao finding;
- callers/dependências estritamente necessárias;
- testes existentes relacionados;
- contrato afetado.

### `RED_CONTRACT_DEFECT`

O Judge encontrou evidência de que o RED aprovado não representa corretamente o comportamento esperado.

Não editar RED. Determinar exatamente:

- qual cenário está incorreto;
- por quê;
- qual parte do contrato deve mudar;
- impacto em solução/PRD/plano.

### `REQUIREMENT_AMBIGUITY`

O finding expôs uma decisão de produto/regra que não pode ser inferida com segurança.

Fazer **somente a pergunta mínima necessária** ao usuário e permanecer em `JUDGE_RECOVERY` até a resposta.

---

## Saída obrigatória

Persistir um artefato curto:

```text
recovery/judge-recovery-<N>.md
```

Formato:

```yaml
JUDGE_FINDING_ID:
FAIL_CLASS:
NEW_FACT:
TARGETED_EVIDENCE:
SOLUTION_IMPACT: NONE | PATCH_REQUIRED
PRD_PLAN_IMPACT: NONE | PATCH_REQUIRED
RED_IMPACT: VALID | REOPEN_REQUIRED
HUMAN_DECISION_REQUIRED: true|false
DECISION:
NEXT_STATE:
```

Não copiar transcript nem logs extensos.

---

## Decisão de roteamento

### Caso A — implementação apenas

Se após análise o RED e as decisões aprovadas continuam válidos:

```text
DECISION=IMPLEMENTATION_ONLY
NEXT_STATE=REWORK_IMPLEMENTATION
```

Fazer handoff para `EXECUTOR` com somente findings e delta necessário.

### Caso B — RED precisa mudar

Se `RED_IMPACT=REOPEN_REQUIRED`, apresentar ao usuário:

```text
RED REOPEN REQUIRED

Motivo:
<novo fato/finding>

O que muda:
- <delta de solução/PRD se houver>
- <delta do contrato RED>

Impacto:
- invalida o red-tests.lock atual
- exige nova execução RED
- exige novo GREEN
- exige novo Judge fresh

Para autorizar, responda exatamente:
REOPEN RED
```

Não aceitar `sim`, `ok`, `aprovado` ou equivalente como autorização de reabertura.

Após `REOPEN RED`:

```yaml
RED_REOPEN_COUNT: +1
RED_APPROVED: true
RED_LOCKED: false
CURRENT_STATE: RED_REVIEW
NEXT_ACTION: APPLY_APPROVED_RED_REOPEN_DELTA
NEXT_MODEL_ROLE: EXECUTOR
```

A revisão proposta do contrato RED fica registrada no artefato de recovery. Após a autorização, `skills/07-testes-red.md` aplica **somente o delta aprovado** em `05-red-tests.md` e então segue para nova `RED_EXECUTION`.

### Caso C — bloqueado por decisão humana

Se requisito continuar ambíguo:

```text
DECISION=BLOCKED_FOR_HUMAN_DECISION
CURRENT_STATE=JUDGE_RECOVERY
```

Perguntar somente o ponto necessário.

---

## Regra de modelo

`JUDGE_RECOVERY` exige `HEAD_STRONG`.

Em roteamento manual, nunca continuar esse estado com `JUDGE_PRIMARY` nem `EXECUTOR`.

Quando a decisão exigir implementação ou nova execução RED, parar em `MODEL_HANDOFF_REQUIRED` para `EXECUTOR`.
