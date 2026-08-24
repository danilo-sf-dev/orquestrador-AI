---
name: scenario-historia-padrao
load_mode: on_demand
context_loading: lazy
reads:
  - STATE.md
  - scenario_signal_only
forbidden_reads:
  - chat_transcript
  - unrelated_feature_artifacts
writes:
  - STATE.md
---

# Cenário — História padrão

## Quando usar
Nova história Jira com critérios de aceite e, frequentemente, endpoint/arquitetura indicada.

## Pipeline
```text
bootstrap -> intake -> memory -> discovery
-> interview only if needed
-> solution [approve]
-> PRD/plan [approve]
-> RED [approve+lock]
-> GO -> implementation -> GREEN
-> Judge -> QA [approve] -> commit [confirm] -> archive
```

## Otimização
Se endpoint já estiver no Jira, discovery começa por ele. Não indexar workspace inteiro sem necessidade.

## Modelo por fase
- discovery: ECONOMICAL
- solution/PRD/judge: HEAD_STRONG/JUDGE
- implementation/RED/GREEN/QA: EXECUTOR
- imagens: MULTIMODAL


## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras, contratos ou riscos.
