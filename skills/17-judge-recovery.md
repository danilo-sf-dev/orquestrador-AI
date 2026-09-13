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
  - 03-spec.md
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
Tratar Judge FAIL não trivial sem reiniciar a história inteira e sem deixar executor improvisar entre Discovery, RED e implementação.

## Entrada

```yaml
CURRENT_STATE: JUDGE_RECOVERY
JUDGE_STATUS: FAIL
JUDGE_FAIL_CLASS: DISCOVERY_GAP | RED_CONTRACT_DEFECT | REQUIREMENT_AMBIGUITY
```

`IMPLEMENTATION_DEFECT` vai direto para `REWORK_IMPLEMENTATION`.

## Princípio
Investigar somente o novo fato/questionamento. Não refazer Jira intake, Discovery completo, entrevista inteira,
solução inteira, SPEC inteira ou RED inteiro.

Responder:

```text
O finding revela algo novo?
O que muda?
A solução continua válida?
A SPEC/plano precisam de patch?
O RED continua válido?
É necessária decisão humana?
```

## Saída
Persistir `recovery/judge-recovery-<N>.md`:

```yaml
JUDGE_FINDING_ID:
FAIL_CLASS:
NEW_FACT:
TARGETED_EVIDENCE:
SOLUTION_IMPACT: NONE | PATCH_REQUIRED
SPEC_PLAN_IMPACT: NONE | PATCH_REQUIRED
RED_IMPACT: VALID | REOPEN_REQUIRED
HUMAN_DECISION_REQUIRED: true|false
DECISION:
NEXT_STATE:
```

## Roteamento
Se implementação apenas: `REWORK_IMPLEMENTATION`.
Se RED precisa mudar, apresentar motivo, delta de solução/SPEC e contrato RED, impacto e exigir resposta exata `REOPEN RED`.
Após autorização: invalidar lock, aplicar somente delta aprovado, executar novo RED, GREEN e Judge fresh.
Se requisito continuar ambíguo: permanecer bloqueado em `JUDGE_RECOVERY` perguntando somente o ponto necessário.

## Regra de modelo
`JUDGE_RECOVERY` exige `HEAD_STRONG`; execução/reabertura posterior exige handoff para `EXECUTOR`.
