---
name: scenario-bug-desenvolvimento
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

# Cenário — Bug em desenvolvimento

## Objetivo
Corrigir comportamento ainda não produtivo com teste de regressão explícito.

## Pipeline
1. Intake com comportamento esperado vs atual.
2. Memory-first.
3. Discovery/reprodução.
4. Entrevista somente se o esperado não estiver claro.
5. Solução/root cause proposta [aprovação].
6. PRD/plano compacto [aprovação].
7. Criar teste de regressão RED [aprovação + lock].
8. GO.
9. Corrigir com EXECUTOR.
10. GREEN sem alterar RED.
11. Judge fresh-context.
12. QA pack [aprovação].
13. Archive com causa raiz e prevenção.

## Memória importante
Arquivar a causa raiz e o padrão de falha para que bugs semelhantes sejam encontrados por busca futura.


## Regra de testes unitários
Os testes RED devem incluir happy path e **edge cases aplicáveis** à história/bug. Edge cases relevantes não cobertos precisam de justificativa explícita; não criar cenários artificiais sem vínculo com critérios, regras, contratos ou riscos.
