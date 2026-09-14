---
name: judge-recovery
role: recovery-analysis
preferred_model_role: HEAD_STRONG
context_loading: lazy
reads:
  - STATE.md
  - 00-jira.md
  - 01-discovery.md_if_exists
  - 01-requirements.md_if_exists
  - 02-design.md_if_exists
  - 02-solution.md_if_exists
  - 03-spec.md_if_exists
  - 04-implementation-plan.md_if_exists
  - 05-red-tests.md_if_exists
  - red-tests.lock_if_exists
  - 08-judgement.md_if_recovery_source_judge
  - recovery_trigger_current_only
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
  - approved_contracts_directly
  - acceptance_criteria_without_human_confirmation
---

# Skill — Recovery dirigido

## Objetivo

Tratar um finding material que possa invalidar implementação, requisito, solução, SPEC/plano ou RED
**sem reiniciar a história inteira e sem deixar o executor improvisar o contrato**.

O estado canônico continua `JUDGE_RECOVERY`, mas esta skill pode ser acionada antes ou depois do Judge.
O nome do estado não significa que `JUDGE_STATUS=FAIL` seja obrigatório em recovery pré-Judge.

## Entrada obrigatória

```yaml
CURRENT_STATE: JUDGE_RECOVERY
RECOVERY_STATUS: REQUIRED | IN_PROGRESS
RECOVERY_SOURCE: RED_EXECUTION | IMPLEMENTATION | GREEN_VALIDATION | QUICK_AUTOGO | JUDGE
```

### Quando a origem é `JUDGE`

Também exigir:

```yaml
JUDGE_STATUS: FAIL
JUDGE_FAIL_CLASS: RED_CONTRACT_DEFECT | DISCOVERY_GAP | REQUIREMENT_AMBIGUITY
```

`IMPLEMENTATION_DEFECT` vai direto para `REWORK_IMPLEMENTATION`.

### Quando a origem é pré-Judge

Usar `RECOVERY_CLASS`:

```text
CONTRACT_MISMATCH
RED_CONTRACT_DEFECT
DISCOVERY_GAP
REQUIREMENT_AMBIGUITY
```

O trigger/finding deve ser compacto e verificável; não carregar histórico de tentativas.

## Princípio

Investigar **somente o delta** que gerou o recovery.

Não refazer automaticamente:

- Jira intake;
- Discovery completo;
- análise de requisitos inteira;
- solução inteira;
- SPEC inteira;
- RED inteiro.

Responder:

```text
O finding revela fato novo?
Qual contrato/decisão é afetado?
A solução aprovada continua válida?
A SPEC/plano continuam válidos?
O RED/lock continuam válidos?
Existe decisão humana necessária?
Qual é o menor estado seguro para retomar?
```

## Saída obrigatória

Persistir:

```text
recovery/judge-recovery-<N>.md
```

Formato:

```yaml
RECOVERY_SOURCE:
TRIGGER_OR_FINDING_ID:
RECOVERY_CLASS:
NEW_FACT:
TARGETED_EVIDENCE:
REQUIREMENT_IMPACT: NONE | PATCH_REQUIRED
SOLUTION_IMPACT: NONE | PATCH_REQUIRED
SPEC_PLAN_IMPACT: NONE | PATCH_REQUIRED
RED_IMPACT: VALID | REVIEW_REQUIRED | REOPEN_REQUIRED
HUMAN_DECISION_REQUIRED: true|false
DECISION:
NEXT_STATE:
```

Não copiar transcript nem logs extensos.

## Roteamento mínimo

### Caso A — implementação apenas

Se requisitos, solução, SPEC/plano e RED continuam válidos:

```yaml
DECISION: IMPLEMENTATION_ONLY
RECOVERY_STATUS: RESOLVED
CURRENT_STATE: REWORK_IMPLEMENTATION
NEXT_ACTION: APPLY_RECOVERY_FINDING
NEXT_MODEL_ROLE: EXECUTOR
```

### Caso B — requisito precisa ser esclarecido/corrigido

Se uma decisão humana for necessária, perguntar somente o ponto material e manter:

```yaml
RECOVERY_STATUS: BLOCKED
CURRENT_STATE: JUDGE_RECOVERY
NEXT_ACTION: WAIT_HUMAN_DECISION
```

Depois da decisão, se o requisito mudar materialmente:

```yaml
RECOVERY_STATUS: IN_PROGRESS
REQUIREMENT_ANALYSIS_STATUS: PENDING
SOLUTION_DESIGN_STATUS: PENDING
SOLUTION_APPROVED: false
SPEC_STATUS: STALE
SPEC_PLAN_APPROVED: false
RECOVERY_RED_REOPEN_REQUIRED: <true se RED_LOCKED=true; senão false>
CURRENT_STATE: REQUIREMENT_ANALYSIS
NEXT_ACTION: APPLY_RECOVERY_REQUIREMENT_DELTA
NEXT_MODEL_ROLE: HEAD_STRONG
```

### Caso C — solução precisa mudar, requisitos continuam válidos

```yaml
RECOVERY_STATUS: IN_PROGRESS
SOLUTION_DESIGN_STATUS: PENDING
SOLUTION_APPROVED: false
SPEC_STATUS: STALE
SPEC_PLAN_APPROVED: false
RECOVERY_RED_REOPEN_REQUIRED: <true se RED_LOCKED=true; senão false>
CURRENT_STATE: SOLUTION_DESIGN
NEXT_ACTION: APPLY_RECOVERY_DESIGN_DELTA
NEXT_MODEL_ROLE: HEAD_STRONG
```

### Caso D — somente SPEC/plano precisa mudar

```yaml
RECOVERY_STATUS: IN_PROGRESS
SPEC_STATUS: STALE
SPEC_PLAN_APPROVED: false
RECOVERY_RED_REOPEN_REQUIRED: <true se RED_LOCKED=true; senão false>
CURRENT_STATE: SPEC_PLAN_REVIEW
NEXT_ACTION: APPLY_RECOVERY_SPEC_PLAN_DELTA
NEXT_MODEL_ROLE: HEAD_STRONG
```

A skill responsável aplica o delta documentado e usa seu gate humano normal. Recovery não edita diretamente
solução/SPEC/plano aprovados.

### Caso E — RED precisa mudar e o contrato superior já está válido

Se **não existe lock válido ainda**, retornar ao gate normal:

```yaml
RECOVERY_STATUS: RESOLVED
RED_APPROVED: false
RED_LOCKED: false
CURRENT_STATE: RED_REVIEW
NEXT_ACTION: REDESIGN_RED_FROM_RECOVERY
NEXT_MODEL_ROLE: EXECUTOR
```

Se `RED_LOCKED=true`, não alterar o teste. Marcar:

```yaml
RECOVERY_STATUS: IN_PROGRESS
RECOVERY_RED_REOPEN_REQUIRED: true
CURRENT_STATE: JUDGE_RECOVERY
NEXT_ACTION: REQUEST_REOPEN_RED
```

e apresentar:

```text
RED REOPEN REQUIRED

Motivo:
<novo fato/finding>

O que muda:
- <delta já documentado>

Impacto:
- invalida o red-tests.lock atual
- exige nova execução RED
- exige novo GREEN
- exige novo Judge fresh

Para autorizar, responda exatamente:
REOPEN RED
```

Não aceitar `sim`, `ok`, `aprovado` ou equivalente.

Após `REOPEN RED`:

```yaml
RED_REOPEN_COUNT: +1
RED_APPROVED: true
RED_LOCKED: false
RECOVERY_RED_REOPEN_REQUIRED: false
RECOVERY_STATUS: RESOLVED
CURRENT_STATE: RED_REVIEW
NEXT_ACTION: APPLY_APPROVED_RED_REOPEN_DELTA
NEXT_MODEL_ROLE: EXECUTOR
```

A skill 07 aplica somente o delta aprovado e segue para nova `RED_EXECUTION`.

## Reaprovação antes de reabrir RED

Quando recovery tornou solução/SPEC stale, **reaprovar primeiro os contratos superiores** usando os gates
existentes. `06-spec-plano.md` verifica `RECOVERY_RED_REOPEN_REQUIRED`; depois de `APROVAR SPEC/PLANO`,
retorna a esta skill para solicitar `REOPEN RED` quando necessário.

## Regra de modelo

`JUDGE_RECOVERY` exige `HEAD_STRONG`. Em routing manual, não continuar com Judge/Executor.
Quando o recovery terminar em implementação ou RED, parar para handoff `EXECUTOR` quando necessário.
